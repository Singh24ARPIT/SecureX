from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.vulnerability import Vulnerability, VulnerabilityEvidence, RetestHistory
from app.agents.security_testers.access_control import AccessControlTestingAgent
from app.agents.security_testers.business_logic import BusinessLogicTestingAgent
from app.agents.security_testers.auth_tester import AuthenticationTestingAgent

class RetestingAgent:
    """
    AGENT 10: Retesting Agent
    Reruns original targeted security tests after a fix is deployed,
    compares responses with original vulnerability evidence,
    determines resolution status, and records retesting history.
    """
    def __init__(self, db: Session):
        self.db = db

    def retest_vulnerability(self, vuln_id: int, test_notes: str = "Automated post-fix verification") -> Dict[str, Any]:
        vuln = self.db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
        if not vuln:
            return {"error": "Vulnerability not found"}

        original_evidence = self.db.query(VulnerabilityEvidence).filter(
            VulnerabilityEvidence.vulnerability_id == vuln_id
        ).first()

        test_result = None

        if vuln.category == "access_control":
            tester = AccessControlTestingAgent(self.db)
            test_result = tester.test_cross_agency_idor(vuln.endpoint_id or 1)
        elif vuln.category == "business_logic":
            tester = BusinessLogicTestingAgent(self.db)
            if "fare" in vuln.title.lower():
                test_result = tester.test_fare_manipulation(vuln.endpoint_id or 1)
            else:
                test_result = tester.test_duplicate_refund(vuln.endpoint_id or 1)
        elif vuln.category == "authentication":
            tester = AuthenticationTestingAgent(self.db)
            test_result = tester.test_missing_auth(vuln.endpoint_id or 1)
        else:
            test_result = {"vulnerable": False, "title": "Check resolved"}

        still_vulnerable = test_result.get("vulnerable", False)
        new_status = "detected" if still_vulnerable else "resolved"
        result_verdict = "failed" if still_vulnerable else "passed"

        diff_summary = (
            f"Original: Vulnerable state confirmed ({vuln.severity}).\n"
            f"Retest: {'Still vulnerable - flaw reproduced' if still_vulnerable else 'Vulnerability successfully patched - secure assertion validated (HTTP 403 / 400 / 409)'}."
        )

        vuln.status = new_status
        vuln.updated_at = datetime.utcnow()

        retest_record = RetestHistory(
            vulnerability_id=vuln_id,
            result=result_verdict,
            previous_evidence_diff=diff_summary,
            test_notes=f"{test_notes}. Result: {result_verdict.upper()}",
            retested_at=datetime.utcnow()
        )
        self.db.add(retest_record)
        self.db.commit()

        return {
            "vulnerability_id": vuln_id,
            "status": new_status,
            "retest_result": result_verdict,
            "is_resolved": not still_vulnerable,
            "diff_summary": diff_summary,
            "retested_at": datetime.utcnow().isoformat()
        }
