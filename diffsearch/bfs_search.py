import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse, json, math
from typing import Dict, Tuple, List
from mbc.sbox import SBOX, DDT, sbox_pmax
from mbc.perm import permute_bits

def popcount16(x: int) -> int:
    return bin(x & 0xFFFF).count("1")

def nibble(x: int, j: int) -> int:
    return (x >> (4*j)) & 0xF

def apply_s_prob(diff_in: int) -> List[Tuple[int, float, int]]:
    """
    Enumerate all possible S-layer output differences for 4 S-boxes, with probability.
    Returns list of tuples (diff_out_16bit, prob, actives_this_round)
    """
    # For each nibble, get mapping options (beta, prob)
    options = []
    actives = 0
    for j in range(4):
        a = nibble(diff_in, j)
        if a == 0:
            options.append([(0, 1.0)])
        else:
            actives += 1
            row = []
            for b in range(16):
                cnt = DDT[a][b]
                if cnt == 0: 
                    continue
                if b == 0:  # for bijective S, should not happen for a!=0
                    continue
                row.append((b, cnt/16.0))
            options.append(row)
    # combine 4 nibbles
    outs = []
    def dfs(idx, cur_val, cur_p):
        if idx == 4:
            outs.append((cur_val, cur_p, actives))
            return
        for b, p in options[idx]:
            dfs(idx+1, cur_val | (b << (4*idx)), cur_p * p)
    dfs(0, 0, 1.0)
    return outs

def best_characteristic(rounds: int, init_mode: str = "one_nibble") -> Dict:
    """Search the best prob characteristic for R rounds.
    init_mode: 'one_nibble' -> try all positions and all nonzero 4-bit values for single nibble
    """
    best = {"prob": 0.0}
    starts = []
    if init_mode == "one_nibble":
        for j in range(4):
            for a in range(1,16):
                starts.append(a << (4*j))
    else:
        for x in range(1, 1<<16):
            starts.append(x)

    pmax = sbox_pmax()
    for d0 in starts:
        # DFS over rounds
        def dfs(r, diff, prob_acc, actives_acc, path):
            nonlocal best
            if r == rounds:
                if prob_acc > best["prob"]:
                    best = {"prob": prob_acc, "path": path[:], "actives": actives_acc}
                return
            for s_out, p, act in apply_s_prob(diff):
                next_diff = permute_bits(s_out)
                remaining = rounds - (r+1)
                ub = prob_acc * p * (pmax ** remaining)
                if ub <= best["prob"]:
                    continue
                path.append({"round": r+1, "in": diff, "sout": s_out, "pout": next_diff, "act": act, "p": p})
                dfs(r+1, next_diff, prob_acc * p, actives_acc + act, path)
                path.pop()
        dfs(0, d0, 1.0, 0, [{"round": 0, "in": d0}])
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int)
    ap.add_argument("--rmin", type=int)
    ap.add_argument("--rmax", type=int)
    ap.add_argument("--init", choices=["one_nibble", "all"], default="one_nibble")
    ap.add_argument("--save", default="best.json")
    ap.add_argument("--save-dir", default="best_runs")
    args = ap.parse_args()

    if args.rounds and not (args.rmin or args.rmax):
        res = best_characteristic(args.rounds, args.init)
        res["neglog2p"] = -math.log(res["prob"], 2) if res["prob"]>0 else 999
        with open(args.save, "w") as f:
            json.dump(res, f, indent=2)
        print(f"[+] Best characteristic for R={args.rounds}: p={res['prob']:.3e}, -log2={res['neglog2p']:.2f}, actives={res['actives']}")
        print(f"    Saved to {args.save}")
        return

    rmin = args.rmin if args.rmin is not None else 1
    rmax = args.rmax if args.rmax is not None else rmin
    os.makedirs(args.save_dir, exist_ok=True)

    grid_all = []
    best_overall = None
    for r in range(rmin, rmax+1):
        res = best_characteristic(r, args.init)
        res["neglog2p"] = -math.log(res["prob"], 2) if res["prob"]>0 else 999
        save_path = os.path.join(args.save_dir, f"best_R{r}.json")
        with open(save_path, "w") as f:
            json.dump(res, f, indent=2)
        print(f"[+] R={r}: p={res['prob']:.3e}, -log2={res['neglog2p']:.2f}, actives={res['actives']} -> {save_path}")
        grid_all.append({
            "rounds": r,
            "prob": res["prob"],
            "neglog2p": res["neglog2p"],
            "actives": res["actives"],
            "path_file": save_path
        })
        if best_overall is None or res["prob"] > best_overall["prob"]:
            best_overall = {"rounds": r, **res, "path_file": save_path}

    grid_all_path = os.path.join(args.save_dir, "grid_all.json")
    with open(grid_all_path, "w") as f:
        json.dump(grid_all, f, indent=2)
    if best_overall:
        grid_best_path = os.path.join(args.save_dir, "grid_best.json")
        with open(grid_best_path, "w") as f:
            json.dump(best_overall, f, indent=2)
        print(f"[RESULT] Best overall: R={best_overall['rounds']}, p={best_overall['prob']:.3e}, -log2={best_overall['neglog2p']:.2f}, actives={best_overall['actives']}")
        print(f"          Saved grid to {grid_all_path}, best to {grid_best_path}")

if __name__ == "__main__":
    main()
