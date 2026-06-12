"""
match_engine.py — find conserved (exactly-isomorphic) directed induced subgraphs
across multiple connectome graphs.

Three tiers, by structural richness (a deliberate frontier, since the literal
"maximize N" objective is degenerate — see README):

  Tier 0  common independent set   (induced subgraph = empty graph; trivially iso)
  Tier 1  common induced out-star  (hub -> n leaves, leaves mutually non-adjacent)
  Tier 2  seeded growth of the largest RICHLY-connected common induced subgraph

Every returned correspondence is verified exactly with VF2 (iso_utils.is_iso).
"""
from __future__ import annotations
import numpy as np
from graph_core import DiGraph


# ---------------------------------------------------------------- Tier 0
def greedy_independent_set(G: DiGraph, cap: int | None = None) -> list[int]:
    """Greedy maximal independent set (treat edges as undirected). Not provably max,
    but demonstrates the degeneracy: induced subgraph on these nodes has no edges."""
    order = np.argsort(G.outdeg + G.indeg)  # low-degree first packs more nodes
    chosen = []
    blocked = np.zeros(G.n, dtype=bool)
    for i in order.tolist():
        if blocked[i]:
            continue
        chosen.append(i)
        blocked[i] = True
        blocked[G.out_neighbors(i)] = True
        blocked[G.in_neighbors(i)] = True
        if cap and len(chosen) >= cap:
            break
    return chosen


# ---------------------------------------------------------------- Tier 1
def max_induced_out_star(G: DiGraph, n_hubs_try: int = 50) -> list[int]:
    """Find a large induced out-star: a hub h and leaves L s.t. h->l for all l in L,
    and no other edges among {h} U L (no l->h, no l->l')."""
    best = []
    hubs = np.argsort(-G.outdeg)[:n_hubs_try]
    for h in hubs.tolist():
        outs = G.out_neighbors(h)
        # drop leaves that point back to the hub (would break induced out-star)
        outs = np.array([v for v in outs.tolist() if not G.has_edge(v, h)],
                        dtype=np.int64)
        if len(outs) <= len(best):
            continue
        # pick a subset of outs that is mutually non-adjacent (independent set
        # in the induced subgraph on `outs`)
        leaf_set = set(outs.tolist())
        chosen, blocked = [], set()
        # process candidate leaves low-degree-first for a larger independent subset
        for l in sorted(outs.tolist(), key=lambda x: G.outdeg[x] + G.indeg[x]):
            if l in blocked:
                continue
            chosen.append(l)
            for w in G.out_neighbors(l).tolist():
                if w in leaf_set:
                    blocked.add(w)
            for w in G.in_neighbors(l).tolist():
                if w in leaf_set:
                    blocked.add(w)
        if len(chosen) > len(best):
            best = [h] + chosen
    return best


# ---------------------------------------------------------------- Tier 2
def _attach_sig(G: DiGraph, node: int, matched: list[int]) -> tuple:
    """Binary (out, in) attachment pattern of `node` to the ordered `matched` set."""
    outs = tuple(1 if G.has_edge(node, m) else 0 for m in matched)
    ins = tuple(1 if G.has_edge(m, node) else 0 for m in matched)
    return outs + ins


def _attach_sigs_batch(G: DiGraph, cand: np.ndarray, matched: np.ndarray):
    """Vectorized attachment signatures of every candidate to the matched set.
    Returns (sig_bytes_list, edgecount_array). sig encodes out-edges (cand->matched)
    then in-edges (matched->cand) as a 2k-length 0/1 vector.
    """
    cand = cand.astype(np.int64)
    matched = matched.astype(np.int64)
    F, k = len(cand), len(matched)
    out_keys = ((cand[:, None] << 32) | matched[None, :]).ravel()   # cand -> matched
    in_keys = ((matched[None, :] << 32) | cand[:, None]).ravel()    # matched -> cand
    out_p = G.has_edges(out_keys).reshape(F, k)
    in_p = G.has_edges(in_keys).reshape(F, k)
    sig_mat = np.concatenate([out_p, in_p], axis=1).astype(np.uint8)
    edgecount = sig_mat.sum(axis=1)
    sigs = [sig_mat[i].tobytes() for i in range(F)]
    return sigs, edgecount


def _frontier(G: DiGraph, matched: set[int], cap: int = 4000) -> list[int]:
    """Unmatched nodes adjacent (either direction) to the matched set.

    Deterministic: we iterate `matched` in sorted order and return a SORTED list, so
    the candidate set (and the cap cut-off) does not depend on Python set iteration
    order. Downstream, the first candidate per (signature, type) key is therefore the
    lowest node index, making the whole search reproducible run-to-run (no seed needed;
    there is no randomness, only previously order-dependent set traversal)."""
    cand = set()
    for m in sorted(matched):
        cand.update(G.out_neighbors(m).tolist())
        cand.update(G.in_neighbors(m).tolist())
        if len(cand) > cap:
            break
    cand -= matched
    return sorted(cand)


def grow_common_subgraph(graphs: list[DiGraph], seeds: list[int],
                         max_n: int = 60, strategy: str = "rich",
                         frontier_cap: int = 1500, labels=None):
    """Greedily grow a common induced subgraph across all graphs, starting from one
    seed node per graph.

    Correctness invariant: at every step the induced adjacency matrices (in matched
    order) are IDENTICAL. We only add a node triple whose in/out attachment pattern
    to the current matched set is the same string in all three graphs; appending an
    identical row+column to identical matrices keeps them identical. (VF2 still
    re-verifies at the end.)

    If `labels` is given (one node->label map per graph), an added triple must ALSO
    share the same label in all graphs -> enforces biological identity (same cell
    type), turning the result into a genuine *conserved* circuit, not a coincidental
    structural match.

    strategy: 'rich' picks the attachment signature with the most edges (denser,
    more biologically meaningful); 'wide' picks the thinnest (grows larger N).
    Returns list-of-lists of matched node indices (one per graph), consistent order.
    """
    matched = [[s] for s in seeds]
    msets = [set([s]) for s in seeds]
    while len(matched[0]) < max_n:
        # Build key -> candidate map for each graph's frontier (vectorized).
        sigmaps = []
        for gi, G in enumerate(graphs):
            front = _frontier(G, msets[gi], cap=frontier_cap)
            d = {}
            if front:
                cand = np.array(front, dtype=np.int64)
                marr = np.array(matched[gi], dtype=np.int64)
                sigs, ec = _attach_sigs_batch(G, cand, marr)
                for x, sig, e in zip(front, sigs, ec.tolist()):
                    if e == 0:           # require the new node to connect
                        continue
                    key = sig if labels is None else (sig, labels[gi][x])
                    # Deterministic representative per key: highest total degree
                    # (more onward edges -> richer future growth), tie-break lowest
                    # index. Any node with this key is a valid match (identity depends
                    # only on attachment to the *current* matched set), so the choice
                    # affects only downstream growth, not correctness.
                    cur = d.get(key)
                    if cur is None or (G.indeg[x] + G.outdeg[x],
                                       -x) > (G.indeg[cur] + G.outdeg[cur], -cur):
                        d[key] = x
            sigmaps.append(d)
        common = set(sigmaps[0])
        for d in sigmaps[1:]:
            common &= set(d)
        if not common:
            break
        # popcount of the signature component = number of edges it adds
        def _popcount(k):
            sig = k[0] if labels is not None else k
            return sig.count(b"\x01")
        if strategy == "rich":
            key = max(common, key=lambda k: (_popcount(k), k))
        else:  # 'wide' — fewest new edges (thinner, tends to grow longer)
            key = min(common, key=lambda k: (_popcount(k), k))
        for gi in range(len(graphs)):
            x = sigmaps[gi][key]
            matched[gi].append(x)
            msets[gi].add(x)
    return matched


# ---------------------------------------------------------------- circuit extraction
def two_core_positions(A: np.ndarray) -> np.ndarray:
    """Return positions of the undirected 2-core of adjacency A (min total degree >= 2).
    Removes dangling leaves so the result is a real 'circuit' (every node on a cycle
    path), not a star/tree fringe."""
    und = (A | A.T).astype(bool)
    keep = np.ones(A.shape[0], dtype=bool)
    while True:
        deg = und[np.ix_(keep, keep)].sum(1)
        idxs = np.where(keep)[0]
        low = idxs[deg < 2]
        if low.size == 0:
            break
        keep[low] = False
        if keep.sum() == 0:
            break
    return np.where(keep)[0]


def largest_weak_component_positions(A: np.ndarray) -> np.ndarray:
    """Positions of the largest weakly-connected component of adjacency A."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    n = A.shape[0]
    if n == 0:
        return np.array([], dtype=int)
    S = csr_matrix((A | A.T).astype(np.int8))
    ncomp, lab = connected_components(S, directed=False)
    if ncomp == 0:
        return np.arange(n)
    big = np.bincount(lab).argmax()
    return np.where(lab == big)[0]
