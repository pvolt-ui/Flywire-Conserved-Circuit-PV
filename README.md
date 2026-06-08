# Largest Conserved Neuronal Circuit Across Three FlyWire Connectomes

Result in one line: the canonical olfactory → mushroom-body associative-memory pathway — a directed induced subgraph of N = 155 neurons / 1,074 edges — is exactly isomorphic (VF2-verified, byte-identical adjacency) across three independent connectomes, with 155/155 matched neurons sharing cell type: female brain (FAFB), female brain + nerve cord (BANC), and male CNS (MCNS). It is therefore conserved across sex and across CNS region/specimen.

`network.csv` — 3 columns (FAFB, BANC, MCNS) × 155 rows (matched neuron IDs). `science.md` — the one-page scientific report.

---

## 1. Problem and the assumption that matters most

The task asks for the largest set of N neurons whose directed induced subgraphs are mutually isomorphic across ≥ 3 of the 5 datasets, ignoring edge weights.

Taken literally, the objective is degenerate. Any N mutually non-adjacent neurons induce the empty graph, which is trivially isomorphic to any other empty graph; likewise any clique. So “maximize N” alone is won by biologically meaningless structures. We measured this directly (the frontier below): a common independent set of ≥ 20,000 neurons and a common out-star of 772 neurons both exist and are both “valid” under the literal rule.

We therefore make the assumption the problem is really probing: a “circuit” must be structurally non-trivial _and_ biologically meaningful. Our reported answer is the largest subgraph that is simultaneously (i) a connected directed circuit (every node has total degree ≥ 2; no dangling leaves — the graph 2-core), and (ii) biologically homologous — each matched neuron is the same annotated cell type in all three datasets. This converts a degenerate optimization into a real scientific question and is consistent with the challenge’s stated preference for *methodological rigor over raw size*.

### The degeneracy frontier (we report the rightmost, meaningful point)

| Tier | Structure | N | Cell-type concordant? | Verdict |
|---|---|---|---|---|
| 0 | Common independent set (empty graph) | ≥ 20,000 | — | trivial |
| 1 | Common induced out-star (1 hub → n silent leaves) | 772 | — | trivial-ish |
| 2a | Largest structural-only induced circuit | 37 | 0 / 37 | topological coincidence |
| 2b | Largest cell-type-constrained conserved circuit | 155 | 155 / 155 | reported answer |

Tier 2a is important: a purely topological match of 37 neurons is exactly isomorphic yet zero of its neurons are the same cell type across datasets. *Topological isomorphism alone does not imply biological homology.* Requiring cell-type identity is what makes Tier 2b a genuine conserved circuit — and, strikingly, the biological constraint lets the circuit grow larger (155 > 37), because real conserved wiring is more extensive than coincidental wiring.

## 2. Datasets and which three we chose

We chose FAFB, BANC, MCNS — the three datasets that all contain a full central brain, and that span both sexes (FAFB ♀, BANC ♀, MCNS ♂). This makes any conserved circuit a statement about sex- and region-invariant wiring. (MANC is nerve-cord only; MAOL is optic-lobe only — they share less brain anatomy.)

After cleaning, graph sizes match the official Codex neuron counts, validating the pipeline:

| Dataset | Sex / region | Nodes | Directed edges |
|---|---|---|---|
| FAFB v783 | ♀ brain | 138,584 | 3,732,460 |
| BANC v626 | ♀ brain + nerve cord | 112,885 | 2,676,592 |
| MCNS v0.9 | ♂ CNS | 165,820 | 6,239,094 |

## 3. Method

Cleaning (`src/io_utils.py`). Per the rules we ignore synapse weights. We drop self-loops, collapse parallel edges, and relabel the 18-digit root IDs (small integer body IDs for MCNS) to contiguous indices cached as `.npy`.

Graph core (`src/graph_core.py`). CSR in/out adjacency plus a sorted packed-edge array giving O(log M) vectorized edge-existence tests — the workhorse for induced-subgraph queries at this scale. Validated against NetworkX ground truth (`src/test_core.py`).

Conserved-circuit search (`src/match_engine.py`). We grow a common induced subgraph across all three graphs simultaneously from a seed triple:

- *Correctness by construction.* We only ever add a node-triple whose in/out attachment pattern to the already-matched set is the identical bit-string in all three graphs. Appending an identical row+column to identical adjacency matrices keeps them identical, so the induced subgraphs are isomorphic at every step (the matched ordering *is* the isomorphism).
- *Biological constraint.* The added triple must also share the same cell type in all three datasets — enforcing homology, not coincidence.
- *Vectorized.* Attachment signatures for an entire candidate frontier are computed with one batched `searchsorted`, making each growth step fast on multi-million-edge graphs.
- *Circuit extraction.* From the grown subgraph we take the 2-core (removes degree-1 leaves) and its largest weakly-connected component — a real circuit.
- *Seeding.* We seed from cell types present in all three datasets (4,125 of them) and keep the seed that yields the largest circuit. The winner seeds from APL.

Independent verification (`src/iso_utils.py`). The final 155-node correspondence is confirmed two ways: (a) the three induced adjacency matrices are byte-for-byte identical, and (b) exact VF2 directed isomorphism (`networkx.DiGraphMatcher`) passes for all pairs. WL-hashing is used only to *bucket* candidates; every guarantee comes from VF2.

## 4. Reproduce

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy pandas scipy networkx matplotlib

# 1) clean + profile the five graphs
python src/profile_graphs.py
# 2) download per-dataset metadata (cell type / neurotransmitter) from Codex GCS
#    (see src/annotate.py header for the exact GCS paths used)
# 3) find the conserved circuit (writes network.csv + results/headline_typed.json)
python src/find_circuit_typed.py FAFB BANC MCNS
python src/grow_apl.py            # grows the APL-seeded circuit to N=155
# 4) figures
python src/make_figures.py        # network graph + degeneracy frontier
python src/make_3d.py             # 3D skeleton morphologies (Codex SWCs)
```

Metadata files (`data/meta/`) are pulled from `storage.googleapis.com/flywire-data/codex/data/<ds>/<ver>/`. The raw edge lists are the five provided CSVs at the repo root.

## 5. Repository layout

```
network.csv                 # DELIVERABLE: 3 cols (FAFB,BANC,MCNS) x 155 matched neuron IDs
science.md                  # DELIVERABLE: one-page scientific report
README.md                   # this file
src/                        # io_utils, graph_core, iso_utils, match_engine, annotate,
                            # find_circuit_typed, grow_apl, make_figures, make_3d, test_core
results/                    # headline_typed.json, frontier.json, adjacency .npy
figures/                    # circuit_network.png, frontier.png, circuit_3d.png
data/clean/                 # cached cleaned graphs (.npy)
data/meta/                  # Codex cell-type / neurotransmitter tables
```

## 6. Honest limitations

- The correspondence is type- and wiring-preserving, i.e. a FAFB KCg-m maps to *a* KCg-m in MCNS with identical induced wiring — not a claim of identical individual cells (impossible across specimens). This is the biologically correct notion of homology across animals.
- BANC/MCNS cell types and neurotransmitters are partly predicted; FAFB is curated. Concordance uses these published labels.
- The growth heuristic is greedy (not a proof of the global maximum). N = 155 is a strong, verified lower bound on the largest cell-type-conserved circuit; the exact maximum is NP-hard. All reported isomorphisms are nonetheless exact and verified.
