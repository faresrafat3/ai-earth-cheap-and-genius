"""
EXP13C-Balanced — balanced early-topology prediction pilot.

Procedure:
1. Generate a pool of tasks with harder step counts.
2. For each task, sample k0=3 answers and classify early topology:
   - early-unanimous
   - early-split-2
   - early-scattered-3
3. Select up to target_per_bin tasks from each bin.
4. Complete selected tasks to k=10 and evaluate SC@10.

Outputs:
  runs/exp13c_balanced_<timestamp>/screening_generations.jsonl
  runs/exp13c_balanced_<timestamp>/selected_generations.jsonl
  runs/exp13c_balanced_<timestamp>/task_metrics.jsonl
  runs/exp13c_balanced_<timestamp>/report.md
"""
from __future__ import annotations

import argparse, json, math, random, re, sys
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
    ops: list[tuple[str,int]]
    start: int


def apply_op(acc:int,op:str,val:int)->int:
    if op=='+': return acc+val
    if op=='-': return acc-val
    if op=='*': return acc*val
    raise ValueError(op)


def make_task(task_id:str, steps:int, rng:random.Random)->Task:
    start=rng.randint(1,9); acc=start; ops=[]
    # Slightly multiplication-heavy to generate harder regimes.
    choices=['+','-','*','*']
    for _ in range(steps):
        op=rng.choice(choices); val=rng.randint(2,9)
        ops.append((op,val)); acc=apply_op(acc,op,val)
    difficulty=f"steps_{steps}"
    prompt='\n'.join([f"START {start}"]+[f"OP {op} {v}" for op,v in ops])
    return Task(task_id,difficulty,steps,prompt,acc,ops,start)


def make_pool(max_pool:int, seed:int, step_options:list[int])->list[Task]:
    rng=random.Random(seed); tasks=[]
    for i in range(max_pool):
        steps=rng.choice(step_options)
        tasks.append(make_task(f"pool_{i:04d}_s{steps}",steps,rng))
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


def entropy(c:Counter[Any])->float:
    n=sum(c.values())
    if not n: return 0.0
    return -sum((v/n)*math.log((v/n)+1e-12) for v in c.values())


def early_bin(answers:list[int|None])->str:
    d=len(Counter(answers))
    if any(a is None for a in answers): return 'parse-risk'
    if d==1: return 'early-unanimous'
    if d==2: return 'early-split-2'
    return 'early-scattered-3'


def majority_answer(answers:list[int|None])->tuple[int|None,bool]:
    c=Counter(answers); maxc=max(c.values()); winners=[a for a,n in c.items() if n==maxc]
    for a in answers:
        if a in winners: return a, len(winners)>1
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
    early=answers[:k0]; full=answers
    ec=Counter(early); fc=Counter(full)
    early_top, early_top_count=ec.most_common(1)[0]
    sc_answer, sc_tie=majority_answer(full)
    correct_count=fc.get(task.answer,0)
    wrong_counts=Counter({a:c for a,c in fc.items() if a!=task.answer})
    if wrong_counts:
        largest_wrong_answer, largest_wrong_count=wrong_counts.most_common(1)[0]
    else:
        largest_wrong_answer, largest_wrong_count=None,0
    return {
        'task_id':task.task_id,'difficulty':task.difficulty,'steps':task.steps,'ground_truth':task.answer,
        'k0':k0,'k':len(full),'early_bin':early_bin(early),
        'early_top_answer':early_top,'early_top_dominance':early_top_count/k0,'early_distinct_count':len(ec),
        'early_entropy':entropy(ec),'early_unanimous':len(ec)==1,'early_parse_failure_count':sum(1 for a in early if a is None),
        'early_correct_count':ec.get(task.answer,0),'early_top_correct':early_top==task.answer,
        'sc10_answer':sc_answer,'sc10_correct':sc_answer==task.answer,'sc10_tie':sc_tie,
        'single_sample_accuracy':correct_count/len(full),'correct_count':correct_count,
        'largest_wrong_answer':largest_wrong_answer,'largest_wrong_count':largest_wrong_count,
        'full_mode_margin':correct_count-largest_wrong_count,'full_wrong_mode_dominance':largest_wrong_count/len(full),
        'full_entropy':entropy(fc),'full_distinct_count':len(fc),'pairwise_error_agreement':pairwise_error_agreement(full,task.answer),
        'early_answers':{str(a):c for a,c in ec.items()},'answers':{str(a):c for a,c in fc.items()}
    }


def pct(x:float)->str: return f"{100*x:.1f}%"

def table(headers, rows):
    out=['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    out += ['| '+' | '.join(map(str,r))+' |' for r in rows]
    return '\n'.join(out)


def summarize(rows):
    if not rows: return {'n':0,'single':0,'sc':0,'entropy':0}
    return {'n':len(rows),'single':sum(r['single_sample_accuracy'] for r in rows)/len(rows),'sc':sum(r['sc10_correct'] for r in rows)/len(rows),'entropy':sum(r['early_entropy'] for r in rows)/len(rows)}


def write_report(outdir:Path, screening_bins:dict[str,int], rows:list[dict[str,Any]], gen_count:int):
    lines=['# EXP13C-Balanced Report','']
    lines.append('Balanced pilot: pre-screen early topology, then complete selected tasks to SC@10.')
    lines.append('')
    lines.append('## Screening pool bins')
    lines.append(table(['bin','count'],[[k,v] for k,v in screening_bins.items()]))
    lines.append('')
    overall=summarize(rows)
    lines.append('## Selected set overall')
    lines.append(table(['selected tasks','selected generations','single','SC@10','mean early entropy'],[[overall['n'],gen_count,pct(overall['single']),pct(overall['sc']),f"{overall['entropy']:.2f}"]]))
    lines.append('')
    groups=defaultdict(list)
    for r in rows: groups[r['early_bin']].append(r)
    lines.append('## By early bin')
    tr=[]
    for b in ['early-unanimous','early-split-2','early-scattered-3','parse-risk']:
        s=summarize(groups[b]); tr.append([b,s['n'],pct(s['single']),pct(s['sc']),f"{s['entropy']:.2f}"])
    lines.append(table(['early bin','n','single','SC@10','early entropy'],tr))
    lines.append('')
    fails=[r for r in rows if not r['sc10_correct']]
    lines.append('## SC@10 failures')
    if fails:
        lines.append(table(['task','steps','truth','early_bin','early_answers','full_answers','full_margin'],[[f['task_id'],f['steps'],f['ground_truth'],f['early_bin'],f['early_answers'],f['answers'],f['full_mode_margin']] for f in fails]))
    else:
        lines.append('No SC@10 failures.')
    lines.append('')
    lines.append('## Readout')
    if groups['early-split-2'] or groups['early-scattered-3']:
        sc_u=summarize(groups['early-unanimous'])['sc']; sc_r=summarize(groups['early-split-2']+groups['early-scattered-3']+groups['parse-risk'])['sc']
        lines.append(f"SC@10 early-unanimous: **{pct(sc_u)}**")
        lines.append(f"SC@10 non-unanimous/risky: **{pct(sc_r)}**")
        if sc_u > sc_r:
            lines.append('Preliminary support: non-unanimous early topology is riskier than early-unanimous.')
        else:
            lines.append('No support: non-unanimous early topology was not riskier in this run.')
    else:
        lines.append('Could not populate non-unanimous bins; model/task regime remains saturated.')
    report='\n'.join(lines)+'\n'
    (outdir/'report.md').write_text(report,encoding='utf-8')
    print(report)


def run(args):
    outdir=Path(args.outdir)/f"exp13c_balanced_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    outdir.mkdir(parents=True,exist_ok=True)
    rm=ResourceManager(); res=rm.openrouter(model=args.model,policy=args.policy,temperature=args.temperature,max_tokens=args.max_tokens,quantizations=args.quantizations.split(',') if args.quantizations else None)
    tasks=make_pool(args.max_pool,args.seed,[int(x) for x in args.step_options.split(',')])
    selected={b:[] for b in ['early-unanimous','early-split-2','early-scattered-3','parse-risk']}
    screening_bins=Counter()
    early_answers_by_task={}
    screen_path=outdir/'screening_generations.jsonl'
    with screen_path.open('w',encoding='utf-8') as sf:
        for task in tasks:
            early=[]
            for sample_index in range(args.k0):
                user=f"Solve this arithmetic chain.\n\n{task.prompt}\n\nRemember: final line must be ANSWER <integer>."
                raw,meta=res.chat(SYSTEM,user); ans=parse_answer(raw); early.append(ans); md=meta.to_dict()
                sf.write(json.dumps({'stage':'screen','task_id':task.task_id,'steps':task.steps,'ground_truth':task.answer,'sample_index':sample_index,'raw_output':raw,'parsed_answer':ans,'is_correct':ans==task.answer,**md,'timestamp':datetime.now(UTC).isoformat()},ensure_ascii=False)+'\n')
            b=early_bin(early); screening_bins[b]+=1; early_answers_by_task[task.task_id]=early
            if len(selected[b])<args.target_per_bin:
                selected[b].append(task)
            if all(len(selected[b])>=args.target_per_bin for b in ['early-unanimous','early-split-2','early-scattered-3']):
                break
    chosen=[]
    for b in ['early-unanimous','early-split-2','early-scattered-3','parse-risk']:
        chosen.extend(selected[b])
    gen_path=outdir/'selected_generations.jsonl'; met_path=outdir/'task_metrics.jsonl'
    rows=[]; gen_count=0
    with gen_path.open('w',encoding='utf-8') as gf, met_path.open('w',encoding='utf-8') as mf:
        for task in chosen:
            answers=list(early_answers_by_task[task.task_id])
            # log early rows into selected file too
            for i,ans in enumerate(answers):
                gf.write(json.dumps({'stage':'selected_early_reused','task_id':task.task_id,'steps':task.steps,'ground_truth':task.answer,'sample_index':i,'parsed_answer':ans,'is_correct':ans==task.answer},ensure_ascii=False)+'\n')
                gen_count+=1
            for sample_index in range(args.k0,args.k):
                user=f"Solve this arithmetic chain.\n\n{task.prompt}\n\nRemember: final line must be ANSWER <integer>."
                raw,meta=res.chat(SYSTEM,user); ans=parse_answer(raw); answers.append(ans); md=meta.to_dict()
                gf.write(json.dumps({'stage':'selected_completion','task_id':task.task_id,'steps':task.steps,'ground_truth':task.answer,'sample_index':sample_index,'raw_output':raw,'parsed_answer':ans,'is_correct':ans==task.answer,**md,'timestamp':datetime.now(UTC).isoformat()},ensure_ascii=False)+'\n')
                gen_count+=1
            m=metrics(task,answers,args.k0); rows.append(m); mf.write(json.dumps(m,ensure_ascii=False)+'\n')
    write_report(outdir,dict(screening_bins),rows,gen_count)
    print(f"Wrote run to: {outdir}")


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--outdir',default='ai-earth-rebuild/runs')
    p.add_argument('--seed',type=int,default=132)
    p.add_argument('--max-pool',type=int,default=150)
    p.add_argument('--target-per-bin',type=int,default=10)
    p.add_argument('--step-options',default='8,11,14,17')
    p.add_argument('--k0',type=int,default=3)
    p.add_argument('--k',type=int,default=10)
    p.add_argument('--temperature',type=float,default=0.7)
    p.add_argument('--model',default='meta-llama/llama-3.1-8b-instruct')
    p.add_argument('--policy',choices=['exploratory','fixed'],default='exploratory')
    p.add_argument('--quantizations',default=None)
    p.add_argument('--max-tokens',type=int,default=220)
    args=p.parse_args(); run(args)

if __name__=='__main__': main()
