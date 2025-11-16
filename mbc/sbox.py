# 4-bit S-box and helpers (default: PRESENT S-box)
SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]
INV_SBOX = [0]*16
for i,v in enumerate(SBOX):
    INV_SBOX[v] = i

def sbox_nibble(n4: int) -> int:
    return SBOX[n4 & 0xF]

def sbox_block16(x: int) -> int:
    y = 0
    for i in range(4):
        nib = (x >> (4*i)) & 0xF
        y |= SBOX[nib] << (4*i)
    return y

def build_ddt():
    # ddt[a][b] = count of x s.t. S(x) ^ S(x^a) == b
    ddt = [[0]*16 for _ in range(16)]
    for a in range(16):
        for x in range(16):
            b = SBOX[x] ^ SBOX[x ^ a]
            ddt[a][b] += 1
    return ddt

DDT = build_ddt()

def sbox_pmax():
    # maximum non-zero input differential probability
    pmax = 0.0
    for a in range(1,16):
        for b in range(16):
            if DDT[a][b] > 0 and b != 0:
                p = DDT[a][b] / 16.0
                if p > pmax:
                    pmax = p
    return pmax
