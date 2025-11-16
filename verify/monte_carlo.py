import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse, json, random, math, tqdm
from mbc.cipher import encrypt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, required=False, help="if omitted, read from JSON 'rounds'")
    ap.add_argument("--path", required=True, help="best.json from bfs_search")
    ap.add_argument("--trials", type=int, default=1<<18)
    args = ap.parse_args()

    data = json.load(open(args.path))
    delta_in  = data["path"][0]["in"]
    delta_out = data["path"][-1].get("sout", data["path"][-1].get("pout", 0)) if len(data["path"])>1 else 0
    rounds = args.rounds if args.rounds is not None else int(data.get("rounds", 0))
    if rounds <= 0:
        raise SystemExit("--rounds not provided and JSON lacks 'rounds'")

    N = args.trials
    hit = 0
    for _ in tqdm.trange(N):
        p0 = random.getrandbits(16)
        p1 = p0 ^ delta_in
        k  = random.getrandbits(16)
        c0 = encrypt(p0, k, rounds)
        c1 = encrypt(p1, k, rounds)
        if (c0 ^ c1) == delta_out:
            hit += 1

    phat = hit / N
    neglog = -math.log(phat, 2) if phat>0 else float("inf")
    print(f"[MC] hit={hit}/{N}, p≈{phat:.3e}, -log2≈{neglog:.2f}")
    if "prob" in data:
        print(f"[Ref] theory p≈{data['prob']:.3e}, -log2≈{-math.log(data['prob'],2):.2f}")

if __name__ == "__main__":
    main()
