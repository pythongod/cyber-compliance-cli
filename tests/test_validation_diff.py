from cyber_compliance_cli.assessment_schema import validate_assessment
from cyber_compliance_cli.diffing import compare_assessments


def test_validate_assessment_ok():
    data = {"frameworks": {"nist_csf": {"statuses": {"A": "implemented"}}}}
    assert validate_assessment(data) == []


def test_validate_assessment_bad_status():
    data = {"frameworks": {"nist_csf": {"statuses": {"A": "weird"}}}}
    errs = validate_assessment(data)
    assert errs and "invalid status" in errs[0]


def test_compare_assessments_improvement():
    old = {"frameworks": {"nist_csf": {"statuses": {"A": "missing"}}}}
    new = {"frameworks": {"nist_csf": {"statuses": {"A": "partial"}}}}
    out = compare_assessments(old, new)
    assert len(out["improved"]) == 1
    assert len(out["regressed"]) == 0
