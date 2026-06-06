"""
test_core.py — validate DiGraph primitives against a networkx ground truth.
Uses MANC (smallest) and checks: neighbor sets, edge existence, induced adjacency.
"""
from __future__ import annotations
import numpy as np
import networkx as nx

from io_utils import build_clean
from graph_core import DiGraph

rng = np.random.default_rng(0)

nodes, edges = build_clean("MANC")
G = DiGraph(len(nodes), edges)

# Ground-truth networkx graph on the same contiguous indices.
GT = nx.DiGraph()
GT.add_nodes_from(range(len(nodes)))
GT.add_edges_from(map(tuple, edges.tolist()))

# 1) neighbor sets for random nodes
ok_nb = True
for i in rng.integers(0, len(nodes), size=200):
    i = int(i)
    if set(G.out_neighbors(i).tolist()) != set(GT.successors(i)):
        ok_nb = False; break
    if set(G.in_neighbors(i).tolist()) != set(GT.predecessors(i)):
        ok_nb = False; break
print("neighbor sets match:", ok_nb)

# 2) edge existence (positive + negative)
pos = edges[rng.integers(0, len(edges), size=500)]
ok_pos = all(G.has_edge(int(u), int(v)) for u, v in pos.tolist())
neg_ok = 0; neg_tot = 0
for _ in range(500):
    u = int(rng.integers(0, len(nodes))); v = int(rng.integers(0, len(nodes)))
    if not GT.has_edge(u, v):
        neg_tot += 1
        if not G.has_edge(u, v):
            neg_ok += 1
print("edge existence positives ok:", ok_pos)
print(f"edge existence negatives ok: {neg_ok}/{neg_tot}")

# 3) induced adjacency vs networkx subgraph
ok_ind = True
for _ in range(50):
    k = int(rng.integers(3, 8))
    sub = rng.choice(len(nodes), size=k, replace=False).tolist()
    A = G.induced_adcmatrix(sub)
    H = GT.subgraph(sub)
    # Build ground-truth adjacency in the same node order.
    B = np.zeros((k, k), dtype=np.uint8)
    idx = {node: p for p, node in enumerate(sub)}
    for a, b in H.edges():
        if a != b:
            B[idx[a], idx[b]] = 1
    if not np.array_equal(A, B):
        ok_ind = False; break
print("induced adjacency match:", ok_ind)
