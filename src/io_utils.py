"""
io_utils.py — shared loading / cleaning utilities for the FlyWire connectome graphs.

Each raw file is a 2-column CSV: `source neuron id, target neuron id`.
Edges are directed. We ignore synapse-count weights (per the challenge rules),
drop self-loops, and collapse parallel edges to a simple directed graph.

For speed downstream we relabel the (large int64) root IDs to contiguous int32
node indices and cache:
    data/clean/<ds>_nodes.npy  -> int64[N]   original root IDs, sorted; index i == node i
    data/clean/<ds>_edges.npy  -> int32[M,2] (src_idx, dst_idx), deduped, no self-loops
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

DATASETS = {
    "BANC": "banc_626_edge_list.csv",
    "FAFB": "fafb_783_edge_list.csv",
    "MANC": "manc_1.2.1_edge_list.csv",
    "MAOL": "maol_1.1_edge_list.csv",
    "MCNS": "mcns_0.9_edge_list.csv",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(ROOT, "data", "clean")


def raw_path(ds: str) -> str:
    return os.path.join(ROOT, DATASETS[ds])


def clean_paths(ds: str) -> tuple[str, str]:
    return (
        os.path.join(CLEAN_DIR, f"{ds}_nodes.npy"),
        os.path.join(CLEAN_DIR, f"{ds}_edges.npy"),
    )


def build_clean(ds: str, force: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Load raw edge list, clean it, relabel to contiguous indices, cache, and return
    (nodes_int64[N], edges_int32[M,2])."""
    os.makedirs(CLEAN_DIR, exist_ok=True)
    npath, epath = clean_paths(ds)
    if not force and os.path.exists(npath) and os.path.exists(epath):
        return np.load(npath), np.load(epath)

    # Read the two columns as int64. The headers are
    # "source neuron id","target neuron id".
    df = pd.read_csv(raw_path(ds), usecols=[0, 1], header=0,
                     names=["src", "dst"], dtype=np.int64)
    src = df["src"].to_numpy()
    dst = df["dst"].to_numpy()

    # Drop self-loops.
    keep = src != dst
    src, dst = src[keep], dst[keep]

    # Relabel original IDs -> contiguous indices.
    nodes, inv = np.unique(np.concatenate([src, dst]), return_inverse=True)
    inv = inv.astype(np.int64)
    n_src = inv[: len(src)]
    n_dst = inv[len(src):]

    # Dedupe parallel edges via a single 64-bit key (safe: index < 2^31).
    key = (n_src.astype(np.int64) << 32) | n_dst.astype(np.int64)
    key = np.unique(key)
    e_src = (key >> 32).astype(np.int32)
    e_dst = (key & 0xFFFFFFFF).astype(np.int32)
    edges = np.stack([e_src, e_dst], axis=1)

    nodes = nodes.astype(np.int64)
    np.save(npath, nodes)
    np.save(epath, edges)
    return nodes, edges
