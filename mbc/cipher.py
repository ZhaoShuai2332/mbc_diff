# Simple 16-bit SPN cipher (S -> P -> AddRoundKey)
from .sbox import sbox_block16
from .perm import permute_bits

def key_schedule(master_key: int, rounds: int):
    # lightweight toy schedule: rotate and xor round index
    k = master_key & 0xFFFF
    ks = []
    for r in range(rounds+1):
        ks.append(k)
        k = ((k << 4) | (k >> 12)) & 0xFFFF
        k ^= (r & 0xF)
    return ks

def encrypt(plain: int, key: int, rounds: int) -> int:
    ks = key_schedule(key, rounds)
    s = plain ^ ks[0]
    for r in range(rounds-1):
        s = sbox_block16(s)
        s = permute_bits(s)
        s ^= ks[r+1]
    s = sbox_block16(s)
    s ^= ks[-1]
    return s & 0xFFFF
