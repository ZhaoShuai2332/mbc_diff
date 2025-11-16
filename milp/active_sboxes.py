# MILP model (PuLP+CBC) for minimal number of active S-boxes
from typing import List, Tuple
import pulp

# nibble index 0..3; each nibble has 4 bits -> bit indices in 0..15
def nibble_bits(j: int) -> List[int]:
    return [4*j + k for k in range(4)]

# permutation for 16-bit
PBOX = [(i % 4)*4 + (i // 4) for i in range(16)]

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
            # each bit <= a
            for b in bits:
                prob += x[r][b] <= a[r][j]
            # if a==1 at least one input bit is 1
            prob += pulp.lpSum(x[r][b] for b in bits) >= a[r][j]

            # S-box property (coarse): if active then some output bit 1; if not active, no output bit
            for b in bits:
                prob += y[r][b] <= a[r][j]
            prob += pulp.lpSum(y[r][b] for b in bits) >= a[r][j]

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
