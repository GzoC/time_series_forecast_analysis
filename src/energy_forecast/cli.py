import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Daily industrial energy study")
    commands = parser.add_subparsers(dest="command", required=True)
    study = commands.add_parser("run")
    study.add_argument("--data", type=Path, default=Path("data/raw/Steel_industry_data.csv"))
    study.add_argument("--output", type=Path, default=Path("reports"))
    plan = commands.add_parser("plan")
    plan.add_argument("--scenario", type=Path)
    plan.add_argument("--output", type=Path, default=Path("reports/planning"))
    plan.add_argument("--max-nodes", type=int, default=1_000_000)
    dashboard = commands.add_parser("dashboard")
    dashboard.add_argument("--port", type=int, default=8504)
    args = parser.parse_args()
    if args.command == "plan":
        import json

        from .planning import load_scenario, run_planning

        try:
            scenario = load_scenario(args.scenario) if args.scenario else None
            report = run_planning(args.output, scenario, args.max_nodes)
        except (OSError, ValueError, TypeError) as exc:
            parser.error(str(exc))
        result = report["plans"]["optimized"]
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "feasible": result["feasible"],
                    "optimal": result["optimal"],
                    "cost_usd": result["total_cost_usd"],
                    "errors": result["errors"],
                    "output": str(args.output),
                },
                indent=2,
            )
        )
        if not result["feasible"]:
            raise SystemExit(2 if result["status"] == "infeasible" else 3)
    elif args.command == "run":
        from .evaluation import run

        report = run(args.data, args.output)
        print(
            f"Selected: {report['selected']}; test MAE: {report['test'][report['selected']]['mae_kwh']:.2f} kWh"
        )
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).with_name("dashboard.py")),
                "--server.address=127.0.0.1",
                f"--server.port={args.port}",
                "--server.headless=true",
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
