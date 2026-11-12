"""Small exact load scheduling, independent from the historical daily forecast.

All powers, tariffs and windows are synthetic assumptions available before dispatch.
No observed future series or held-out forecast targets are inputs to this module.
"""

import csv
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class Task:
    task_id: str
    power_kw: float
    duration_intervals: int
    release: int
    deadline: int  # Exclusive end of the allowed operating window.
    required_kwh: float
    fixed_start: int


@dataclass(frozen=True)
class Scenario:
    interval_hours: float
    capacity_kw: float
    base_kw: tuple[float, ...]
    tariff_usd_per_kwh: tuple[float, ...]
    tasks: tuple[Task, ...]

    def validate(self):
        def finite(value, name, positive=False):
            if (
                type(value) not in {float, int}
                or not math.isfinite(value)
                or value < 0
                or (positive and value == 0)
            ):
                raise ValueError(
                    f"{name} must be finite and {'positive' if positive else 'nonnegative'}"
                )

        finite(self.interval_hours, "interval_hours", True)
        finite(self.capacity_kw, "capacity_kw", True)
        if not self.base_kw or len(self.base_kw) != len(self.tariff_usd_per_kwh):
            raise ValueError("Base and tariff must have the same nonzero horizon")
        for value in self.base_kw:
            finite(value, "base_kw")
        for value in self.tariff_usd_per_kwh:
            finite(value, "tariff_usd_per_kwh")
        seen = set()
        for task in self.tasks:
            if (
                not isinstance(task.task_id, str)
                or not task.task_id.strip()
                or task.task_id in seen
            ):
                raise ValueError("Task IDs must be unique nonempty strings")
            seen.add(task.task_id)
            finite(task.power_kw, "power_kw", True)
            finite(task.required_kwh, "required_kwh")
            for name in ["duration_intervals", "release", "deadline", "fixed_start"]:
                if type(getattr(task, name)) is not int:
                    raise ValueError(f"{name} must be an integer")
            if task.duration_intervals < 1 or not 0 <= task.release < task.deadline <= len(
                self.base_kw
            ):
                raise ValueError("Invalid task duration or window")
        return self


def default_scenario():
    return Scenario(
        1.0,
        85.0,
        (42.0, 40.0, 44.0, 48.0, 50.0, 56.0, 60.0, 58.0, 52.0, 48.0, 44.0, 40.0),
        (0.09, 0.08, 0.08, 0.14, 0.21, 0.28, 0.30, 0.24, 0.16, 0.12, 0.10, 0.09),
        (
            Task("washing", 18.0, 2, 0, 8, 36.0, 1),
            Task("heater", 24.0, 3, 2, 12, 72.0, 4),
            Task("air_preparation", 12.0, 2, 0, 9, 24.0, 2),
            Task("finishing", 16.0, 2, 4, 12, 32.0, 7),
            Task("dryer", 14.0, 3, 6, 12, 42.0, 9),
        ),
    ).validate()


def load_scenario(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if set(raw) != {"interval_hours", "capacity_kw", "base_kw", "tariff_usd_per_kwh", "tasks"}:
        raise ValueError("Unknown or missing scenario fields")
    tasks = tuple(Task(**task) for task in raw["tasks"])
    return Scenario(
        raw["interval_hours"],
        raw["capacity_kw"],
        tuple(raw["base_kw"]),
        tuple(raw["tariff_usd_per_kwh"]),
        tasks,
    ).validate()


def options(task, scenario):
    energy = task.power_kw * task.duration_intervals * scenario.interval_hours
    if energy + 1e-9 < task.required_kwh:
        return []
    return list(range(task.release, task.deadline - task.duration_intervals + 1))


def task_cost(task, start, scenario):
    return (
        task.power_kw
        * scenario.interval_hours
        * sum(scenario.tariff_usd_per_kwh[start : start + task.duration_intervals])
    )


def assess(scenario, starts, method, status="feasible", **metadata):
    scenario.validate()
    errors = []
    flexible = [0.0] * len(scenario.base_kw)
    delivered = {}
    if set(starts) != {t.task_id for t in scenario.tasks}:
        errors.append("Every required task must be scheduled exactly once")
    for task in scenario.tasks:
        start = starts.get(task.task_id)
        if type(start) is not int or start not in options(task, scenario):
            errors.append(f"{task.task_id}: invalid window or unmet energy requirement")
            continue
        for index in range(start, start + task.duration_intervals):
            flexible[index] += task.power_kw
        delivered[task.task_id] = task.power_kw * task.duration_intervals * scenario.interval_hours
    total = [base + load for base, load in zip(scenario.base_kw, flexible, strict=True)]
    violations = [i for i, value in enumerate(total) if value > scenario.capacity_kw + 1e-9]
    if violations:
        errors.append(f"Capacity exceeded at intervals {violations}")
    feasible = not errors
    base_cost = sum(
        p * t * scenario.interval_hours
        for p, t in zip(scenario.base_kw, scenario.tariff_usd_per_kwh, strict=True)
    )
    flexible_cost = sum(
        p * t * scenario.interval_hours
        for p, t in zip(flexible, scenario.tariff_usd_per_kwh, strict=True)
    )
    return {
        "method": method,
        "status": status if feasible else "infeasible",
        "feasible": feasible,
        "starts": starts,
        "errors": errors,
        "delivered_kwh": delivered,
        "flexible_energy_kwh": sum(flexible) * scenario.interval_hours if feasible else None,
        "total_energy_kwh": sum(total) * scenario.interval_hours if feasible else None,
        "base_cost_usd": base_cost,
        "flexible_cost_usd": flexible_cost if feasible else None,
        "total_cost_usd": base_cost + flexible_cost if feasible else None,
        "peak_kw": max(total) if feasible else None,
        "flexible_kw": flexible,
        "total_kw": total,
        **metadata,
    }


def fixed(scenario):
    return assess(scenario, {task.task_id: task.fixed_start for task in scenario.tasks}, "fixed")


def greedy(scenario):
    scenario.validate()
    total = list(scenario.base_kw)
    starts = {}
    for task in scenario.tasks:
        candidates = sorted(
            options(task, scenario), key=lambda start: (task_cost(task, start, scenario), start)
        )
        chosen = next(
            (
                start
                for start in candidates
                if all(
                    total[i] + task.power_kw <= scenario.capacity_kw + 1e-9
                    for i in range(start, start + task.duration_intervals)
                )
            ),
            None,
        )
        if chosen is None:
            result = assess(scenario, starts, "greedy")
            result["status"] = "no_feasible_schedule_found"
            result["errors"].append("Greedy failure does not prove global infeasibility")
            return result
        starts[task.task_id] = chosen
        for i in range(chosen, chosen + task.duration_intervals):
            total[i] += task.power_kw
    return assess(scenario, starts, "greedy")


def optimize(scenario, max_nodes=1_000_000):
    """Enumerative branch-and-bound; claims optimality only after completing proof."""
    scenario.validate()
    if type(max_nodes) is not int or max_nodes < 1:
        raise ValueError("max_nodes must be a positive integer")
    candidates = {
        task.task_id: sorted(
            options(task, scenario), key=lambda start: (task_cost(task, start, scenario), start)
        )
        for task in scenario.tasks
    }
    if any(not choices for choices in candidates.values()) or any(
        p > scenario.capacity_kw + 1e-9 for p in scenario.base_kw
    ):
        result = assess(scenario, {}, "branch_and_bound")
        result.update(
            status="infeasible",
            optimal=False,
            proven_infeasible=True,
            nodes=0,
            proof="Task energy/window or base load makes every schedule infeasible",
        )
        result["errors"] = [
            f"{task.task_id}: no start satisfies its duration/window and energy requirement"
            for task in scenario.tasks
            if not candidates[task.task_id]
        ]
        excess = [
            i for i, power in enumerate(scenario.base_kw) if power > scenario.capacity_kw + 1e-9
        ]
        if excess:
            result["errors"].append(f"Base load alone exceeds capacity at intervals {excess}")
        return result
    ordered = sorted(scenario.tasks, key=lambda task: (len(candidates[task.task_id]), task.task_id))
    lower = [0.0] * (len(ordered) + 1)
    for index in range(len(ordered) - 1, -1, -1):
        task = ordered[index]
        lower[index] = lower[index + 1] + min(
            task_cost(task, s, scenario) for s in candidates[task.task_id]
        )
    incumbents = [plan for plan in [fixed(scenario), greedy(scenario)] if plan["feasible"]]
    incumbent = min(incumbents, key=lambda p: p["flexible_cost_usd"]) if incumbents else None
    best_cost = incumbent["flexible_cost_usd"] if incumbent else math.inf
    best = dict(incumbent["starts"]) if incumbent else None
    total = list(scenario.base_kw)
    nodes, limited = 0, False

    def search(index, cost, starts):
        nonlocal nodes, limited, best, best_cost
        if nodes >= max_nodes:
            limited = True
            return
        nodes += 1
        # Independent cheapest remaining starts provide a valid cost lower bound.
        if cost + lower[index] >= best_cost - 1e-9:
            return
        if index == len(ordered):
            best, best_cost = dict(starts), cost
            return
        task = ordered[index]
        for start in candidates[task.task_id]:
            if limited:
                return
            positions = range(start, start + task.duration_intervals)
            if any(total[i] + task.power_kw > scenario.capacity_kw + 1e-9 for i in positions):
                continue
            for i in positions:
                total[i] += task.power_kw
            starts[task.task_id] = start
            search(index + 1, cost + task_cost(task, start, scenario), starts)
            starts.pop(task.task_id)
            for i in positions:
                total[i] -= task.power_kw

    search(0, 0.0, {})
    status = (
        "feasible"
        if limited and best is not None
        else "unknown"
        if limited
        else "optimal"
        if best is not None
        else "infeasible"
    )
    result = assess(scenario, best or {}, "branch_and_bound")
    result.update(
        status=status,
        optimal=(best is not None and not limited),
        proven_infeasible=(status == "infeasible"),
        cost_tolerance_usd=1e-9,
        nodes=nodes,
        max_nodes=max_nodes,
        proof="Search budget reached; no optimality claim"
        if limited
        else "Complete branch-and-bound with admissible lower bounds",
    )
    if best is None:
        result["errors"] = [
            "Search budget ended without a feasible schedule"
            if limited
            else "No combination of task starts satisfies capacity and operating windows"
        ]
    return result


def compare(scenario, max_nodes=1_000_000):
    return {
        "fixed": fixed(scenario),
        "greedy": greedy(scenario),
        "optimized": optimize(scenario, max_nodes),
    }


def sensitivity(scenario, nominal, max_nodes=1_000_000):
    results = []
    for scale in [0.9, 1.0, 1.1, 1.2]:
        changed = replace(scenario, base_kw=tuple(p * scale for p in scenario.base_kw))
        stress = (
            assess(changed, nominal["starts"], "nominal_schedule_stress")
            if nominal["feasible"]
            else None
        )
        plan = optimize(changed, max_nodes)
        results.append(
            {
                "assumption": "base_power_multiplier",
                "factor": scale,
                "nominal_schedule_feasible": stress["feasible"] if stress else None,
                "nominal_schedule_errors": stress["errors"] if stress else None,
                "reoptimized_status": plan["status"],
                "reoptimized_cost_usd": plan["total_cost_usd"],
            }
        )
    for scale in [0.75, 1.25, 1.5]:
        changed = replace(
            scenario,
            tariff_usd_per_kwh=tuple(
                t * scale if 4 <= i <= 7 else t for i, t in enumerate(scenario.tariff_usd_per_kwh)
            ),
        )
        plan = optimize(changed, max_nodes)
        results.append(
            {
                "assumption": "peak_tariff_multiplier_intervals_4_to_7",
                "factor": scale,
                "reoptimized_status": plan["status"],
                "reoptimized_cost_usd": plan["total_cost_usd"],
            }
        )
    return results


def run_planning(output, scenario=None, max_nodes=1_000_000):
    scenario = (scenario or default_scenario()).validate()
    plans = compare(scenario, max_nodes)
    report = {
        "domain": "Separate synthetic scheduling exercise; not the UCI plant or an observed hourly profile",
        "assumptions": {
            "power_unit": "kW",
            "energy_unit": "kWh",
            "currency": "USD",
            "tariff_unit": "USD/kWh",
            "base": "Synthetic day-ahead estimate available before dispatch",
            "tariff": "Assumed announced before dispatch; no tax or demand charge",
            "tasks": "All mandatory, fixed power, contiguous nonpreemptive duration, one start each",
            "uncertainty": "Sensitivity scenarios are assumptions, not observed future consumption",
        },
        "scenario": asdict(scenario),
        "plans": plans,
        "sensitivity": sensitivity(scenario, plans["optimized"], max_nodes),
    }
    reference = plans["fixed"]["total_cost_usd"]
    report["simulated_cost_reduction_usd"] = (
        reference - plans["optimized"]["total_cost_usd"]
        if plans["fixed"]["feasible"] and plans["optimized"]["feasible"]
        else None
    )
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "planning.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (output / "scenario.json").write_text(
        json.dumps(asdict(scenario), indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Generated synthetic dispatch results",
        "",
        report["domain"],
        "",
        "| Method | Status | Total cost (USD) | Peak (kW) |",
        "|---|---|---:|---:|",
    ]
    for method, plan in plans.items():
        cost = f"{plan['total_cost_usd']:.2f}" if plan["feasible"] else "N/A"
        peak = f"{plan['peak_kw']:.2f}" if plan["feasible"] else "N/A"
        lines.append(f"| {method} | {plan['status']} | {cost} | {peak} |")
    lines += [
        "",
        f"Estimated cost reduction versus fixed schedule: {report['simulated_cost_reduction_usd']:.2f} USD, simulated under stated assumptions only."
        if report["simulated_cost_reduction_usd"] is not None
        else "Fixed reference or optimized dispatch infeasible; no cost reduction claimed.",
        "",
        "All powers are synthetic; energy is power × interval hours. Sensitivity and constraint details are in planning.json. Optimality applies only to this finite discrete model, never to an actual plant.",
    ]
    (output / "PLANNING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (output / "dispatch.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = [
            "method",
            "interval",
            "start_hour",
            "end_hour",
            "base_kw",
            "flexible_kw",
            "total_kw",
            "capacity_kw",
            "energy_kwh",
            "tariff_usd_per_kwh",
            "cost_usd",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for method, plan in plans.items():
            if not plan["feasible"]:
                continue
            for i, power in enumerate(plan["total_kw"]):
                writer.writerow(
                    {
                        "method": method,
                        "interval": i,
                        "start_hour": i * scenario.interval_hours,
                        "end_hour": (i + 1) * scenario.interval_hours,
                        "base_kw": scenario.base_kw[i],
                        "flexible_kw": plan["flexible_kw"][i],
                        "total_kw": power,
                        "capacity_kw": scenario.capacity_kw,
                        "energy_kwh": power * scenario.interval_hours,
                        "tariff_usd_per_kwh": scenario.tariff_usd_per_kwh[i],
                        "cost_usd": power
                        * scenario.interval_hours
                        * scenario.tariff_usd_per_kwh[i],
                    }
                )
    return report
