from pathlib import Path

from scripts.run_benchmark import main


def test_benchmark_script_writes_results():
    data = main()
    assert data["total_tasks"] >= 6
    assert Path("outputs/benchmark_results.json").exists()
    assert Path("docs/assets/figures/benchmark_latency.png").exists()

