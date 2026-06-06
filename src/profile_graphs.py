"""
profile_graphs.py — clean + profile all five connectome graphs.

For each dataset prints:
  - N nodes, M directed edges (after dropping self-loops + parallel edges)
  - mean / max in- and out-degree
  - reciprocity (fraction of directed edges whose reverse also exists)
  - number of isolated-after-induction singletons is N/A here (edge list only)
  - largest weakly-connected component size
  - count of "leaf-ish" low-degree nodes (relevant to independent-set degeneracy)

Run:  python src/profile_graphs.py
"""
from __future__ import annotations
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import connected_components

from io_utils import DATASETS, build_clean


def reciprocity(edges: np.ndarray, n: int) -> float:
    """Fraction of directed edges (u->v) for which v->u also exists."""
    fwd = set(map(tuple, edges.tolist()))
    rec = sum(1 for u, v in edges.tolist() if (v, u) in fwd)
    return rec / len(edges) if len(edges) else 0.0


def profile(ds: str) -> dict:
    nodes, edges = build_clean(ds)
    n = len(nodes)
    m = len(edges)
    outdeg = np.bincount(edges[:, 0], minlength=n)
    indeg = np.bincount(edges[:, 1], minlength=n)
    deg = outdeg + indeg

    # Weakly-connected components (treat as undirected).
    sym = coo_matrix(
        (np.ones(m, dtype=np.int8), (edges[:, 0], edges[:, 1])), shape=(n, n)
    )
    ncomp, labels = connected_components(sym, directed=True, connection="weak")
    comp_sizes = np.bincount(labels)
    largest_wcc = comp_sizes.max()

    # Reciprocity on a sample if huge (exact is O(M) with a set; fine up to ~6M).
    recip = reciprocity(edges, n)

    return {
        "dataset": ds,
        "N_nodes": n,
        "M_edges": m,
        "mean_outdeg": outdeg.mean(),
        "max_outdeg": int(outdeg.max()),
        "mean_indeg": indeg.mean(),
        "max_indeg": int(indeg.max()),
        "reciprocity": recip,
        "n_wcc": ncomp,
        "largest_wcc": int(largest_wcc),
        "deg1_nodes": int((deg == 1).sum()),
        "isolated_in_lcc_pct": 100.0 * largest_wcc / n,
    }


def main():
    rows = [profile(ds) for ds in DATASETS]
    cols = ["dataset", "N_nodes", "M_edges", "mean_outdeg", "max_outdeg",
            "mean_indeg", "max_indeg", "reciprocity", "n_wcc", "largest_wcc",
            "isolated_in_lcc_pct", "deg1_nodes"]
    # Pretty print.
    widths = {c: max(len(c), 12) for c in cols}
    print(" | ".join(c.rjust(widths[c]) for c in cols))
    print("-" * (sum(widths.values()) + 3 * (len(cols) - 1)))
    for r in rows:
        cells = []
        for c in cols:
            v = r[c]
            s = f"{v:.3f}" if isinstance(v, float) else str(v)
            cells.append(s.rjust(widths[c]))
        print(" | ".join(cells))


if __name__ == "__main__":
    main()
