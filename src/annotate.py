"""
annotate.py — unified per-dataset metadata: map node index -> (super_class, cell_type, nt).

FAFB: classification.csv.gz (super_class/class/sub_class) + consolidated_cell_types.csv.gz
      (primary_type) + neurons.csv.gz (nt_type).
BANC/MCNS: neurons.csv.gz with columns 'Super Class','Class','Primary Cell Type',
      'Predicted NT type'.
Returned dicts are keyed by the CONTIGUOUS node index used by graph_core (via io_utils).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from io_utils import build_clean, ROOT

META = os.path.join(ROOT, "data", "meta")


def _idmap(ds):
    nodes, _ = build_clean(ds)
    return {int(rid): i for i, rid in enumerate(nodes.tolist())}, nodes


def load_annotations(ds: str):
    """Return dict: node_index -> {'super_class','cell_type','nt','side'} and the
    int64 root-id array (index -> root id)."""
    idmap, nodes = _idmap(ds)
    ann = {i: {"super_class": "", "cell_type": "", "nt": "", "side": ""}
           for i in range(len(nodes))}

    if ds == "FAFB":
        cls = pd.read_csv(os.path.join(META, "fafb_classification.csv.gz"))
        ct = pd.read_csv(os.path.join(META, "fafb_consolidated_cell_types.csv.gz"))
        nt = pd.read_csv(os.path.join(META, "fafb_neurons.csv.gz"),
                         usecols=["root_id", "nt_type"])
        ctmap = dict(zip(ct["root_id"].astype("int64"), ct["primary_type"]))
        ntmap = dict(zip(nt["root_id"].astype("int64"), nt["nt_type"]))
        for rid, sc, cl, scl, side in zip(cls["root_id"].astype("int64"),
                                          cls["super_class"], cls["class"],
                                          cls["sub_class"], cls["side"]):
            i = idmap.get(int(rid))
            if i is None:
                continue
            ann[i]["super_class"] = str(sc)
            ann[i]["cell_type"] = str(ctmap.get(int(rid)) or scl or cl or "")
            ann[i]["nt"] = str(ntmap.get(int(rid)) or "")
            ann[i]["side"] = str(side)
    else:
        fn = "banc_neurons.csv.gz" if ds == "BANC" else "mcns_neurons.csv.gz"
        df = pd.read_csv(os.path.join(META, fn))
        for rid, sc, pct, cl, nt, side in zip(
                df["Root ID"].astype("int64"), df["Super Class"],
                df["Primary Cell Type"], df["Class"],
                df["Predicted NT type"], df["Soma side"]):
            i = idmap.get(int(rid))
            if i is None:
                continue
            ann[i]["super_class"] = "" if pd.isna(sc) else str(sc)
            ct = pct if not pd.isna(pct) else (cl if not pd.isna(cl) else "")
            ann[i]["cell_type"] = str(ct)
            ann[i]["nt"] = "" if pd.isna(nt) else str(nt)
            ann[i]["side"] = "" if pd.isna(side) else str(side)
    return ann, nodes
