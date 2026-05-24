from scripts.check_publish_readiness import build_report
from scripts.package_release import main as package_release_main


def test_publish_readiness_reports_required_assets_without_remote_failure():
    package_release_main()
    report = build_report()
    assert report["git_repository"] is True
    assert report["status"] in {"ready", "needs_remote", "ready_with_warnings"}
    assert any(item["path"] == "README.md" and item["exists"] for item in report["required_assets"])
    assert "git push -u origin main" in report["push_commands"]
