import argparse, csv
from active_sboxes import min_active_for_rounds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=10)
    ap.add_argument("--out", default="data_active.csv")
    args = ap.parse_args()

    rows = [("round", "active_sboxes")]
    for r in range(args.start, args.end+1):
        total, per_round = min_active_for_rounds(r)
        rows.append((r, per_round[-1] if per_round else 0))  # report last round actives
        print(f"R={r}: min total actives = {total}; per-round={per_round}")
    with open(args.out, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"[+] CSV written to {args.out}")

if __name__ == "__main__":
    main()
