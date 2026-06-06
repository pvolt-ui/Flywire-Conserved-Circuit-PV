"""
make_figures.py — build the network-graph figure and the frontier figure from the
saved headline circuit. Run after the conserved-circuit search.
"""
from __future__ import annotations
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from io_utils import ROOT

FIG = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results")
os.makedirs(FIG, exist_ok=True)

NT_COLORS = {"ACH": "#d62728", "GABA": "#1f77b4", "GLUT": "#2ca02c",
             "DA": "#9467bd", "SER": "#ff7f0e", "OCT": "#8c564b", "": "#999999"}


def _layer(t):
    """Coarse layer of the olfactory->MB pathway for layout/coloring."""
    if t == "APL":
        return 4
    if t.startswith("KC"):
        return 3
    if t.startswith("ORN") or t.startswith("HRN"):
        return 0
    if "PN" in t:
        return 2
    return 1  # local neurons / interneurons


def network_figure(headline_path, adj_path, out):
    with open(headline_path) as f:
        h = json.load(f)
    A = np.load(adj_path)
    n = A.shape[0]
    rows = h["rows"]
    types = [r["cell_type"][0] for r in rows]
    nts = [(r["nt"][0] or "").upper() for r in rows]
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                G.add_edge(i, j)
    # Layered layout along the olfactory->MB pathway for readability.
    layer_x = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.2, 4: 4.4}
    layer_nodes = {}
    for i in range(n):
        layer_nodes.setdefault(_layer(types[i]), []).append(i)
    pos = {}
    for lay, members in layer_nodes.items():
        members = sorted(members, key=lambda i: types[i])
        cnt = len(members)
        for k, i in enumerate(members):
            y = 0.5 if cnt == 1 else k / (cnt - 1)
            jitter = 0.18 * np.sin(k * 2.399)  # spread KC blob horizontally
            pos[i] = (layer_x[lay] + (jitter if lay == 3 else 0), y)
    colors = [NT_COLORS.get((nt.split(",")[0] if nt else ""), "#999999") for nt in nts]
    sizes = [620 if types[i] == "APL" else (90 if types[i].startswith("KC") else 300)
             for i in range(n)]
    plt.figure(figsize=(13, 10))
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=6, width=0.4,
                           edge_color="#888888", alpha=0.4,
                           connectionstyle="arc3,rad=0.06")
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors,
                           edgecolors="black", linewidths=0.4)
    # label only the non-KC nodes + the APL, to keep it readable
    lbl = {i: types[i] for i in range(n) if not types[i].startswith("KC")}
    lbl.update({i: "" for i in range(n) if types[i].startswith("KC")})
    nx.draw_networkx_labels(G, pos, labels=lbl, font_size=6)
    handles = [plt.Line2D([0], [0], marker="o", color="w", label=k,
                          markerfacecolor=v, markersize=9)
               for k, v in NT_COLORS.items() if k]
    plt.legend(handles=handles, title="neurotransmitter (FAFB)", loc="upper right",
               fontsize=8)
    # pathway layer captions
    caps = {0.0: "ORN/HRN\n(receptor)", 1.0: "local neurons\n(antennal lobe)",
            2.0: "projection\nneurons", 3.2: "Kenyon cells\n(89x KCg-m)",
            4.4: "APL\n(feedback)"}
    for x, c in caps.items():
        plt.text(x, -0.12, c, ha="center", va="top", fontsize=9, fontweight="bold")
    plt.ylim(-0.25, 1.08)
    plt.title(f"Conserved olfactory→mushroom-body circuit (N={n}, {int(A.sum())} edges)\n"
              f"directed induced subgraph IDENTICAL across {', '.join(h['triple'])}  "
              f"(89 KCg-m unlabeled; small dots)", fontsize=11)
    plt.axis("off"); plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
    print("wrote", out)


def frontier_figure(frontier_path, typed_path, out):
    fr = json.load(open(frontier_path)) if os.path.exists(frontier_path) else {}
    ty = json.load(open(typed_path))
    struct_n = 37
    sp = os.path.join(RES, "headline_circuit.json")
    if os.path.exists(sp):
        struct_n = json.load(open(sp))["N"]
    labels = ["independent set\n(empty graph)", "out-star\n(broadcast hub)",
              "structural\ncircuit", "cell-type\nconserved circuit"]
    vals = [fr.get("tier0_independent_set_min", 20000),
            fr.get("tier1_outstar_N", 772), struct_n, ty["N"]]
    meaning = ["trivial", "trivial-ish", "topological only", "biological + exact"]
    colors = ["#cccccc", "#bbbbbb", "#7aa6c2", "#2ca02c"]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, vals, color=colors, edgecolor="black")
    plt.yscale("log")
    plt.ylabel("N (matched neurons, log scale)")
    for b, v, mlab in zip(bars, vals, meaning):
        plt.text(b.get_x() + b.get_width() / 2, v * 1.12, f"{v}\n({mlab})",
                 ha="center", va="bottom", fontsize=8)
    plt.ylim(top=vals[0] * 4)
    plt.title("The degeneracy frontier: N vs. structural meaning\n"
              "literal max-N is degenerate; we report the largest biologically "
              "meaningful point")
    plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    network_figure(os.path.join(RES, "headline_typed.json"),
                   os.path.join(RES, "headline_typed_adjacency.npy"),
                   os.path.join(FIG, "circuit_network.png"))
    frontier_figure(os.path.join(RES, "frontier.json"),
                    os.path.join(RES, "headline_typed.json"),
                    os.path.join(FIG, "frontier.png"))
