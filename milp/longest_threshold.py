import argparse, math, csv
from active_sboxes import min_active_for_rounds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-threshold", type=int, default=2)
    ap.add_argument("--p-exp", type=int, default=16)
    ap.add_argument("--pmax", type=float, default=None)
    ap.add_argument("--rmin", type=int, default=1)
    ap.add_argument("--rmax", type=int, default=12)
    ap.add_argument("--out", default="longest_threshold.csv")
    args = ap.parse_args()

    pt_val = math.pow(args.p_threshold, -args.p_exp)
    exp_t = args.p_exp * math.log(args.p_threshold, 2)
    pmax = args.pmax if args.pmax is not None else 0.25
    exp_pa = -math.log(pmax, 2)
    w_max = math.floor(exp_t / exp_pa + 1e-9)
    print(f"threshold=2^-{args.p_exp} ({pt_val:.3e}); pmax={pmax}; w_max={w_max}")

    rows = [("round", "min_total_actives", "feasible")]
    best_R = 0
    for r in range(args.rmin, args.rmax+1):
        total, per_round = min_active_for_rounds(r)
        feas = total <= w_max
        if feas:
            best_R = r
            print(f"R={r}: feasible; min_total={total} <= {w_max}")
        else:
            print(f"R={r}: infeasible; min_total={total} > {w_max}")
            rows.append((r, total, int(feas)))
            break
        rows.append((r, total, int(feas)))

    with open(args.out, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"[RESULT] longest_R={best_R}; saved={args.out}")

if __name__ == "__main__":
    main()
