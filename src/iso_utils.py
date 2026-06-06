"""
iso_utils.py — exact directed-(sub)graph isomorphism helpers.

Strategy: use a Weisfeiler–Lehman hash to *bucket* candidate subgraphs cheaply,
then confirm with exact VF2 (networkx DiGraphMatcher). WL-hash can collide across
non-isomorphic graphs, so it is only ever used to narrow candidates; the final
guarantee always comes from VF2. This keeps the pipeline both fast and exact.
"""
from __future__ import annotations
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher


def adj_to_nx(adj: np.ndarray) -> nx.DiGraph:
    """k x k 0/1 directed adjacency -> nx.DiGraph on nodes 0..k-1."""
    g = nx.DiGraph()
    g.add_nodes_from(range(adj.shape[0]))
    rows, cols = np.nonzero(adj)
    g.add_edges_from(zip(rows.tolist(), cols.tolist()))
    return g


def wl_hash(adj: np.ndarray, iterations: int = 3) -> str:
    """Directed WL hash. Initial node label = (in_deg, out_deg). Cheap bucketing key."""
    g = adj_to_nx(adj)
    for node in g.nodes():
        g.nodes[node]["d"] = f"{g.in_degree(node)}_{g.out_degree(node)}"
    return nx.weisfeiler_lehman_graph_hash(
        g, node_attr="d", iterations=iterations, digest_size=16
    )


def is_iso(adj_a: np.ndarray, adj_b: np.ndarray) -> bool:
    """Exact directed isomorphism test (VF2)."""
    if adj_a.shape != adj_b.shape:
        return False
    if adj_a.sum() != adj_b.sum():
        return False
    ga, gb = adj_to_nx(adj_a), adj_to_nx(adj_b)
    return DiGraphMatcher(ga, gb).is_isomorphic()


def iso_mapping(adj_a: np.ndarray, adj_b: np.ndarray):
    """Return a node mapping a->b realizing an isomorphism, or None."""
    ga, gb = adj_to_nx(adj_a), adj_to_nx(adj_b)
    m = DiGraphMatcher(ga, gb)
    if m.is_isomorphic():
        return m.mapping  # dict: node_in_a -> node_in_b
    return None


def degree_signature(adj: np.ndarray) -> tuple:
    """Sorted (in_deg, out_deg) multiset — a fast necessary invariant for isomorphism."""
    indeg = adj.sum(axis=0)
    outdeg = adj.sum(axis=1)
    return tuple(sorted(zip(indeg.tolist(), outdeg.tolist())))
