"""
graph_core.py — fast directed-graph primitives for the conserved-circuit search.

A `DiGraph` stores:
  - out_csr / in_csr : CSR adjacency for O(deg) neighbor iteration
  - ekey (sorted int64) : packed (u<<32 | v) edge keys for O(log M) existence tests,
                          vectorizable via np.searchsorted

Edge-existence on an induced node set is the workhorse of induced-subgraph matching,
so it must be fast. We avoid a Python set of millions of ints (memory heavy) and use
a sorted key array instead.
"""
from __future__ import annotations
import numpy as np


class DiGraph:
    def __init__(self, n: int, edges: np.ndarray):
        self.n = int(n)
        self.edges = edges.astype(np.int64)
        u = self.edges[:, 0]
        v = self.edges[:, 1]

        # CSR for out-neighbors (sorted by u).
        order = np.argsort(u, kind="stable")
        self.out_indptr = np.zeros(self.n + 1, dtype=np.int64)
        np.add.at(self.out_indptr, u + 1, 1)
        np.cumsum(self.out_indptr, out=self.out_indptr)
        self.out_indices = v[order].astype(np.int32)

        # CSR for in-neighbors (sorted by v).
        order_in = np.argsort(v, kind="stable")
        self.in_indptr = np.zeros(self.n + 1, dtype=np.int64)
        np.add.at(self.in_indptr, v + 1, 1)
        np.cumsum(self.in_indptr, out=self.in_indptr)
        self.in_indices = u[order_in].astype(np.int32)

        # Sorted packed edge keys for existence queries.
        self.ekey = np.sort((u << 32) | v)

        self.outdeg = np.diff(self.out_indptr).astype(np.int64)
        self.indeg = np.diff(self.in_indptr).astype(np.int64)

    def out_neighbors(self, i: int) -> np.ndarray:
        return self.out_indices[self.out_indptr[i]:self.out_indptr[i + 1]]

    def in_neighbors(self, i: int) -> np.ndarray:
        return self.in_indices[self.in_indptr[i]:self.in_indptr[i + 1]]

    def has_edge(self, u: int, v: int) -> bool:
        k = (np.int64(u) << 32) | np.int64(v)
        idx = np.searchsorted(self.ekey, k)
        return idx < self.ekey.size and self.ekey[idx] == k

    def has_edges(self, keys: np.ndarray) -> np.ndarray:
        """Vectorized existence test for an array of packed (u<<32|v) keys."""
        idx = np.searchsorted(self.ekey, keys)
        idx = np.clip(idx, 0, self.ekey.size - 1)
        return self.ekey[idx] == keys

    def induced_adcmatrix(self, nodes: list[int]) -> np.ndarray:
        """Directed adjacency matrix (k x k, uint8) of the induced subgraph on `nodes`,
        in the given node order."""
        k = len(nodes)
        nodes_arr = np.asarray(nodes, dtype=np.int64)
        # All ordered pairs.
        uu = np.repeat(nodes_arr, k)
        vv = np.tile(nodes_arr, k)
        keys = (uu << 32) | vv
        present = self.has_edges(keys).reshape(k, k)
        np.fill_diagonal(present, False)
        return present.astype(np.uint8)
