from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.vulnerability import Vulnerability, RiskAssessment

class RiskAssessmentAgent:
    """
    AGENT 8: Risk & Severity Assessment Agent
    Calculates vulnerability severity based on technical impact, exploitability,
    booking/payment impact, and cross-agency risk.
    Outputs transparent reasoning behind each classification.
    """
    def __init__(self, db: Session):
        self.db = db

    def evaluate_risk(self, vuln_id: int) -> Dict[str, Any]:
        vuln = self.db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
        if not vuln:
            return {"error": "Vulnerability not found"}

        # Calculate impact metrics
        cross_agency_risk = False
        booking_payment_impact = False
        technical_impact = "Medium"
        exploitability = "Moderate"
        financial_impact = "Moderate"
        rationale_points = []

        if vuln.category == "access_control":
            cross_agency_risk = True
            technical_impact = "High"
            exploitability = "Easy"
            financial_impact = "Severe"
            vuln.severity = "critical"
            vuln.cvss_score = 9.1
            rationale_points.append("Allows cross-tenant data exfiltration across separate travel agencies.")
            rationale_points.append("Trivial exploitability via predictable reference identifiers (BOLA/IDOR).")

        elif vuln.category == "business_logic":
            booking_payment_impact = True
            technical_impact = "High"
            exploitability = "Easy"
            financial_impact = "Severe"
            if "fare" in vuln.title.lower():
                vuln.severity = "critical"
                vuln.cvss_score = 9.3
                rationale_points.append("Direct pricing and revenue manipulation in production booking pipeline.")
            else:
                vuln.severity = "high"
                vuln.cvss_score = 8.5
                rationale_points.append("Duplicate refund issuance causing balance leakage.")

        elif vuln.category == "authentication":
            technical_impact = "High"
            exploitability = "Easy"
            financial_impact = "Severe"
            vuln.severity = "critical"
            vuln.cvss_score = 9.8
            rationale_points.append("Unauthenticated external exposure of customer travel records.")

        elif vuln.category == "api_security":
            technical_impact = "Medium"
            exploitability = "Moderate"
            financial_impact = "Moderate"
            vuln.severity = "high" if "zombie" in vuln.title.lower() else "medium"
            vuln.cvss_score = 7.5
            rationale_points.append("Unmonitored legacy API path bypassing ingress governance.")

        rationale = " | ".join(rationale_points)

        # Update or create RiskAssessment
        assessment = self.db.query(RiskAssessment).filter(RiskAssessment.vulnerability_id == vuln_id).first()
        if not assessment:
            assessment = RiskAssessment(
                vulnerability_id=vuln_id,
                technical_impact=technical_impact,
                exploitability=exploitability,
                financial_impact=financial_impact,
                cross_agency_risk=cross_agency_risk,
                booking_payment_impact=booking_payment_impact,
                composite_score=vuln.cvss_score,
                severity_rationale=rationale
            )
            self.db.add(assessment)
        else:
            assessment.technical_impact = technical_impact
            assessment.exploitability = exploitability
            assessment.financial_impact = financial_impact
            assessment.cross_agency_risk = cross_agency_risk
            assessment.booking_payment_impact = booking_payment_impact
            assessment.composite_score = vuln.cvss_score
            assessment.severity_rationale = rationale

        self.db.commit()

        return {
            "vulnerability_id": vuln_id,
            "severity": vuln.severity,
            "cvss_score": vuln.cvss_score,
            "cross_agency_risk": cross_agency_risk,
            "booking_payment_impact": booking_payment_impact,
            "rationale": rationale
        }

