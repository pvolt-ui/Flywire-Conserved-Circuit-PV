"""
make_3d.py — download FAFB skeletons (SWC) for a representative subset of the
conserved circuit and render a 3D morphology figure, colored by pathway layer.
Satisfies the 'Codex 3D meshes' deliverable. Run with python -u.
"""
from __future__ import annotations
import os, json, urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

from io_utils import ROOT

FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
SWC = "https://storage.googleapis.com/flywire-data/codex/skeletons/fafb/lod1/{}.swc"

LAYER_COLOR = {"ORN": "#d62728", "PN": "#1f77b4", "LN": "#ff7f0e",
               "KC": "#2ca02c", "APL": "#9467bd"}


def bucket(t):
    if t == "APL":
        return "APL"
    if t.startswith("KC"):
        return "KC"
    if t.startswith("ORN") or t.startswith("HRN"):
        return "ORN"
    if "PN" in t:
        return "PN"
    return "LN"


def fetch_swc(rid):
    try:
        with urllib.request.urlopen(SWC.format(rid), timeout=90) as r:
            data = r.read().decode("utf-8", "ignore")
    except Exception as e:
        print("  skip", rid, e); return None
    pts = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) >= 5:
            pts.append((float(f[2]), float(f[3]), float(f[4])))
    return np.array(pts) if pts else None


def main():
    h = json.load(open(os.path.join(RES, "headline_typed.json")))
    rows = h["rows"]
    picks, seen = [], {}
    quota = {"APL": 1, "PN": 2, "LN": 2, "KC": 5, "ORN": 6}
    for r in rows:
        t = r["cell_type"][0]; b = bucket(t)
        if seen.get(b, 0) < quota.get(b, 0):
            picks.append((r["root_ids"][0], t, b))
            seen[b] = seen.get(b, 0) + 1
    print("subset:", [p[1] for p in picks], flush=True)

    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")
    legend_done = set()
    for rid, t, b in picks:
        pts = fetch_swc(rid)
        if pts is None or len(pts) < 3:
            continue
        if len(pts) > 2500:
            pts = pts[np.random.default_rng(0).choice(len(pts), 2500, replace=False)]
        lab = b if b not in legend_done else None
        legend_done.add(b)
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=1.5,
                   color=LAYER_COLOR[b], alpha=0.5, label=lab)
        print(f"  plotted {t} ({len(pts)} pts)", flush=True)
    ax.set_title("Conserved circuit neurons in FAFB brain space (Codex skeletons)\n"
                 "representative subset, colored by pathway layer", fontsize=11)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.legend(markerscale=6, fontsize=9, loc="upper left")
    ax.view_init(elev=18, azim=-70)
    plt.tight_layout()
    out = os.path.join(FIG, "circuit_3d.png")
    plt.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    main()
