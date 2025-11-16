# 16-bit bit permutation from the slide:
# source positions 0..15 -> destination positions:
PBOX = [0]*16
for i in range(16):
    PBOX[i] = (i % 4) * 4 + (i // 4)  # maps [0..15] to [0,4,8,12,1,5,9,...]

INV_PBOX = [0]*16
for i,d in enumerate(PBOX):
    INV_PBOX[d] = i

def permute_bits(x: int) -> int:
    y = 0
    for i in range(16):
        y |= ((x >> i) & 1) << PBOX[i]
    return y

def inv_permute_bits(x: int) -> int:
    y = 0
    for i in range(16):
        y |= ((x >> i) & 1) << INV_PBOX[i]
    return y
