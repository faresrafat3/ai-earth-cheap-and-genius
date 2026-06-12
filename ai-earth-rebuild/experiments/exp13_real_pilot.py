"""
EXP13 Phase B — Real-model pilot for Error Topology.

Purpose:
  Test whether mode_margin / wrong-mode dominance separates Self-Consistency
  success from failure on a real LLM.

Default pilot is deliberately small unless overridden:
  n_per_difficulty=15, k=10, temperature=0.7 (preregistered Phase B)

Safety:
  Reads OpenRouter keys from /tmp/ai_earth_keys.env:
    OPENROUTER_KEYS=sk-or-...,sk-or-...
  No secrets are written to the workspace.

Run small smoke:
  python ai-earth-rebuild/experiments/exp13_real_pilot.py --n-per-difficulty 1 --k 2

Run preregistered pilot:
  python ai-earth-rebuild/experiments/exp13_real_pilot.py --n-per-difficulty 15 --k 10
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import requests
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from core.resource_manager import ResourceManager


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
    ops: list[tuple[str, int]] = []
    for _ in range(steps):
        op = rng.choice(["+", "-", "*"])
        val = rng.randint(2, 9)
        ops.append((op, val))
        acc = apply_op(acc, op, val)
    prompt = "\n".join([f"START {start}"] + [f"OP {op} {v}" for op, v in ops])
    return Task(task_id, difficulty, steps, prompt, acc, ops, start)


def make_dataset(n_per_difficulty: int, seed: int) -> list[Task]:
    rng = random.Random(seed)
    tasks: list[Task] = []
    for difficulty, steps in [("easy", 5), ("medium", 8), ("hard", 11)]:
        for i in range(n_per_difficulty):
            tasks.append(make_task(f"{difficulty}_{i:03d}", difficulty, steps, rng))
    return tasks


def load_keys(path: str) -> list[str]:
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r"OPENROUTER_KEYS=(.+)", txt)
    if not m:
        raise RuntimeError("OPENROUTER_KEYS not found")
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


SYSTEM = (
    "You are a precise arithmetic solver. The user gives a START value and OP lines. "
    "Apply operations strictly in order, left-to-right, ignoring normal precedence. "
    "Return the final line exactly as: ANSWER <integer>."
)


class OpenRouterSampler:
    def __init__(self, model: str, key_path: str, temperature: float, max_tokens: int = 220):
        self.keys = load_keys(key_path)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.ki = 0
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.failures: Counter[str] = Counter()

    def complete(self, task_prompt: str) -> tuple[str, dict[str, Any]]:
        user = f"Solve this arithmetic chain.\n\n{task_prompt}\n\nRemember: final line must be ANSWER <integer>."
        last = ""
        for off in range(len(self.keys)):
            key = self.keys[(self.ki + off) % len(self.keys)]
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM},
                            {"role": "user", "content": user},
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                    },
                    timeout=90,
                )
            except Exception as e:
                last = f"EXC {type(e).__name__}"
                self.failures[last] += 1
                continue
            if r.status_code == 200:
                self.ki = (self.ki + off + 1) % len(self.keys)
                self.calls += 1
                data = r.json()
                usage = data.get("usage", {}) or {}
                self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
                self.completion_tokens += int(usage.get("completion_tokens") or 0)
                return data["choices"][0]["message"].get("content") or "", {"usage": usage, "model": self.model}
            last = f"HTTP {r.status_code}"
            self.failures[last] += 1
            if r.status_code not in (401, 402, 429, 500, 502, 503):
                # hard model/config error
                break
            time.sleep(0.2)
        raise RuntimeError(f"all keys failed; last={last}; failures={dict(self.failures)}")


def parse_answer(text: str) -> int | None:
    m = re.search(r"ANSWER[^\-0-9]*(-?\d+)", text, flags=re.I)
    if m:
        try: return int(m.group(1))
        except Exception: return None
    nums = re.findall(r"-?\d+", text)
    if not nums:
        return None
    try:
        return int(nums[-1])
    except Exception:
        return None


def entropy(counts: Counter[Any]) -> float:
    n = sum(counts.values())
    if n == 0: return 0.0
    return -sum((c/n) * math.log((c/n) + 1e-12) for c in counts.values())


def pairwise_error_agreement(answers: list[int | None], correct: int) -> float:
    wrongs = [a for a in answers if a != correct]
    if len(wrongs) < 2: return 0.0
    same = total = 0
    for i in range(len(wrongs)):
        for j in range(i+1, len(wrongs)):
            total += 1
            if wrongs[i] == wrongs[j]: same += 1
    return same / total if total else 0.0


def majority_answer(answers: list[int | None]) -> tuple[int | None, bool]:
    counts = Counter(answers)
    maxc = max(counts.values())
    winners = [a for a, c in counts.items() if c == maxc]
    for a in answers:
        if a in winners:
            return a, len(winners) > 1
    raise RuntimeError("unreachable")


def task_metrics(task: Task, answers: list[int | None], temperature: float) -> dict[str, Any]:
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
        "difficulty": task.difficulty,
        "steps": task.steps,
        "temperature": temperature,
        "k": k,
        "ground_truth": task.answer,
        "correct_count": correct_count,
        "largest_wrong_answer": largest_wrong_answer,
        "largest_wrong_count": largest_wrong_count,
        "mode_margin": correct_count - largest_wrong_count,
        "wrong_mode_dominance": largest_wrong_count / k,
        "distinct_answer_count": len(counts),
        "answer_entropy": entropy(counts),
        "pairwise_error_agreement": pairwise_error_agreement(answers, task.answer),
        "sc_answer": sc_answer,
        "sc_correct": sc_answer == task.answer,
        "sc_tie": sc_tie,
        "single_sample_accuracy": correct_count / k,
        "answers": {str(a): c for a, c in counts.items()},
    }


def mean(xs: list[float]) -> float:
    return sum(xs)/len(xs) if xs else 0.0


def pct(x: float) -> str:
    return f"{100*x:.1f}%"


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {"n":0,"single_acc":0,"sc_acc":0,"sc_gain":0,"margin":0,"wrong_dom":0,"entropy":0,"err_agree":0}
    single = mean([r["single_sample_accuracy"] for r in rows])
    sc = mean([1.0 if r["sc_correct"] else 0.0 for r in rows])
    return {
        "n": len(rows), "single_acc": single, "sc_acc": sc, "sc_gain": sc-single,
        "margin": mean([r["mode_margin"] for r in rows]),
        "wrong_dom": mean([r["wrong_mode_dominance"] for r in rows]),
        "entropy": mean([r["answer_entropy"] for r in rows]),
        "err_agree": mean([r["pairwise_error_agreement"] for r in rows]),
    }


def margin_bin(r: dict[str, Any]) -> str:
    if r["mode_margin"] > 0: return "margin > 0"
    if r["mode_margin"] == 0: return "margin = 0"
    return "margin < 0"


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"]*len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(map(str, row)) + " |")
    return "\n".join(out)


def make_report(rows: list[dict[str, Any]], sampler: OpenRouterSampler, outdir: Path) -> None:
    lines: list[str] = []
    lines.append("# EXP13 Phase B Real Pilot Report")
    lines.append("")
    lines.append("**Status:** real-model pilot. Exploratory unless run with preregistered full settings.")
    lines.append("")
    overall = summarize(rows)
    lines.append("## Overall")
    lines.append(table(["n tasks", "single", "SC", "gain", "margin", "wrong_dom", "entropy", "err_agree"], [[
        overall["n"], pct(overall["single_acc"]), pct(overall["sc_acc"]), pct(overall["sc_gain"]),
        f'{overall["margin"]:.2f}', f'{overall["wrong_dom"]:.2f}', f'{overall["entropy"]:.2f}', f'{overall["err_agree"]:.2f}'
    ]]))
    lines.append("")
    for label, key in [("Difficulty", "difficulty")]:
        grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for r in rows: grouped[r[key]].append(r)
        lines.append(f"## By {label}")
        rows2=[]
        for g in sorted(grouped):
            s=summarize(grouped[g])
            rows2.append([g, s["n"], pct(s["single_acc"]), pct(s["sc_acc"]), pct(s["sc_gain"]), f'{s["margin"]:.2f}', f'{s["wrong_dom"]:.2f}'])
        lines.append(table([label.lower(),"n","single","SC","gain","margin","wrong_dom"], rows2))
        lines.append("")
    grouped2: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows: grouped2[margin_bin(r)].append(r)
    lines.append("## By mode-margin bin")
    rows3=[]
    for b in ["margin > 0", "margin = 0", "margin < 0"]:
        s=summarize(grouped2[b])
        rows3.append([b, s["n"], pct(s["single_acc"]), pct(s["sc_acc"]), pct(s["sc_gain"]), f'{s["wrong_dom"]:.2f}', f'{s["err_agree"]:.2f}'])
    lines.append(table(["bin","n","single","SC","gain","wrong_dom","err_agree"], rows3))
    lines.append("")
    pos=summarize(grouped2["margin > 0"])
    non=summarize(grouped2["margin = 0"]+grouped2["margin < 0"])
    lines.append("## Preregistered readout")
    lines.append(f"SC accuracy margin > 0: **{pct(pos['sc_acc'])}** (n={pos['n']})")
    lines.append(f"SC accuracy margin <= 0: **{pct(non['sc_acc'])}** (n={non['n']})")
    lines.append(f"Difference: **{pct(pos['sc_acc']-non['sc_acc'])}**")
    lines.append("")
    lines.append("## Usage")
    lines.append("calls: recorded per-generation in `generations.jsonl`")
    lines.append("prompt_tokens/completion_tokens: recorded per-generation in `generations.jsonl`")
    lines.append("latency/retries/failures: recorded per-generation in `generations.jsonl`")
    lines.append("")
    lines.append("## Limitations")
    lines.append("- Provider/quantization are not pinned; treat this as pilot evidence only.")
    lines.append("- Prompt sensitivity not swept.")
    lines.append("- Small n if smoke settings used.")
    out = "\n".join(lines) + "\n"
    (outdir/"report.md").write_text(out, encoding="utf-8")
    print(out)


def run(args: argparse.Namespace) -> Path:
    outdir = Path(args.outdir) / f"exp13_real_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True, exist_ok=True)
    tasks = make_dataset(args.n_per_difficulty, args.seed)
    rm = ResourceManager()
    sampler = rm.openrouter(model=args.model, policy=args.policy, temperature=args.temperature, max_tokens=args.max_tokens, quantizations=args.quantizations.split(",") if args.quantizations else None)
    gen_path = outdir/"generations.jsonl"
    metrics_path = outdir/"task_metrics.jsonl"
    all_metrics=[]
    with gen_path.open("w", encoding="utf-8") as gf, metrics_path.open("w", encoding="utf-8") as mf:
        for task in tasks:
            answers=[]
            for sample_index in range(args.k):
                raw, call_meta = sampler.chat(SYSTEM, f"Solve this arithmetic chain.\n\n{task.prompt}\n\nRemember: final line must be ANSWER <integer>.")
                ans = parse_answer(raw)
                answers.append(ans)
                meta_dict = call_meta.to_dict()
                rec = {
                    "task_id": task.task_id, "difficulty": task.difficulty, "steps": task.steps,
                    "prompt": task.prompt, "ground_truth": task.answer,
                    "sample_index": sample_index, "temperature": args.temperature,
                    "raw_output": raw, "parsed_answer": ans, "is_correct": ans == task.answer,
                    "model": args.model, "provider": "openrouter-unpinned",
                    "prompt_tokens": meta_dict.get("prompt_tokens", 0),
                    "completion_tokens": meta_dict.get("completion_tokens", 0),
                    "latency_s": meta_dict.get("latency_s", 0),
                    "policy": meta_dict.get("policy"),
                    "retries": meta_dict.get("retries", 0),
                    "failures": meta_dict.get("failures"),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                gf.write(json.dumps(rec, ensure_ascii=False)+"\n")
            m = task_metrics(task, answers, args.temperature)
            all_metrics.append(m)
            mf.write(json.dumps(m, ensure_ascii=False)+"\n")
    make_report(all_metrics, sampler, outdir)
    print(f"Wrote run to: {outdir}")
    return outdir


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--outdir", default="ai-earth-rebuild/runs")
    p.add_argument("--key-path", default="/tmp/ai_earth_keys.env")
    p.add_argument("--model", default="meta-llama/llama-3.1-8b-instruct")
    p.add_argument("--seed", type=int, default=130)
    p.add_argument("--n-per-difficulty", type=int, default=15)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max-tokens", type=int, default=220)
    p.add_argument("--policy", choices=["exploratory", "fixed"], default="exploratory")
    p.add_argument("--quantizations", default=None, help="Comma-separated OpenRouter quantizations, e.g. fp16,bf16")
    args=p.parse_args()
    run(args)

if __name__ == "__main__":
    main()
