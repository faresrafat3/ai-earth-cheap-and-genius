"""
EXP0 — Instrument Stability Calibration.

Question:
  Does the same task + prompt + model + sampling setting produce stable answer
  topology across independent sessions?

Default run:
  20 tasks x 3 sessions x k=10 = 600 generations.

Outputs:
  runs/exp0_<timestamp>/generations.jsonl
  runs/exp0_<timestamp>/session_task_metrics.jsonl
  runs/exp0_<timestamp>/stability_metrics.jsonl
  runs/exp0_<timestamp>/report.md

Secrets:
  Reads OPENROUTER_KEYS from /tmp/ai_earth_keys.env or environment.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.resource_manager import ResourceManager


SYSTEM = (
    "You are a precise arithmetic solver. The user gives a START value and OP lines. "
    "Apply operations strictly in order, left-to-right, ignoring normal precedence. "
    "Return the final line exactly as: ANSWER <integer>."
)


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
    if op == "+": return acc + val
    if op == "-": return acc - val
    if op == "*": return acc * val
    raise ValueError(op)


def make_task(task_id: str, difficulty: str, steps: int, rng: random.Random) -> Task:
    start = rng.randint(1, 9)
    acc = start
    ops = []
    for _ in range(steps):
        op = rng.choice(["+", "-", "*"])
        val = rng.randint(2, 9)
        ops.append((op, val))
        acc = apply_op(acc, op, val)
    prompt = "\n".join([f"START {start}"] + [f"OP {op} {v}" for op, v in ops])
    return Task(task_id, difficulty, steps, prompt, acc, ops, start)


def make_dataset(seed: int, n_easy: int, n_medium: int, n_hard: int) -> list[Task]:
    rng = random.Random(seed)
    tasks = []
    for difficulty, steps, n in [("easy", 5, n_easy), ("medium", 8, n_medium), ("hard", 11, n_hard)]:
        for i in range(n):
            tasks.append(make_task(f"{difficulty}_{i:03d}", difficulty, steps, rng))
    return tasks


def parse_answer(text: str) -> int | None:
    m = re.search(r"ANSWER[^\-0-9]*(-?\d+)", text, flags=re.I)
    if m:
        try: return int(m.group(1))
        except Exception: return None
    nums = re.findall(r"-?\d+", text)
    if not nums: return None
    try: return int(nums[-1])
    except Exception: return None


def entropy(counts: Counter[Any]) -> float:
    n = sum(counts.values())
    if n == 0: return 0.0
    return -sum((c/n)*math.log((c/n)+1e-12) for c in counts.values())


def pairwise_error_agreement(answers: list[int | None], correct: int) -> float:
    wrongs = [a for a in answers if a != correct]
    if len(wrongs) < 2: return 0.0
    same = total = 0
    for i in range(len(wrongs)):
        for j in range(i+1, len(wrongs)):
            total += 1
            same += int(wrongs[i] == wrongs[j])
    return same / total if total else 0.0


def majority_answer(answers: list[int | None]) -> tuple[int | None, bool]:
    c = Counter(answers)
    maxc = max(c.values())
    winners = [a for a, n in c.items() if n == maxc]
    for a in answers:
        if a in winners:
            return a, len(winners) > 1
    raise RuntimeError("unreachable")


def session_task_metrics(task: Task, session_id: int, answers: list[int | None], temperature: float) -> dict[str, Any]:
    k = len(answers)
    counts = Counter(answers)
    correct_count = counts.get(task.answer, 0)
    wrong_counts = Counter({a: c for a, c in counts.items() if a != task.answer})
    if wrong_counts:
        largest_wrong_answer, largest_wrong_count = wrong_counts.most_common(1)[0]
    else:
        largest_wrong_answer, largest_wrong_count = None, 0
    sc_answer, sc_tie = majority_answer(answers)
    return {
        "task_id": task.task_id,
        "session_id": session_id,
        "difficulty": task.difficulty,
        "steps": task.steps,
        "temperature": temperature,
        "k": k,
        "ground_truth": task.answer,
        "top_answer": counts.most_common(1)[0][0],
        "top_count": counts.most_common(1)[0][1],
        "sc_answer": sc_answer,
        "sc_correct": sc_answer == task.answer,
        "sc_tie": sc_tie,
        "correct_count": correct_count,
        "largest_wrong_answer": largest_wrong_answer,
        "largest_wrong_count": largest_wrong_count,
        "mode_margin": correct_count - largest_wrong_count,
        "wrong_mode_dominance": largest_wrong_count / k,
        "distinct_answer_count": len(counts),
        "answer_entropy": entropy(counts),
        "pairwise_error_agreement": pairwise_error_agreement(answers, task.answer),
        "single_sample_accuracy": correct_count / k,
        "answers": {str(a): c for a, c in counts.items()},
    }


def distribution_overlap(a: dict[str, int], b: dict[str, int]) -> float:
    keys = set(a) | set(b)
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb: return 0.0
    return sum(min(a.get(k, 0)/na, b.get(k, 0)/nb) for k in keys)


def stability_for_task(rows: list[dict[str, Any]]) -> dict[str, Any]:
    task_id = rows[0]["task_id"]
    tops = [str(r["top_answer"]) for r in rows]
    sc_answers = [str(r["sc_answer"]) for r in rows]
    sc_corrects = [bool(r["sc_correct"]) for r in rows]
    margins = [float(r["mode_margin"]) for r in rows]
    entropies = [float(r["answer_entropy"]) for r in rows]
    overlaps = []
    for i in range(len(rows)):
        for j in range(i+1, len(rows)):
            overlaps.append(distribution_overlap(rows[i]["answers"], rows[j]["answers"]))
    return {
        "task_id": task_id,
        "difficulty": rows[0]["difficulty"],
        "top_answer_stable": len(set(tops)) == 1,
        "sc_answer_stable": len(set(sc_answers)) == 1,
        "sc_correct_stable": len(set(sc_corrects)) == 1,
        "top_answers": tops,
        "sc_answers": sc_answers,
        "sc_corrects": sc_corrects,
        "mode_margin_min": min(margins),
        "mode_margin_max": max(margins),
        "mode_margin_range": max(margins) - min(margins),
        "entropy_min": min(entropies),
        "entropy_max": max(entropies),
        "entropy_range": max(entropies) - min(entropies),
        "mean_distribution_overlap": sum(overlaps)/len(overlaps) if overlaps else 0.0,
    }


def pct(x: float) -> str:
    return f"{100*x:.1f}%"


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"]*len(headers)) + "|"]
    out += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(out)


def write_report(outdir: Path, session_rows: list[dict[str, Any]], stability_rows: list[dict[str, Any]], generation_count: int) -> None:
    n = len(stability_rows)
    top_stab = sum(r["top_answer_stable"] for r in stability_rows) / n if n else 0
    sc_ans_stab = sum(r["sc_answer_stable"] for r in stability_rows) / n if n else 0
    sc_corr_stab = sum(r["sc_correct_stable"] for r in stability_rows) / n if n else 0
    mean_overlap = sum(r["mean_distribution_overlap"] for r in stability_rows) / n if n else 0
    mean_margin_range = sum(r["mode_margin_range"] for r in stability_rows) / n if n else 0
    mean_entropy_range = sum(r["entropy_range"] for r in stability_rows) / n if n else 0

    # Session summary
    by_session = defaultdict(list)
    for r in session_rows:
        by_session[r["session_id"]].append(r)
    session_table = []
    for sid in sorted(by_session):
        rows = by_session[sid]
        single = sum(r["single_sample_accuracy"] for r in rows) / len(rows)
        sc = sum(1 for r in rows if r["sc_correct"]) / len(rows)
        margin = sum(r["mode_margin"] for r in rows) / len(rows)
        ent = sum(r["answer_entropy"] for r in rows) / len(rows)
        session_table.append([sid, len(rows), pct(single), pct(sc), f"{margin:.2f}", f"{ent:.2f}"])

    unstable = [r for r in stability_rows if not r["top_answer_stable"] or not r["sc_correct_stable"]]

    lines = []
    lines.append("# EXP0 Instrument Stability Calibration Report")
    lines.append("")
    lines.append("This is a calibration run: it tests whether answer topology is stable across repeated sessions.")
    lines.append("")
    lines.append("## Overall stability")
    lines.append(table(
        ["tasks", "generations", "top-answer stable", "SC-answer stable", "SC-correct stable", "mean dist overlap", "mean margin range", "mean entropy range"],
        [[n, generation_count, pct(top_stab), pct(sc_ans_stab), pct(sc_corr_stab), f"{mean_overlap:.2f}", f"{mean_margin_range:.2f}", f"{mean_entropy_range:.2f}"]]
    ))
    lines.append("")
    lines.append("## By session")
    lines.append(table(["session", "tasks", "single", "SC", "mean margin", "mean entropy"], session_table))
    lines.append("")
    lines.append("## Unstable tasks")
    if unstable:
        lines.append(table(
            ["task_id", "difficulty", "top_answers", "sc_corrects", "margin_range", "overlap"],
            [[u["task_id"], u["difficulty"], u["top_answers"], u["sc_corrects"], f"{u['mode_margin_range']:.1f}", f"{u['mean_distribution_overlap']:.2f}"] for u in unstable]
        ))
    else:
        lines.append("No unstable tasks by top-answer or SC-correct criteria.")
    lines.append("")
    lines.append("## Decision rule")
    if top_stab >= 0.80 and sc_corr_stab >= 0.90:
        lines.append("Preliminary pass: instrument stability is sufficient to proceed to EXP13C, with caveats about unpinned provider/quantization.")
    else:
        lines.append("Preliminary fail: do not proceed to EXP13C until instrument variance is understood or reduced.")
    lines.append("")
    lines.append("## Caveats")
    lines.append("- OpenRouter provider/quantization may be unpinned unless explicit constraints were used.")
    lines.append("- This calibrates the operational stack used, not a pure model in isolation.")
    lines.append("- If exploratory fallback occurred, inspect generations.jsonl failures/retries.")
    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def run(args: argparse.Namespace) -> Path:
    outdir = Path(args.outdir) / f"exp0_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True, exist_ok=True)
    tasks = make_dataset(args.seed, args.n_easy, args.n_medium, args.n_hard)
    rm = ResourceManager()
    resource = rm.openrouter(
        model=args.model,
        policy=args.policy,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        quantizations=args.quantizations.split(",") if args.quantizations else None,
    )

    gen_path = outdir / "generations.jsonl"
    stm_path = outdir / "session_task_metrics.jsonl"
    stability_path = outdir / "stability_metrics.jsonl"

    session_metrics = []
    generation_count = 0

    with gen_path.open("w", encoding="utf-8") as gf, stm_path.open("w", encoding="utf-8") as sf:
        for session_id in range(args.sessions):
            for task in tasks:
                answers = []
                for sample_index in range(args.k):
                    user = f"Solve this arithmetic chain.\n\n{task.prompt}\n\nRemember: final line must be ANSWER <integer>."
                    raw, meta = resource.chat(SYSTEM, user)
                    ans = parse_answer(raw)
                    answers.append(ans)
                    md = meta.to_dict()
                    rec = {
                        "session_id": session_id,
                        "task_id": task.task_id,
                        "difficulty": task.difficulty,
                        "steps": task.steps,
                        "prompt": task.prompt,
                        "ground_truth": task.answer,
                        "sample_index": sample_index,
                        "temperature": args.temperature,
                        "raw_output": raw,
                        "parsed_answer": ans,
                        "is_correct": ans == task.answer,
                        "provider": md.get("provider"),
                        "model": md.get("model"),
                        "policy": md.get("policy"),
                        "latency_s": md.get("latency_s"),
                        "prompt_tokens": md.get("prompt_tokens"),
                        "completion_tokens": md.get("completion_tokens"),
                        "retries": md.get("retries"),
                        "failures": md.get("failures"),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    gf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    generation_count += 1
                m = session_task_metrics(task, session_id, answers, args.temperature)
                session_metrics.append(m)
                sf.write(json.dumps(m, ensure_ascii=False) + "\n")

    grouped = defaultdict(list)
    for m in session_metrics:
        grouped[m["task_id"]].append(m)
    stability_rows = [stability_for_task(rows) for rows in grouped.values()]
    with stability_path.open("w", encoding="utf-8") as f:
        for r in stability_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    write_report(outdir, session_metrics, stability_rows, generation_count)
    print(f"Wrote run to: {outdir}")
    return outdir


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", default="ai-earth-rebuild/runs")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-easy", type=int, default=7)
    p.add_argument("--n-medium", type=int, default=7)
    p.add_argument("--n-hard", type=int, default=6)
    p.add_argument("--sessions", type=int, default=3)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--model", default="meta-llama/llama-3.1-8b-instruct")
    p.add_argument("--policy", choices=["exploratory", "fixed"], default="exploratory")
    p.add_argument("--quantizations", default=None)
    p.add_argument("--max-tokens", type=int, default=220)
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
