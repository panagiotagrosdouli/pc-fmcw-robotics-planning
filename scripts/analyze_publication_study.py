#!/usr/bin/env python3
"""Publication analysis: paired inference, oracle gap, and summary tables."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from iscai.evaluation.research_analysis import (
    paired_effects,
    scenario_paired_effects,
    value_of_information,
    reliability_mobility_pareto,
    feasibility_diagnostics,
    prediction_break_even,
)


def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--output-dir',required=True); p.add_argument('--bootstrap-samples',type=int,default=10000); p.add_argument('--rng-seed',type=int,default=2026); return p.parse_args()


def main():
    a=parse_args(); frame=pd.read_csv(a.input); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    effects=paired_effects(frame,bootstrap_samples=a.bootstrap_samples,rng=a.rng_seed); scenario=scenario_paired_effects(frame,bootstrap_samples=a.bootstrap_samples,rng=a.rng_seed)
    effects.to_csv(out/'paired_effects.csv',index=False); scenario.to_csv(out/'scenario_paired_effects.csv',index=False)
    value_of_information(frame).to_csv(out/'oracle_information_ladder.csv',index=False)
    reliability_mobility_pareto(frame).to_csv(out/'reliability_mobility_pareto.csv',index=False)
    feasibility_diagnostics(frame).to_csv(out/'feasibility_diagnostics.csv',index=False)
    prediction_break_even(effects).to_csv(out/'prediction_break_even.csv',index=False)
    core=frame[frame.experiment=='core']
    metrics=['mean_snr_db','min_snr_db','mean_outage_probability','mean_ber_model','mean_goodput_bps_model','path_length_m','progress_m','min_target_distance_m','min_static_obstacle_clearance_m','collision_indicator','min_realized_ttc_s','no_candidate_rate']
    rows=[]
    for planner,g in core.groupby('planner'):
        row={'planner':planner,'n_episodes':len(g)}
        for m in metrics:
            if m in g: row[m]=g[m].replace([float('inf'),float('-inf')],pd.NA).mean(skipna=True)
        rows.append(row)
    pd.DataFrame(rows).to_csv(out/'core_planner_summary.csv',index=False)
    print(f'wrote publication analysis tables to {out}')

if __name__=='__main__': main()
