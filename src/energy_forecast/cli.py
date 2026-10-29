import argparse
import subprocess
import sys
from pathlib import Path

from .evaluation import run


def main():
    parser = argparse.ArgumentParser(description="Daily industrial energy study")
    commands = parser.add_subparsers(dest="command", required=True)
    study = commands.add_parser("run")
    study.add_argument("--data", type=Path, default=Path("data/raw/Steel_industry_data.csv"))
    study.add_argument("--output", type=Path, default=Path("reports"))
    dashboard = commands.add_parser("dashboard")
    dashboard.add_argument("--port", type=int, default=8504)
    args = parser.parse_args()
    if args.command == "run":
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
