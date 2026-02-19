from cyber_compliance_cli.data.framework_catalog import list_frameworks, list_controls


def test_catalog_has_pci_and_nist():
    fws = list_frameworks()
    assert "nist_csf" in fws
    assert "pci_dss" in fws


def test_pci_controls_exist():
    rows = list_controls("pci_dss")
    assert len(rows) >= 12


def test_control_query_filters():
    rows = list_controls("pci_dss", query="cryptography")
    assert any("cryptography" in r["title"].lower() for r in rows)
