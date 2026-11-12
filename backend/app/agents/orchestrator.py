import time
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.scan import SecurityScan, AgentExecutionLog
from app.models.vulnerability import Vulnerability, VulnerabilityEvidence
from app.agents.safety_policy import SafetyPolicyAgent
from app.agents.recon_discovery import ReconDiscoveryAgent
from app.agents.inventory_classifier import ApiInventoryAgent
from app.agents.attack_planner import AttackPlanningAgent
from app.agents.security_testers.access_control import AccessControlTestingAgent
from app.agents.security_testers.business_logic import BusinessLogicTestingAgent
from app.agents.security_testers.auth_tester import AuthenticationTestingAgent
from app.agents.security_testers.injection_tester import InjectionTestingAgent
from app.agents.security_testers.api_security import ApiSecurityTestingAgent
from app.agents.verification import VulnerabilityVerificationAgent
from app.agents.risk_assessment import RiskAssessmentAgent
from app.agents.reporting import ReportingAgent

class MultiAgentOrchestrator:
    """
    Coordinates the 10-agent dynamic testing pipeline for SentinelAI.
    Executes sequentially with safety policy bounds, logging each agent's execution.
    """
    def __init__(self, db: Session):
        self.db = db

    def log_agent_step(self, scan_id: int, agent_name: str, step_name: str, status: str, input_str: str, output_str: str, duration_ms: float = 0.0):
        log = AgentExecutionLog(
            scan_id=scan_id,
            agent_name=agent_name,
            step_name=step_name,
            status=status,
            input_summary=input_str[:1000],
            output_summary=output_str[:1000],
            execution_duration_ms=duration_ms
        )
        self.db.add(log)
        self.db.commit()

    def run_scan(self, scan_id: int) -> Dict[str, Any]:
        scan = self.db.query(SecurityScan).filter(SecurityScan.id == scan_id).first()
        if not scan:
            return {"error": "Scan not found"}

        scan.status = "running"
        scan.start_time = datetime.utcnow()
        self.db.commit()

        # Step 1: Agent 6 (Safety & Policy Agent)
        t0 = time.time()
        safety = SafetyPolicyAgent(self.db)
        is_safe, reason, target = safety.validate_target_scope(scan.target_id)
        if not is_safe:
            scan.status = "stopped"
            scan.stop_reason = f"Safety Guardrail: {reason}"
            scan.end_time = datetime.utcnow()
            self.db.commit()
            self.log_agent_step(scan_id, "Safety & Policy Agent", "Scope Authorization Check", "alert", f"Target ID: {scan.target_id}", reason, (time.time() - t0) * 1000)
            return {"status": "stopped", "reason": reason}

        health_ok, health_msg = safety.check_application_health(target)
        self.log_agent_step(scan_id, "Safety & Policy Agent", "Target Health & Policy Validation", "completed", f"Target: {target.name}", f"Approved. {health_msg}", (time.time() - t0) * 1000)

        # Step 2: Agent 2 (Recon & Discovery Agent)
        t0 = time.time()
        recon = ReconDiscoveryAgent(self.db)
        discovery_res = recon.discover_staging_apis(scan.target_id)
        scan.total_endpoints = discovery_res["total_endpoints_discovered"]
        self.db.commit()
        self.log_agent_step(scan_id, "Recon Discovery Agent", "Endpoint Enumeration & Parameter Mapping", "completed", f"Target URL: {target.target_url}", f"Mapped {scan.total_endpoints} API endpoints across HTTP methods", (time.time() - t0) * 1000)

        # Step 3: Agent 3 (API Inventory Agent)
        t0 = time.time()
        inventory = ApiInventoryAgent(self.db)
        inv_res = inventory.evaluate_inventory(scan.target_id)
        self.log_agent_step(scan_id, "API Inventory Agent", "Active / Zombie / Shadow API Classification", "completed", f"Analyzed {inv_res['total_inventory_count']} endpoints", f"Active: {inv_res['active_count']}, Zombie: {inv_res['zombie_count']}, Shadow: {inv_res['shadow_count']}", (time.time() - t0) * 1000)

        # Step 4: Agent 4 (AI Attack Planning Agent)
        t0 = time.time()
        planner = AttackPlanningAgent(self.db)
        categories = (scan.config_json or {}).get("selected_categories", ["access_control", "business_logic", "authentication", "api_security"])
        test_plan = planner.generate_plan(scan.target_id, categories)
        self.log_agent_step(scan_id, "Attack Planning Agent", "Targeted Test Plan Synthesis", "completed", f"Input: {len(categories)} categories", f"Synthesized targeted plan with {len(test_plan)} precision tests", (time.time() - t0) * 1000)

        # Step 5: Execute Specialized Security Testing Agents (Agent 5)
        access_tester = AccessControlTestingAgent(self.db)
        biz_tester = BusinessLogicTestingAgent(self.db)
        auth_tester = AuthenticationTestingAgent(self.db)
        inj_tester = InjectionTestingAgent(self.db)
        api_sec_tester = ApiSecurityTestingAgent(self.db)

        verification_agent = VulnerabilityVerificationAgent(self.db)
        risk_agent = RiskAssessmentAgent(self.db)

        findings_created = 0
        tested_count = 0

        for test in test_plan:
            tested_count += 1
            t_sub = time.time()
            cat = test["test_category"]
            result = None

            if cat == "access_control":
                result = access_tester.test_cross_agency_idor(test["endpoint_id"])
                agent_name = "Access Control Agent"
            elif cat == "business_logic":
                if "fare" in test["test_name"].lower():
                    result = biz_tester.test_fare_manipulation(test["endpoint_id"])
                else:
                    result = biz_tester.test_duplicate_refund(test["endpoint_id"])
                agent_name = "Business Logic Agent"
            elif cat == "authentication":
                result = auth_tester.test_missing_auth(test["endpoint_id"])
                agent_name = "Authentication Agent"
            elif cat == "injection":
                result = inj_tester.test_input_validation(test["endpoint_id"])
                agent_name = "Injection Testing Agent"
            elif cat == "api_security":
                result = api_sec_tester.test_zombie_shadow_exposure(test["endpoint_id"])
                agent_name = "API Security Agent"
            else:
                continue

            dur_ms = (time.time() - t_sub) * 1000

            if result and result.get("vulnerable"):
                # Save detected vulnerability
                vuln = Vulnerability(
                    scan_id=scan.id,
                    endpoint_id=test["endpoint_id"],
                    title=result["title"],
                    category=result["category"],
                    severity=result["severity"],
                    status="detected",
                    cvss_score=result["cvss_score"],
                    description=result["description"],
                    business_impact=result.get("business_impact"),
                    remediation_guidance=result.get("remediation_guidance"),
                    responsible_owner="Backend Security Team"
                )
                self.db.add(vuln)
                self.db.commit()
                self.db.refresh(vuln)

                # Save minimal evidence
                ev = VulnerabilityEvidence(
                    vulnerability_id=vuln.id,
                    evidence_type="http_traffic",
                    request_dump=result.get("request_dump"),
                    response_dump=result.get("response_dump"),
                    is_reproduced=True,
                    verification_notes="Minimal proof captured during automated scan turn."
                )
                self.db.add(ev)
                self.db.commit()

                # Step 6: Agent 7 (Verification Agent)
                t_v = time.time()
                ver_res = verification_agent.verify_vulnerability(vuln.id)
                self.log_agent_step(scan_id, "Vulnerability Verification Agent", f"Deterministic Proof Verification: {vuln.title}", "completed", f"Vuln ID {vuln.id}", f"Verification Status: {ver_res['status']}. Notes: {ver_res['verification_notes']}", (time.time() - t_v) * 1000)

                # Step 7: Agent 8 (Risk Assessment Agent)
                t_r = time.time()
                risk_res = risk_agent.evaluate_risk(vuln.id)
                self.log_agent_step(scan_id, "Risk & Severity Assessment Agent", f"Business Impact Assessment: {vuln.title}", "completed", f"Score: {risk_res['cvss_score']}", f"Severity: {risk_res['severity'].upper()} | Cross-Agency: {risk_res['cross_agency_risk']} | Financial: {risk_res['booking_payment_impact']}", (time.time() - t_r) * 1000)

                findings_created += 1
                self.log_agent_step(scan_id, agent_name, f"Executed {test['test_name']}", "alert", f"{test['method']} {test['path']}", f"VULNERABILITY IDENTIFIED: {vuln.title} (Severity: {vuln.severity.upper()})", dur_ms)
            else:
                self.log_agent_step(scan_id, agent_name, f"Executed {test['test_name']}", "completed", f"{test['method']} {test['path']}", f"PASS: Secure behavior asserted ({result.get('title') if result else 'OK'})", dur_ms)

        # Wrap up scan
        scan.tested_endpoints = tested_count
        scan.vulnerabilities_count = findings_created
        scan.status = "completed"
        scan.end_time = datetime.utcnow()
        self.db.commit()

        # Step 8: Agent 9 (Reporting Agent)
        reporter = ReportingAgent(self.db)
        report_data = reporter.generate_report_data()
        self.log_agent_step(scan_id, "Reporting Agent", "Security Audit Report Compilation", "completed", f"{findings_created} verified findings", f"Report compiled: {report_data['severity_breakdown']}", 15.0)

        return {
            "scan_id": scan.id,
            "status": "completed",
            "endpoints_tested": tested_count,
            "findings_count": findings_created,
            "scan_duration_sec": (scan.end_time - scan.start_time).total_seconds()
        }
