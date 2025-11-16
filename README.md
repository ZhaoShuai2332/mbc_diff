# MBC16 Differential Analysis Project

This project solves the three assignment problems for an SPN cipher "MBC" with **16‑bit block**, **4 parallel 4‑bit S‑boxes**, and the bit permutation shown in your slides.

> Problems
> 1) Lower bound of the number of **active S‑boxes** for 1..10 rounds.  
> 2) Search differential characteristics whose probability is **>= 2^-16** and find the **longest** number of rounds; verify by Monte‑Carlo.  
> 3) Study whether the **max‑probability** characteristic always uses the **minimum number of active S‑boxes**.

The code contains two engines:
- **MILP (CBC via PuLP)** for lower‑bound of active S‑boxes (no license needed).
- **Exact DDT enumeration** for real probabilities and characteristics.
- **Monte‑Carlo** simulator for verification.

## Quick start

```bash
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt

# Q1: lower bound for 1..10 rounds -> data/active_1_10.csv
python milp/run_active_range.py --start 1 --end 10

# Q2: longest rounds with prob >= 2^-16 (pmax from S-box DDT)
python milp/longest_threshold.py --p-threshold 2 --p-exp 16 --rmax 12

# Search best characteristic for a fixed round (default R from previous step)
python diffsearch/bfs_search.py --rounds 4 --save best_r4.json

# Verify the found char by Monte Carlo
python verify/monte_carlo.py --rounds 4 --path best_r4.json --trials 262144
```

## Files

- `mbc/sbox.py`: 4‑bit S‑box (default PRESENT S‑box) + DDT builder.
- `mbc/perm.py`: 16‑bit bit permutation from the slide: [1..16] -> [1,5,9,13,2,6,10,14,3,7,11,15,4,8,12,16].
- `mbc/cipher.py`: simple SPN encrypt for simulation (S -> P -> AddRoundKey each round).
- `milp/active_sboxes.py`: MILP model for minimal active boxes for **one** round count.
- `milp/run_active_range.py`: loop 1..N and writes CSV.
- `milp/longest_threshold.py`: find the longest round where min‑active <= budget derived from probability threshold (uses S‑box p_max from DDT).
- `diffsearch/bfs_search.py`: exact enumeration search of best differential characteristic and probability for small rounds.
- `verify/monte_carlo.py`: simulation to estimate the probability of a characteristic.
- `scripts/run_all.py`: reproducible pipeline for report.

All modules are **pure Python** and require only open‑source packages.
