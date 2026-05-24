from clawflow.governance.policy import ToolPolicy


def test_policy_allows_low_risk_and_asks_high_risk():
    policy = ToolPolicy({"low": "allow", "medium": "ask", "high": "ask"})
    assert policy.decide("read_file", "low").decision == "allow"
    assert policy.decide("delete_file_dry_run", "high").decision == "ask"

