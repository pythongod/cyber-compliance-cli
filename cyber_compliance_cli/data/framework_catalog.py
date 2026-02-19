from __future__ import annotations

from typing import Dict, List

FRAMEWORK_CATALOG: Dict[str, List[dict]] = {
    "nist_csf": [
        {"id": "GV.OV-01", "title": "Governance strategy defined", "domain": "Govern"},
        {"id": "ID.AM-01", "title": "Asset inventory maintained", "domain": "Identify"},
        {"id": "PR.AA-01", "title": "Identity and access managed", "domain": "Protect"},
        {"id": "DE.CM-01", "title": "Continuous monitoring enabled", "domain": "Detect"},
        {"id": "RS.RP-01", "title": "Incident response plan executed", "domain": "Respond"},
        {"id": "RC.RP-01", "title": "Recovery plan validated", "domain": "Recover"},
    ],
    "pci_dss": [
        {"id": "1", "title": "Install and maintain network security controls", "domain": "Network Security"},
        {"id": "2", "title": "Apply secure configurations to all system components", "domain": "Secure Configuration"},
        {"id": "3", "title": "Protect stored account data", "domain": "Data Protection"},
        {"id": "4", "title": "Protect cardholder data with strong cryptography during transmission", "domain": "Crypto"},
        {"id": "5", "title": "Protect systems and networks from malicious software", "domain": "Malware Defense"},
        {"id": "6", "title": "Develop and maintain secure systems and software", "domain": "Secure SDLC"},
        {"id": "7", "title": "Restrict access to system components and cardholder data", "domain": "Access Control"},
        {"id": "8", "title": "Identify users and authenticate access", "domain": "Identity/Auth"},
        {"id": "9", "title": "Restrict physical access to cardholder data", "domain": "Physical Security"},
        {"id": "10", "title": "Log and monitor all access to system components and cardholder data", "domain": "Logging/Monitoring"},
        {"id": "11", "title": "Test security of systems and networks regularly", "domain": "Security Testing"},
        {"id": "12", "title": "Support information security with organizational policies", "domain": "Governance"},
    ],
}


def list_frameworks() -> List[str]:
    return sorted(FRAMEWORK_CATALOG.keys())


def list_controls(framework: str, query: str | None = None) -> List[dict]:
    key = framework.lower().strip()
    controls = FRAMEWORK_CATALOG.get(key, [])
    if not query:
        return controls
    q = query.lower().strip()
    return [c for c in controls if q in c["id"].lower() or q in c["title"].lower() or q in c["domain"].lower()]
