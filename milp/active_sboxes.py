# MILP model (PuLP+CBC) for minimal number of active S-boxes
from typing import List, Tuple
import pulp
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mbc.sbox import DDT

# nibble index 0..3; each nibble has 4 bits -> bit indices in 0..15
def nibble_bits(j: int) -> List[int]:
    return [4*j + k for k in range(4)]

# permutation for 16-bit
PBOX = [(i % 4)*4 + (i // 4) for i in range(16)]

def _branch_number() -> int:
    bmin = 16
    for a in range(1,16):
        for b in range(1,16):
            if DDT[a][b] > 0:
                w = bin(a).count("1") + bin(b).count("1")
                if w < bmin:
                    bmin = w
    return bmin

BRANCH = _branch_number()

def min_active_for_rounds(rounds: int) -> Tuple[int, List[int]]:
    # Variables:
    # x[r][i] : bit at S-input of round r (0..rounds-1), 16 bits
    # y[r][i] : bit at S-output of round r, 16 bits
    # a[r][j] : if nibble j is active at round r (S-input non-zero)
    prob = pulp.LpProblem("mbc_min_active", pulp.LpMinimize)

    x = [[pulp.LpVariable(f"x_{r}_{i}", lowBound=0, upBound=1, cat=pulp.LpBinary)
          for i in range(16)] for r in range(rounds)]
    y = [[pulp.LpVariable(f"y_{r}_{i}", lowBound=0, upBound=1, cat=pulp.LpBinary)
          for i in range(16)] for r in range(rounds)]
    a = [[pulp.LpVariable(f"a_{r}_{j}", lowBound=0, upBound=1, cat=pulp.LpBinary)
          for j in range(4)] for r in range(rounds)]

    # a[r][j] is OR of x[r] nibble bits
    for r in range(rounds):
        for j in range(4):
            bits = nibble_bits(j)
            for b in bits:
                prob += x[r][b] <= a[r][j]
            prob += pulp.lpSum(x[r][b] for b in bits) >= a[r][j]
            for b in bits:
                prob += y[r][b] <= a[r][j]
            prob += pulp.lpSum(y[r][b] for b in bits) >= a[r][j]
            prob += pulp.lpSum(x[r][b] for b in bits) + pulp.lpSum(y[r][b] for b in bits) >= BRANCH * a[r][j]

    # propagation by PBOX: x[r+1] == PBOX(y[r])
    for r in range(rounds-1):
        for i in range(16):
            prob += x[r+1][PBOX[i]] == y[r][i]

    # Non-zero input difference at round 0
    prob += pulp.lpSum(a[0][j] for j in range(4)) >= 1

    # Objective: minimize total actives
    prob += pulp.lpSum(a[r][j] for r in range(rounds) for j in range(4))

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] != "Optimal":
        raise RuntimeError("MILP not optimal")

    total = int(pulp.value(pulp.lpSum(a[r][j] for r in range(rounds) for j in range(4))))
    per_round = [int(sum(a[r][j].value() for j in range(4))) for r in range(rounds)]
    return total, per_round
