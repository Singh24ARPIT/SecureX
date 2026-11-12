import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_dast_pipeline():
    print("\n=======================================================")
    print("SENTINELAI / SECUREX END-TO-END DAST PIPELINE TEST")
    print("=======================================================")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, res.text
    print("✓ Health Check Passed:", res.json())

    # 2. Authentication
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "SentinelAdmin2026!"
    })
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Admin Authentication Succeeded. JWT received.")

    # 3. Check Target Allowlist
    res = client.get("/api/v1/targets", headers=headers)
    assert res.status_code == 200
    targets = res.json()
    assert len(targets) > 0
    target_id = targets[0]["id"]
    print(f"✓ Target verified in Allowlist: '{targets[0]['name']}' (Environment: {targets[0]['environment']})")

    # 4. Agent 2: Recon & API Discovery
    res = client.post(f"/api/v1/discovery/scan/{target_id}", headers=headers)
    assert res.status_code == 200
    discovery_data = res.json()["details"]
    print(f"✓ Agent 2 (Recon Discovery) Mapped {discovery_data['total_endpoints_discovered']} endpoints.")

    # 5. Agent 3: API Inventory Classification
    res = client.post(f"/api/v1/inventory/reclassify/{target_id}", headers=headers)
    assert res.status_code == 200
    inv = res.json()["result"]
    print(f"✓ Agent 3 (API Inventory) Classified APIs -> Active: {inv['active_count']}, Zombie: {inv['zombie_count']}, Shadow: {inv['shadow_count']}")

    # 6. Multi-Agent Security Scan (Agents 4, 5, 6, 7, 8, 9)
    scan_payload = {
        "target_id": target_id,
        "scan_name": "Integration Automated Scan",
        "scan_type": "full",
        "selected_categories": ["access_control", "business_logic", "authentication", "api_security"],
        "rate_limit_rps": 5.0,
        "auto_verify": True
    }
    res = client.post("/api/v1/scans", json=scan_payload, headers=headers)
    assert res.status_code == 200
    scan = res.json()
    print(f"✓ Multi-Agent Scan Completed -> Tested {scan['tested_endpoints']} endpoints, Identified {scan['vulnerabilities_count']} findings.")

    # 7. Verify Findings & Evidence (Agent 7 & Agent 8)
    res = client.get("/api/v1/vulnerabilities", headers=headers)
    assert res.status_code == 200
    vulns = res.json()
    assert len(vulns) > 0
    print(f"✓ Verified Vulnerabilities Found ({len(vulns)}):")
    for v in vulns:
        print(f"   • [{v['severity'].upper()}] {v['title']} (CVSS: {v['cvss_score']}, Status: {v['status']})")

    # 8. Test Patch & Retest Loop (Agent 10)
    print("\n--- Demonstrating Closed-Loop Fix & Retesting (Agent 10) ---")
    first_vuln = vulns[0]
    print(f"Selected finding to patch & retest: #{first_vuln['id']} - {first_vuln['title']}")

    # Toggle patch on staging app
    patch_res = client.post("/api/v1/staging/security/toggle-patch", json={
        "idor_vulnerable": False,
        "fare_tampering_vulnerable": False,
        "duplicate_refund_vulnerable": False
    })
    assert patch_res.status_code == 200
    print("✓ Staging server security patch applied (authorization and server pricing enforced).")

    # Call Retest Agent
    retest_res = client.post(f"/api/v1/vulnerabilities/{first_vuln['id']}/retest", json={
        "notes": "Developer patch committed in build v4.2"
    }, headers=headers)
    assert retest_res.status_code == 200
    retest_data = retest_res.json()
    print(f"✓ Agent 10 Retest Completed: Result = {retest_data['retest_result'].upper()}, Resolved = {retest_data['is_resolved']}")
    print(f"  Diff Summary: {retest_data['diff_summary']}")

    # 9. Report Export (Agent 9)
    csv_res = client.get("/api/v1/reports/export/csv", headers=headers)
    assert csv_res.status_code == 200
    assert "SentinelAI" in csv_res.text or "title" in csv_res.text
    print("✓ Agent 9 CSV Security Report Generated successfully.")

    print("\n=======================================================")
    print("ALL 10 AGENT CAPABILITIES AND PIPELINE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_full_dast_pipeline()
