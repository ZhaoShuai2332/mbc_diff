# Orchestrate the three problems end-to-end
import subprocess, json, os, math, sys

def run(cmd):
    print("+", cmd)
    sys.stdout.flush()
    subprocess.check_call(cmd, shell=True)

def main():
    # Q1
    run("python milp/run_active_range.py --start 1 --end 10 --out data_active.csv")
    # Q2
    run("python milp/longest_threshold.py --p-threshold 2 --p-exp 16 --rmax 10")
    # Example: search for R=4
    run("python diffsearch/bfs_search.py --rounds 4 --save best_r4.json")
    run("python verify/monte_carlo.py --rounds 4 --path best_r4.json --trials 262144")

if __name__ == '__main__':
    main()
