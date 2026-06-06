"""
verify_submission.py — INDEPENDENT check of network.csv against the raw edge lists.
Does not use the project's graph code: it re-reads the three provided CSVs, builds
edge sets from scratch, extracts the induced subgraph on each column's neuron IDs in
row order, and confirms the three adjacency matrices are byte-identical (hence the
directed induced subgraphs are mutually isomorphic via the row-correspondence).

Usage:  python verify_submission.py
"""
import csv
import numpy as np
import pandas as pd

RAW = {"FAFB": "fafb_783_edge_list.csv", "BANC": "banc_626_edge_list.csv",
       "MCNS": "mcns_0.9_edge_list.csv", "MANC": "manc_1.2.1_edge_list.csv",
       "MAOL": "maol_1.1_edge_list.csv"}

# read the submission
with open("network.csv") as f:
    r = list(csv.reader(f))
cols = r[0]
rows = [[int(x) for x in row] for row in r[1:]]
N = len(rows)
print(f"network.csv: datasets={cols}  N={N} rows")

adjs = []
for c, ds in enumerate(cols):
    ids = [row[c] for row in rows]
    idset = set(ids)
    pos = {rid: i for i, rid in enumerate(ids)}
    assert len(idset) == N, f"{ds}: duplicate IDs in column!"
    # stream the raw edge list, keep only edges within the id set
    A = np.zeros((N, N), dtype=np.uint8)
    df = pd.read_csv(RAW[ds], usecols=[0, 1], header=0,
                     names=["s", "t"], dtype=np.int64)
    s = df["s"].to_numpy(); t = df["t"].to_numpy()
    mask = np.isin(s, list(idset)) & np.isin(t, list(idset))
    for u, v in zip(s[mask].tolist(), t[mask].tolist()):
        if u != v:
            A[pos[u], pos[v]] = 1
    adjs.append(A)
    print(f"  {ds}: induced edges = {int(A.sum())}")

ident = all(np.array_equal(adjs[0], adjs[i]) for i in range(1, len(adjs)))
print(f"\nAll induced adjacency matrices byte-identical: {ident}")
if ident:
    print(f"=> the {len(cols)} directed induced subgraphs are MUTUALLY ISOMORPHIC "
          f"(N={N}, {int(adjs[0].sum())} edges). VERIFIED.")
else:
    # report first divergence
    D = np.argwhere(adjs[0] != adjs[1])
    print("MISMATCH at", D[:5])
