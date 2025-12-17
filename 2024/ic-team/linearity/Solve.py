#!/usr/bin/env python3
import hashlib, time, math
from multiprocessing import Pool, cpu_count

TARGET = "e256693b7b7d07e11f2f83f452f04969ea327261d56406d2d657da1066cefa17"

# ---------- candidates_per_pos taken from your output ----------
candidates_per_pos = [
 ['i'], ['n'], ['f'], ['o'], ['b'],
 ['a'], ['h'], ['n'], ['{'],
 ['*','Y'],
 ['%','7','K','U','o','y'],
 ['u'],
 ['/','_'],
 ['<','H'],
 [';','A'],
 ['&','0','D','J','V','n','x'],
 ['9','E'],
 ['_','g'],
 ['A'],
 ['3','Y','f'],
 ['.','8','B','L','^','f','p'],
 ['1','E','k'],
 ['6','n'],
 ['%','i'],
 ['T','a'],
 ['y'],
 ['_'],
 ['f'],
 ['0'],
 ['r'],
 ['C'],
 ['r'],
 ['y'],
 ['p'],
 ['t'],
 ['%','7','K','U','o','y'],
 ['}']
]
# length should be 37
assert len(candidates_per_pos) == 37

# Reorder some plausible preferences:
prio = {
    9: ['Y','*'],
    10: ['o','y','%','7','K','U'],
    12: ['_','/'],
    13: ['H','<'],
    14: ['A',';'],
    15: ['V','n','&','0','D','J','x'],
    16: ['E','9'],
    17: ['_','g'],
    19: ['f','Y','3'],
    20: ['p','f','B','L','.','8','^'],
    21: ['E','1','k'],
    22: ['n','6'],
    23: ['i','%'],
    24: ['a','T'],
    35: ['y','o','%','7','K','U'],
}
for idx, order in prio.items():
    # reorder candidates_per_pos[idx] preserving only existing candidates
    cand = candidates_per_pos[idx]
    new = [c for c in order if c in cand] + [c for c in cand if c not in order]
    candidates_per_pos[idx] = new

# Build list of fixed bytes (for single-candidate positions) and ambiguous indices
n = len(candidates_per_pos)
fixed_buf = bytearray(n)
ambiguous_positions = []
radices = []
for i, lst in enumerate(candidates_per_pos):
    if len(lst) == 1:
        fixed_buf[i] = ord(lst[0])
    else:
        ambiguous_positions.append(i)
        radices.append(len(lst))

total = 1
for r in radices:
    total *= r

print("Total ambiguous positions:", len(ambiguous_positions))
print("Total combinations to try:", f"{total:,}")
print("Ambiguous indices:", ambiguous_positions)
print("Radices:", radices)

# prepare ordered candidate lists for ambiguous positions
cand_lists = [candidates_per_pos[i] for i in ambiguous_positions]

# mixed-radix index -> digits
# precompute multipliers
multipliers = []
m = 1
for r in reversed(radices):
    multipliers.append(m)
    m *= r
multipliers = list(reversed(multipliers))  # len == len(radices)

def index_to_digits(idx):
    digits = [0]*len(radices)
    for i in range(len(radices)):
        if radices[i] == 1:
            digits[i] = 0
            continue
        d = idx // multipliers[i]
        idx = idx % multipliers[i]
        digits[i] = int(d)
    return digits

# map digits to buffer
def digits_to_buf(digits, out_buf):
    # out_buf is a bytearray copy of fixed_buf
    for di, d in enumerate(digits):
        pos = ambiguous_positions[di]
        out_buf[pos] = ord(cand_lists[di][d])

# worker processing a range of indices [a,b)
def worker_range(args):
    a, b = args
    local = bytearray(fixed_buf)
    mv = memoryview(local)
    # small optimization: reuse allocation for index_to_digits by manual mixed-radix arithmetic
    for idx in range(a, b):
        # compute digits and set bytes
        rem = idx
        for i in range(len(radices)):
            if radices[i] == 1:
                d = 0
            else:
                d = rem // multipliers[i]
                rem = rem % multipliers[i]
            mv[ambiguous_positions[i]] = ord(cand_lists[i][d])
        # check hash
        if hashlib.sha256(local).hexdigest() == TARGET:
            return bytes(local)
    return None

def run_parallel(num_workers=None):
    if total == 0:
        print("Nothing to do")
        return None
    workers = num_workers or min(cpu_count(), 8)
    # split into per-worker blocks
    block = (total + workers - 1) // workers
    ranges = []
    for w in range(workers):
        a = w*block
        b = min(total, (w+1)*block)
        if a < b:
            ranges.append((a,b))
    print("Worker ranges:", ranges)
    t0 = time.time()
    with Pool(processes=len(ranges)) as pool:
        for res in pool.imap_unordered(worker_range, ranges):
            if res:
                print("FOUND flag:", res.decode(errors='replace'))
                pool.terminate()
                print("Elapsed:", time.time()-t0)
                return res
    print("Done. Elapsed:", time.time()-t0)
    return None

if __name__ == "__main__":
    print("Starting search (parallel)...")
    res = run_parallel()
    if res:
        print("FLAG:", res.decode(errors='replace'))
    else:
        print("No match found in candidate space.")
