"""
EXP13 — Error Topology predicts Self-Consistency success.

Phase A (default): offline/simulation dry run.
- Generates arithmetic-chain tasks at 3 difficulties.
- Samples k answers per task at temperatures 0.2/0.7/1.0.
- Logs every generation to JSONL.
- Aggregates per-task error topology metrics.
- Writes a Markdown report.

This script is intentionally self-contained and stdlib-only.
It does NOT claim to prove anything about real LLMs; Phase A validates the
measurement pipeline before a real-model pilot.

Run:
  python ai-earth-rebuild/experiments/exp13_error_topology.py

Outputs:
  ai-earth-rebuild/runs/exp13_<timestamp>/generations.jsonl
  ai-earth-rebuild/runs/exp13_<timestamp>/task_metrics.jsonl
  ai-earth-rebuild/runs/exp13_<timestamp>/report.md
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


# -----------------------------
# Task generation
# -----------------------------

@dataclass(frozen=True)
class Task:
    task_id: str
    difficulty: str
    steps: int
    prompt: str
    answer: int
    ops: list[tuple[str, int]]
    start: int


def apply_op(acc: int, op: str, val: int) -> int:
    if op == "+":
        return acc + val
    if op == "-":
        return acc - val
    if op == "*":
        return acc * val
    raise ValueError(op)


def make_task(task_id: str, difficulty: str, steps: int, rng: random.Random) -> Task:
    # Keep numbers small enough to parse, but hard enough after repeated multiplication.
    ops_choices = ["+", "-", "*"]
    start = rng.randint(1, 9)
    acc = start
    ops: list[tuple[str, int]] = []
    for _ in range(steps):
        op = rng.choice(ops_choices)
        val = rng.randint(2, 9)
        ops.append((op, val))
        acc = apply_op(acc, op, val)
    prompt = "\n".join([f"START {start}"] + [f"OP {op} {v}" for op, v in ops])
    return Task(task_id=task_id, difficulty=difficulty, steps=steps, prompt=prompt, answer=acc, ops=ops, start=start)


def make_dataset(n_per_difficulty: int, seed: int) -> list[Task]:
    rng = random.Random(seed)
    specs = [("easy", 5), ("medium", 8), ("hard", 11)]
    tasks: list[Task] = []
    for difficulty, steps in specs:
        for i in range(n_per_difficulty):
            tasks.append(make_task(f"{difficulty}_{i:03d}", difficulty, steps, rng))
    return tasks


# -----------------------------
# Simulated answer generator
# -----------------------------

class TopologySimulator:
    """A dry-run sampler with explicit error topology.

    It intentionally models *families of errors*, not just random noise:
    - Correct answer mode.
    - A task-specific systematic wrong mode.
    - Several scattered wrong modes.

    Temperature changes the Q/D trade-off:
    - low T: less diverse, more collapse onto the top mode;
    - mid T: useful diversity;
    - high T: more diversity but lower single-sample quality.
    """

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def wrong_modes(self, task: Task) -> list[int]:
        ans = task.answer
        # Generate plausible recurrent wrong answers.
        # These are not meant to mimic any specific LLM; they create topology for pipeline validation.
        modes = []
        modes.append(ans + 1)
        modes.append(ans - 1)
        modes.append(-ans)
        modes.append(task.start)  # premature stop / no-op

        # Treat the first multiplication as addition: common systematic arithmetic misconception.
        acc = task.start
        replaced = False
        for op, val in task.ops:
            op2 = "+" if (op == "*" and not replaced) else op
            if op == "*" and not replaced:
                replaced = True
            acc = apply_op(acc, op2, val)
        modes.append(acc)

        # Drop the last operation.
        acc = task.start
        for op, val in task.ops[:-1]:
            acc = apply_op(acc, op, val)
        modes.append(acc)

        # Deduplicate and remove the correct answer.
        out = []
        for x in modes:
            if x != ans and x not in out:
                out.append(x)
        return out or [ans + 1]

    def base_correct_prob(self, difficulty: str, temperature: float) -> float:
        # p(correct single sample) at T=.7, then temp adjustments.
        base = {"easy": 0.78, "medium": 0.55, "hard": 0.34}[difficulty]
        if temperature <= 0.25:
            # low diversity: can be strong if top mode correct, but brittle.
            return min(0.90, base + 0.08)
        if temperature >= 0.95:
            # high diversity: lower Q.
            return max(0.08, base - 0.12)
        return base

    def systematic_strength(self, task: Task) -> float:
        # Some tasks have a strong wrong mode; deterministic by task_id.
        h = sum(ord(c) for c in task.task_id) % 100
        if task.difficulty == "easy":
            return 0.10 + (h % 10) / 100
        if task.difficulty == "medium":
            return 0.20 + (h % 20) / 100
        return 0.30 + (h % 30) / 100

    def sample_answer(self, task: Task, temperature: float) -> int:
        p_correct = self.base_correct_prob(task.difficulty, temperature)
        wrongs = self.wrong_modes(task)
        sys_wrong = wrongs[0]
        sys_strength = self.systematic_strength(task)

        # Temperature affects wrong-mode concentration.
        if temperature <= 0.25:
            sys_strength = min(0.85, sys_strength + 0.25)
        elif temperature >= 0.95:
            sys_strength = max(0.05, sys_strength - 0.15)

        r = self.rng.random()
        if r < p_correct:
            return task.answer

        # Conditional on being wrong, choose systematic vs scattered.
        if self.rng.random() < sys_strength:
            return sys_wrong
        return self.rng.choice(wrongs)


# -----------------------------
# Metrics
# -----------------------------

def entropy(counts: Counter[Any]) -> float:
    n = sum(counts.values())
    if n == 0:
        return 0.0
    e = 0.0
    for c in counts.values():
        p = c / n
        e -= p * math.log(p + 1e-12)
    return e


def pairwise_error_agreement(answers: list[int], correct_answer: int) -> float:
    wrongs = [a for a in answers if a != correct_answer]
    n = len(wrongs)
    if n < 2:
        return 0.0
    same = 0
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1
            if wrongs[i] == wrongs[j]:
                same += 1
    return same / total if total else 0.0


def majority_answer(answers: list[int]) -> tuple[int, bool]:
    counts = Counter(answers)
    max_count = max(counts.values())
    winners = [a for a, c in counts.items() if c == max_count]
    # Tie-break deterministically by first occurrence; record tie.
    for a in answers:
        if a in winners:
            return a, len(winners) > 1
    raise RuntimeError("unreachable")


def task_metrics(task: Task, answers: list[int], temperature: float) -> dict[str, Any]:
    k = len(answers)
    counts = Counter(answers)
    correct_count = counts.get(task.answer, 0)
    wrong_counts = Counter({a: c for a, c in counts.items() if a != task.answer})
    if wrong_counts:
        largest_wrong_answer, largest_wrong_count = wrong_counts.most_common(1)[0]
    else:
        largest_wrong_answer, largest_wrong_count = None, 0
    sc_answer, sc_tie = majority_answer(answers)
    mode_margin = correct_count - largest_wrong_count
    return {
        "task_id": task.task_id,
        "difficulty": task.difficulty,
        "steps": task.steps,
        "temperature": temperature,
        "k": k,
        "ground_truth": task.answer,
        "correct_count": correct_count,
        "largest_wrong_answer": largest_wrong_answer,
        "largest_wrong_count": largest_wrong_count,
        "mode_margin": mode_margin,
        "wrong_mode_dominance": largest_wrong_count / k,
        "distinct_answer_count": len(counts),
        "answer_entropy": entropy(counts),
        "pairwise_error_agreement": pairwise_error_agreement(answers, task.answer),
        "sc_answer": sc_answer,
        "sc_correct": sc_answer == task.answer,
        "sc_tie": sc_tie,
        "single_sample_accuracy": correct_count / k,
        "answers": dict(counts),
    }


# -----------------------------
# Reporting
# -----------------------------

def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def pct(x: float) -> str:
    return f"{100*x:.1f}%"


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {"n": 0, "single_acc": 0, "sc_acc": 0, "sc_gain": 0, "mean_margin": 0, "mean_wrong_dom": 0}
    single_acc = mean([r["single_sample_accuracy"] for r in rows])
    sc_acc = mean([1.0 if r["sc_correct"] else 0.0 for r in rows])
    return {
        "n": len(rows),
        "single_acc": single_acc,
        "sc_acc": sc_acc,
        "sc_gain": sc_acc - single_acc,
        "mean_margin": mean([r["mode_margin"] for r in rows]),
        "mean_wrong_dom": mean([r["wrong_mode_dominance"] for r in rows]),
        "mean_entropy": mean([r["answer_entropy"] for r in rows]),
        "mean_err_agree": mean([r["pairwise_error_agreement"] for r in rows]),
    }


def margin_bin(r: dict[str, Any]) -> str:
    if r["mode_margin"] > 0:
        return "margin > 0"
    if r["mode_margin"] == 0:
        return "margin = 0"
    return "margin < 0"


def failure_reason(r: dict[str, Any]) -> str:
    if r["sc_correct"]:
        return "SC correct"
    if r["correct_count"] == 0:
        return "no correct samples"
    if r["largest_wrong_count"] >= r["correct_count"]:
        return "wrong mode >= correct mode"
    if r["sc_tie"]:
        return "tie-breaking failure"
    if r["answer_entropy"] > 2.0:
        return "high entropy / scattered"
    return "other"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def make_report(rows: list[dict[str, Any]], outdir: Path) -> str:
    lines: list[str] = []
    lines.append("# EXP13 Phase A Report — Error Topology Dry Run")
    lines.append("")
    lines.append("**Status:** simulation/dry-run only. This validates the measurement pipeline; it is not evidence about real LLMs.")
    lines.append("")

    overall = summarize(rows)
    lines.append("## 1. Overall")
    lines.append(markdown_table(
        ["n task-temp cells", "single acc", "SC acc", "SC gain", "mean margin", "wrong dom", "entropy", "err agree"],
        [[overall["n"], pct(overall["single_acc"]), pct(overall["sc_acc"]), pct(overall["sc_gain"]),
          f'{overall["mean_margin"]:.2f}', f'{overall["mean_wrong_dom"]:.2f}', f'{overall["mean_entropy"]:.2f}', f'{overall["mean_err_agree"]:.2f}']]
    ))
    lines.append("")

    for group_name, key in [("Difficulty", "difficulty"), ("Temperature", "temperature")]:
        lines.append(f"## 2. By {group_name}")
        grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            grouped[r[key]].append(r)
        table = []
        for g in sorted(grouped, key=str):
            s = summarize(grouped[g])
            table.append([g, s["n"], pct(s["single_acc"]), pct(s["sc_acc"]), pct(s["sc_gain"]), f'{s["mean_margin"]:.2f}', f'{s["mean_wrong_dom"]:.2f}'])
        lines.append(markdown_table([group_name.lower(), "n", "single", "SC", "gain", "margin", "wrong_dom"], table))
        lines.append("")

    lines.append("## 3. By mode-margin bin")
    grouped2: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        grouped2[margin_bin(r)].append(r)
    order = ["margin > 0", "margin = 0", "margin < 0"]
    table = []
    for b in order:
        s = summarize(grouped2[b])
        table.append([b, s["n"], pct(s["single_acc"]), pct(s["sc_acc"]), pct(s["sc_gain"]), f'{s["mean_wrong_dom"]:.2f}', f'{s["mean_err_agree"]:.2f}'])
    lines.append(markdown_table(["bin", "n", "single", "SC", "gain", "wrong_dom", "err_agree"], table))
    lines.append("")

    lines.append("## 4. Failure taxonomy")
    fr = Counter(failure_reason(r) for r in rows)
    lines.append(markdown_table(["reason", "count"], [[k, v] for k, v in fr.most_common()]))
    lines.append("")

    # Hypothesis readout.
    pos = summarize(grouped2["margin > 0"])
    nonpos = summarize(grouped2["margin = 0"] + grouped2["margin < 0"])
    delta = pos["sc_acc"] - nonpos["sc_acc"]
    lines.append("## 5. Preregistered readout")
    lines.append(f"SC accuracy when margin > 0: **{pct(pos['sc_acc'])}** (n={pos['n']})")
    lines.append(f"SC accuracy when margin <= 0: **{pct(nonpos['sc_acc'])}** (n={nonpos['n']})")
    lines.append(f"Difference: **{pct(delta)}**")
    lines.append("")
    if pos["n"] and nonpos["n"] and delta >= 0.25:
        lines.append("**Dry-run pattern:** supports the measurement logic: mode_margin separates SC success from failure in the simulator.")
    else:
        lines.append("**Dry-run pattern:** weak or absent separation; inspect simulator/settings before real pilot.")
    lines.append("")
    lines.append("## 6. Files")
    lines.append("- `generations.jsonl`: every sample.")
    lines.append("- `task_metrics.jsonl`: per task × temperature metrics.")

    report = "\n".join(lines) + "\n"
    (outdir / "report.md").write_text(report, encoding="utf-8")
    return report


# -----------------------------
# Runner
# -----------------------------

def run_phase_a(args: argparse.Namespace) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    outdir = Path(args.outdir) / f"exp13_{timestamp}"
    outdir.mkdir(parents=True, exist_ok=True)

    tasks = make_dataset(n_per_difficulty=args.n_per_difficulty, seed=args.seed)
    temps = [float(x) for x in args.temperatures.split(",")]
    sim = TopologySimulator(seed=args.seed + 12345)

    generations_path = outdir / "generations.jsonl"
    metrics_path = outdir / "task_metrics.jsonl"

    all_metrics: list[dict[str, Any]] = []

    with generations_path.open("w", encoding="utf-8") as gf, metrics_path.open("w", encoding="utf-8") as mf:
        for temp in temps:
            for task in tasks:
                answers: list[int] = []
                for sample_index in range(args.k):
                    ans = sim.sample_answer(task, temp)
                    answers.append(ans)
                    rec = {
                        "task_id": task.task_id,
                        "difficulty": task.difficulty,
                        "steps": task.steps,
                        "prompt": task.prompt,
                        "ground_truth": task.answer,
                        "sample_index": sample_index,
                        "temperature": temp,
                        "raw_output": f"ANSWER {ans}",
                        "parsed_answer": ans,
                        "is_correct": ans == task.answer,
                        "model": "TopologySimulator",
                        "provider": "offline",
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "usd": 0.0,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    gf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                m = task_metrics(task, answers, temp)
                all_metrics.append(m)
                mf.write(json.dumps(m, ensure_ascii=False) + "\n")

    report = make_report(all_metrics, outdir)
    print(report)
    print(f"\nWrote run to: {outdir}")
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["A"], default="A")
    parser.add_argument("--outdir", default="ai-earth-rebuild/runs")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--n-per-difficulty", type=int, default=40)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--temperatures", default="0.2,0.7,1.0")
    args = parser.parse_args()
    run_phase_a(args)


if __name__ == "__main__":
    main()
