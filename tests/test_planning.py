import itertools
import json
import subprocess
import sys
from dataclasses import asdict, replace

import pytest

from energy_forecast.planning import (
    Scenario,
    Task,
    assess,
    compare,
    default_scenario,
    load_scenario,
    optimize,
    run_planning,
    sensitivity,
)


def brute_force(scenario):
    """Independent enumeration used only for tiny oracle cases."""
    best = None
    ranges = [range(t.release, t.deadline - t.duration_intervals + 1) for t in scenario.tasks]
    for starts in itertools.product(*ranges):
        powers = [
            scenario.base_kw[i]
            + sum(
                t.power_kw
                for t, s in zip(scenario.tasks, starts, strict=True)
                if s <= i < s + t.duration_intervals
            )
            for i in range(len(scenario.base_kw))
        ]
        if max(powers) > scenario.capacity_kw:
            continue
        cost = sum(
            p * price * scenario.interval_hours
            for p, price in zip(powers, scenario.tariff_usd_per_kwh, strict=True)
        )
        best = cost if best is None else min(best, cost)
    return best


@pytest.mark.parametrize("capacity", [6.0, 8.0, 10.0])
def test_exact_solution_matches_independent_enumeration(capacity):
    scenario = Scenario(
        0.5,
        capacity,
        (2.0, 3.0, 2.0, 4.0),
        (0.1, 0.4, 0.2, 0.1),
        (Task("A", 3.0, 2, 0, 4, 3.0, 0), Task("B", 2.0, 1, 1, 4, 1.0, 2)),
    )
    plan = optimize(scenario)
    oracle = brute_force(scenario)
    if oracle is None:
        assert plan["status"] == "infeasible" and not plan["feasible"]
    else:
        assert plan["status"] == "optimal" and plan["optimal"]
        assert plan["total_cost_usd"] == pytest.approx(oracle)


def test_energy_uses_interval_duration_and_cost_units():
    scenario = Scenario(0.25, 10.0, (0.0, 0.0), (2.0, 2.0), (Task("A", 1.0, 2, 0, 2, 0.5, 0),))
    result = optimize(scenario)
    assert result["delivered_kwh"] == {"A": 0.5}
    assert result["total_energy_kwh"] == 0.5
    assert result["total_cost_usd"] == 1.0


def test_default_all_methods_deliver_same_tasks_and_optimization_never_worse():
    scenario = default_scenario()
    plans = compare(scenario)
    assert all(plan["feasible"] for plan in plans.values())
    for plan in plans.values():
        assert set(plan["starts"]) == {t.task_id for t in scenario.tasks}
        assert max(plan["total_kw"]) <= scenario.capacity_kw + 1e-9
        for task in scenario.tasks:
            start = plan["starts"][task.task_id]
            assert task.release <= start and start + task.duration_intervals <= task.deadline
            assert plan["delivered_kwh"][task.task_id] >= task.required_kwh
        assert plan["flexible_energy_kwh"] == 206.0
    assert plans["optimized"]["optimal"]
    assert (
        plans["optimized"]["total_cost_usd"]
        <= min(p["total_cost_usd"] for p in plans.values()) + 1e-9
    )


@pytest.mark.parametrize("failure", ["base_capacity", "load_capacity", "window", "energy"])
def test_infeasibility_is_reported_without_a_valid_schedule(failure):
    scenario = Scenario(1.0, 5.0, (1.0, 1.0), (0.1, 0.2), (Task("A", 2.0, 1, 0, 2, 2.0, 0),))
    if failure == "base_capacity":
        scenario = replace(scenario, base_kw=(6.0, 1.0))
    elif failure == "load_capacity":
        scenario = replace(scenario, capacity_kw=2.0)
    elif failure == "window":
        scenario = replace(scenario, tasks=(replace(scenario.tasks[0], duration_intervals=3),))
    else:
        scenario = replace(scenario, tasks=(replace(scenario.tasks[0], required_kwh=3.0),))
    result = optimize(scenario)
    assert result["status"] == "infeasible" and not result["feasible"]
    assert not result["optimal"]
    assert result["proven_infeasible"]
    assert result["total_cost_usd"] is None


def test_budget_limited_search_is_feasible_without_claiming_optimality():
    result = optimize(default_scenario(), max_nodes=1)
    assert result["status"] == "feasible" and result["feasible"]
    assert not result["optimal"] and "budget" in result["proof"]


@pytest.mark.parametrize(
    "changes",
    [
        {"interval_hours": 0},
        {"capacity_kw": float("nan")},
        {"tariff_usd_per_kwh": (-1.0,) * 12},
        {"base_kw": (1.0,)},
        {"capacity_kw": True},
    ],
)
def test_invalid_physical_inputs_are_rejected(changes):
    with pytest.raises(ValueError):
        optimize(replace(default_scenario(), **changes))


def test_duplicate_tasks_and_missing_tasks_are_rejected():
    scenario = default_scenario()
    with pytest.raises(ValueError):
        optimize(replace(scenario, tasks=(scenario.tasks[0], scenario.tasks[0])))
    assert not assess(scenario, {}, "external")["feasible"]


def test_sensitivity_flags_nominal_schedule_capacity_risk():
    scenario = default_scenario()
    nominal = optimize(scenario)
    rows = sensitivity(scenario, nominal)
    assert any(row.get("nominal_schedule_feasible") is False for row in rows)
    assert any(row["assumption"].startswith("peak_tariff") for row in rows)


def test_scenario_roundtrip_and_reports_have_explicit_units(tmp_path):
    report = run_planning(tmp_path)
    restored = load_scenario(tmp_path / "scenario.json")
    assert restored == default_scenario()
    assert report["assumptions"]["tariff_unit"] == "USD/kWh"
    assert json.loads((tmp_path / "planning.json").read_text()) == json.loads(json.dumps(report))
    assert (tmp_path / "dispatch.csv").read_text().count("\n") == 37
    assert (tmp_path / "PLANNING.md").exists()


def test_planning_cli_is_independent_of_forecast_files_and_reports(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "energy_forecast.cli", "plan", "--output", str(tmp_path / "out")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "optimal"
    assert not (tmp_path / "data").exists()
    scenario = replace(default_scenario(), capacity_kw=1.0)
    (tmp_path / "impossible.json").write_text(json.dumps(asdict(scenario)))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "energy_forecast.cli",
            "plan",
            "--scenario",
            str(tmp_path / "impossible.json"),
            "--output",
            str(tmp_path / "impossible"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2 and json.loads(result.stdout)["status"] == "infeasible"
    assert (tmp_path / "impossible/planning.json").exists()
