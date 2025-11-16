import argparse, math
from active_sboxes import min_active_for_rounds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-threshold", type=int, default=2,
                    help="probability threshold base b, default 2 (i.e., 2^-exp)")
    ap.add_argument("--p-exp", type=int, default=16,
                    help="probability threshold exponent (2^-exp)")
    ap.add_argument("--pmax", type=float, default=None,
                    help="override S-box max differential probability (default computed from DDT of PRESENT S-box = 0.25)")
    ap.add_argument("--rmax", type=int, default=12)
    args = ap.parse_args()

    # DP budget in terms of active S-boxes: w_max = floor( -log(threshold) / -log(pmax) )
    p_threshold = (args.p-threshold if False else math.pow(args.p_threshold, -args.p_exp))  # keep for clarity
    # p_threshold = 2^-exp
    exp_t = args.p_exp * math.log(args.p_threshold, 2)

    pmax = args.pmax if args.pmax is not None else 0.25
    exp_per_active = -math.log(pmax, 2)  # e.g., 2.0 if pmax=1/4
    w_max = math.floor(exp_t / exp_per_active + 1e-9)
    print(f"Probability threshold = 2^-{args.p_exp}; pmax={pmax}; active budget w_max={w_max}")

    best_R = 0
    for r in range(1, args.rmax+1):
        total, per_round = min_active_for_rounds(r)
        if total <= w_max:
            best_R = r
            print(f"R={r}: feasible (min total actives={total} <= {w_max})")
        else:
            print(f"R={r}: infeasible (min total actives={total} > {w_max})")
            break
    print(f"[RESULT] Longest rounds satisfying threshold: R={best_R}")

if __name__ == "__main__":
    main()
