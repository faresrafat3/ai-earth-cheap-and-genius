"""
EXP13C — Early Topology Prediction.

Question:
  Can topology from the first k0=3 samples predict SC@10 outcome?

Outputs:
  runs/exp13c_<timestamp>/generations.jsonl
  runs/exp13c_<timestamp>/task_metrics.jsonl
  runs/exp13c_<timestamp>/report.md
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
    ops=[]
    for _ in range(steps):
        op = rng.choice(["+", "-", "*"])
        val = rng.randint(2, 9)
        ops.append((op,val))
        acc = apply_op(acc,op,val)
    prompt="\n".join([f"START {start}"]+[f"OP {op} {v}" for op,v in ops])
    return Task(task_id,difficulty,steps,prompt,acc,ops,start)


def make_dataset(seed:int,n_easy:int,n_medium:int,n_hard:int)->list[Task]:
    rng=random.Random(seed)
    tasks=[]
    for difficulty,steps,n in [("easy",5,n_easy),("medium",8,n_medium),("hard",11,n_hard)]:
        for i in range(n):
            tasks.append(make_task(f"{difficulty}_{i:03d}",difficulty,steps,rng))
    return tasks


def parse_answer(text:str)->int|None:
    m=re.search(r"ANSWER[^\-0-9]*(-?\d+)",text,re.I)
    if m:
        try: return int(m.group(1))
        except: return None
    nums=re.findall(r"-?\d+",text)
    if not nums: return None
    try: return int(nums[-1])
    except: return None


def entropy(counts:Counter[Any])->float:
    n=sum(counts.values())
    if n==0: return 0.0
    return -sum((c/n)*math.log((c/n)+1e-12) for c in counts.values())


def majority_answer(answers:list[int|None])->tuple[int|None,bool]:
    c=Counter(answers)
    maxc=max(c.values())
    winners=[a for a,n in c.items() if n==maxc]
    for a in answers:
        if a in winners:
            return a, len(winners)>1
    raise RuntimeError('unreachable')


def pairwise_error_agreement(answers:list[int|None],truth:int)->float:
    wrong=[a for a in answers if a!=truth]
    if len(wrong)<2: return 0.0
    same=total=0
    for i in range(len(wrong)):
        for j in range(i+1,len(wrong)):
            total+=1; same+=int(wrong[i]==wrong[j])
    return same/total if total else 0.0


def metrics(task:Task, answers:list[int|None], k0:int)->dict[str,Any]:
    early=answers[:k0]
    full=answers
    ec=Counter(early)
    fc=Counter(full)
    early_top, early_top_count = ec.most_common(1)[0]
    sc_answer, sc_tie = majority_answer(full)
    correct_count=fc.get(task.answer,0)
    wrong_counts=Counter({a:c for a,c in fc.items() if a!=task.answer})
    if wrong_counts:
        largest_wrong_answer, largest_wrong_count=wrong_counts.most_common(1)[0]
    else:
        largest_wrong_answer, largest_wrong_count=None,0
    return {
        "task_id":task.task_id,
        "difficulty":task.difficulty,
        "steps":task.steps,
        "ground_truth":task.answer,
        "k0":k0,
        "k":len(full),
        # Early predictors without ground truth
        "early_top_answer":early_top,
        "early_top_dominance":early_top_count/k0,
        "early_distinct_count":len(ec),
        "early_entropy":entropy(ec),
        "early_unanimous":len(ec)==1,
        "early_parse_failure_count":sum(1 for a in early if a is None),
        # Diagnostic-only early fields with ground truth
        "early_correct_count":ec.get(task.answer,0),
        "early_top_correct":early_top==task.answer,
        # Outcome
        "sc10_answer":sc_answer,
        "sc10_correct":sc_answer==task.answer,
        "sc10_tie":sc_tie,
        "single_sample_accuracy":correct_count/len(full),
        "correct_count":correct_count,
        "largest_wrong_answer":largest_wrong_answer,
        "largest_wrong_count":largest_wrong_count,
        "full_mode_margin":correct_count-largest_wrong_count,
        "full_wrong_mode_dominance":largest_wrong_count/len(full),
        "full_entropy":entropy(fc),
        "full_distinct_count":len(fc),
        "pairwise_error_agreement":pairwise_error_agreement(full,task.answer),
        "answers":{str(a):c for a,c in fc.items()},
        "early_answers":{str(a):c for a,c in ec.items()},
    }


def pct(x:float)->str: return f"{100*x:.1f}%"

def table(headers:list[str], rows:list[list[Any]])->str:
    out=["| "+" | ".join(headers)+" |","|"+"|".join(["---"]*len(headers))+"|"]
    out += ["| "+" | ".join(map(str,r))+" |" for r in rows]
    return "\n".join(out)


def summarize(rows:list[dict[str,Any]])->dict[str,float]:
    if not rows: return {"n":0,"sc":0,"single":0,"early_unanimous":0,"early_entropy":0}
    return {
        "n":len(rows),
        "sc":sum(r['sc10_correct'] for r in rows)/len(rows),
        "single":sum(r['single_sample_accuracy'] for r in rows)/len(rows),
        "early_unanimous":sum(r['early_unanimous'] for r in rows)/len(rows),
        "early_entropy":sum(r['early_entropy'] for r in rows)/len(rows),
    }


def risk_bin(r:dict[str,Any])->str:
    # Practical predictor without ground truth.
    if r['early_parse_failure_count']>0:
        return 'parse-risk'
    if r['early_unanimous']:
        return 'early-unanimous'
    if r['early_distinct_count']==2:
        return 'early-split-2'
    return 'early-scattered-3'


def write_report(outdir:Path, rows:list[dict[str,Any]], gen_count:int)->None:
    lines=[]
    lines.append('# EXP13C Early Topology Prediction Report')
    lines.append('')
    lines.append('Question: can first k0 samples predict SC@10 outcome?')
    lines.append('')
    overall=summarize(rows)
    lines.append('## Overall')
    lines.append(table(['tasks','generations','single','SC@10','early unanimous','mean early entropy'],[[overall['n'],gen_count,pct(overall['single']),pct(overall['sc']),pct(overall['early_unanimous']),f"{overall['early_entropy']:.2f}"]]))
    lines.append('')
    # By difficulty
    groups=defaultdict(list)
    for r in rows: groups[r['difficulty']].append(r)
    lines.append('## By difficulty')
    tr=[]
    for g in sorted(groups):
        s=summarize(groups[g]); tr.append([g,s['n'],pct(s['single']),pct(s['sc']),pct(s['early_unanimous']),f"{s['early_entropy']:.2f}"])
    lines.append(table(['difficulty','n','single','SC@10','early unanimous','early entropy'],tr))
    lines.append('')
    # By risk bin
    rb=defaultdict(list)
    for r in rows: rb[risk_bin(r)].append(r)
    lines.append('## By early topology bin (no ground truth)')
    tr=[]
    for b in ['early-unanimous','early-split-2','early-scattered-3','parse-risk']:
        s=summarize(rb[b]); tr.append([b,s['n'],pct(s['single']),pct(s['sc']),pct(s['early_unanimous']),f"{s['early_entropy']:.2f}"])
    lines.append(table(['early bin','n','single','SC@10','unanimous','entropy'],tr))
    lines.append('')
    # Diagnostic with ground truth
    lines.append('## Diagnostic: early top correct vs SC@10')
    eg=defaultdict(list)
    for r in rows: eg['early_top_correct' if r['early_top_correct'] else 'early_top_wrong'].append(r)
    tr=[]
    for b in ['early_top_correct','early_top_wrong']:
        s=summarize(eg[b]); tr.append([b,s['n'],pct(s['single']),pct(s['sc'])])
    lines.append(table(['bin','n','single','SC@10'],tr))
    lines.append('')
    # Failures
    fails=[r for r in rows if not r['sc10_correct']]
    lines.append('## SC@10 failures')
    if fails:
        lines.append(table(['task','difficulty','truth','early_answers','full_answers','early_bin','full_margin'],[[f['task_id'],f['difficulty'],f['ground_truth'],f['early_answers'],f['answers'],risk_bin(f),f['full_mode_margin']] for f in fails]))
    else:
        lines.append('No SC@10 failures.')
    lines.append('')
    # Readout
    lines.append('## Readout')
    if len(fails)==0:
        lines.append('No failures occurred; this run cannot strongly test prediction. It only shows SC@10 is saturated on this task set.')
    elif summarize(rb['early-unanimous'])['sc'] > summarize(rb['early-scattered-3'])['sc']:
        lines.append('Preliminary pattern: early topology separates some SC@10 outcomes.')
    else:
        lines.append('No clear early-topology separation found in this pilot.')
    (outdir/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))


def run(args:argparse.Namespace)->Path:
    outdir=Path(args.outdir)/f"exp13c_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True,exist_ok=True)
    tasks=make_dataset(args.seed,args.n_easy,args.n_medium,args.n_hard)
    rm=ResourceManager()
    res=rm.openrouter(model=args.model,policy=args.policy,temperature=args.temperature,max_tokens=args.max_tokens,quantizations=args.quantizations.split(',') if args.quantizations else None)
    gen_path=outdir/'generations.jsonl'
    met_path=outdir/'task_metrics.jsonl'
    rows=[]; gen_count=0
    with gen_path.open('w',encoding='utf-8') as gf, met_path.open('w',encoding='utf-8') as mf:
        for task in tasks:
            answers=[]
            for sample_index in range(args.k):
                user=f"Solve this arithmetic chain.\n\n{task.prompt}\n\nRemember: final line must be ANSWER <integer>."
                raw,meta=res.chat(SYSTEM,user)
                ans=parse_answer(raw); answers.append(ans); md=meta.to_dict()
                gf.write(json.dumps({
                    'task_id':task.task_id,'difficulty':task.difficulty,'steps':task.steps,'prompt':task.prompt,'ground_truth':task.answer,
                    'sample_index':sample_index,'phase':'early' if sample_index<args.k0 else 'late','temperature':args.temperature,
                    'raw_output':raw,'parsed_answer':ans,'is_correct':ans==task.answer,
                    **md,'timestamp':datetime.now(UTC).isoformat()
                },ensure_ascii=False)+'\n')
                gen_count+=1
            m=metrics(task,answers,args.k0); rows.append(m); mf.write(json.dumps(m,ensure_ascii=False)+'\n')
    write_report(outdir,rows,gen_count)
    print(f"Wrote run to: {outdir}")
    return outdir


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--outdir',default='ai-earth-rebuild/runs')
    p.add_argument('--seed',type=int,default=131)
    p.add_argument('--n-easy',type=int,default=7)
    p.add_argument('--n-medium',type=int,default=7)
    p.add_argument('--n-hard',type=int,default=6)
    p.add_argument('--k0',type=int,default=3)
    p.add_argument('--k',type=int,default=10)
    p.add_argument('--temperature',type=float,default=0.7)
    p.add_argument('--model',default='meta-llama/llama-3.1-8b-instruct')
    p.add_argument('--policy',choices=['exploratory','fixed'],default='exploratory')
    p.add_argument('--quantizations',default=None)
    p.add_argument('--max-tokens',type=int,default=220)
    args=p.parse_args(); run(args)

if __name__=='__main__': main()
