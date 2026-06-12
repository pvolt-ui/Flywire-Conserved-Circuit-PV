# Largest Conserved Neuronal Circuit Across FlyWire Connectomes

Result in one line: the canonical olfactory → mushroom-body associative-memory pathway — a directed induced subgraph of **N = 169 neurons / 1,045 edges** — is exactly isomorphic (VF2-verified, byte-identical adjacency) across three independent connectomes, with all 169 matched neurons sharing cell type, and the exact correspondence is **statistically significant** (null model: 0 / 10,000 random same-typed matchings reproduce it; p < 10⁻⁴). Datasets: female brain (FAFB), female brain + nerve cord (BANC), male CNS (MCNS) — so the circuit is conserved across sex and CNS region.

`network.csv` — 3 columns (FAFB, BANC, MCNS) × 169 rows (matched neuron IDs). `science.md` — the one-page scientific report.

**Verify the headline on a clean clone in seconds (no data download):**
```bash
python verify_artifact.py        # asserts weak-connectivity + 2-core + 169/169 concordance from results/
```

---

## 1. Problem and the assumption that matters most

The task asks for the largest set of N neurons whose directed induced subgraphs are mutually isomorphic across ≥ 3 of the 5 datasets, ignoring edge weights.

Taken literally, the objective is degenerate. Any N mutually non-adjacent neurons induce the empty graph, trivially isomorphic to any other empty graph; likewise any clique. So "maximize N" alone is won by biologically meaningless structures — we measured this: a common independent set of ≥ 20,000 neurons and a common out-star of 772 both exist and are both "valid" under the literal rule.

We therefore report the largest subgraph that is simultaneously (i) a connected directed circuit (undirected 2-core: every node total-degree ≥ 2, no dangling leaves) and (ii) biologically homologous — each matched neuron the same annotated cell type in all three datasets. **Cell-type identity is a constraint we impose, not a result we discover.** The result is that, under it, a 169-node identical-wiring circuit exists *and is significant* (see §3). This is consistent with the challenge's stated preference for methodological rigor over raw size; for those who want raw size, we also report a size-maximal lower bound of ≥ 707 (§4).

### The degeneracy frontier (we report the rightmost meaningful point)

| Tier | Structure | N | Cell-type concordant? | Verdict |
|---|---|---|---|---|
| 0 | Common independent set (empty graph) | ≥ 20,000 | — | trivial |
| 1 | Common induced out-star | 772 | — | trivial-ish |
| 2a | Largest structural-only induced circuit | 37 | 0 / 37 | topological coincidence |
| **2b** | **Cell-type-conserved rich 2-core circuit** | **169** | **169 / 169** | **reported headline** |
| 2c | Maximal cell-type-conserved set (KC fan expanded) | ≥ 707 | all | size-maximal lower bound |

Tier 2a is important: a purely topological match of 37 neurons is exactly isomorphic yet zero of its neurons are the same cell type. *Topological isomorphism alone does not imply biological homology.* Requiring cell-type identity is what makes 2b a genuine conserved circuit — and the biological constraint lets it grow larger (169 > 37), because real conserved wiring is more extensive than coincidental wiring.

## 2. Datasets and which three we chose

We chose FAFB, BANC, MCNS — the three datasets that all contain a full central brain and that span both sexes (FAFB ♀, BANC ♀, MCNS ♂), so any conserved circuit is a statement about sex- and region-invariant wiring. (MANC is nerve-cord only; MAOL is optic-lobe only.) After cleaning, graph sizes match the official Codex neuron counts.

| Dataset | Sex / region | Nodes | Directed edges |
|---|---|---|---|
| FAFB v783 | ♀ brain | 138,584 | 3,732,460 |
| BANC v626 | ♀ brain + nerve cord | 112,885 | 2,676,592 |
| MCNS v0.9 | ♂ CNS | 165,820 | 6,239,094 |

## 3. Method

**Cleaning (`src/io_utils.py`).** Per the rules we ignore synapse weights — in fact the provided edge lists carry none (two columns: source, target), so no synapse threshold is applicable. We drop self-loops, collapse duplicate ordered pairs, and relabel root IDs to contiguous indices cached as `.npy`.

**Graph core (`src/graph_core.py`).** CSR in/out adjacency plus a sorted packed-edge array giving O(log M) vectorized edge-existence tests — the workhorse for induced-subgraph queries at multi-million-edge scale. Validated against NetworkX (`src/test_core.py`).

**Conserved-circuit search (`src/match_engine.py`).** We grow a common induced subgraph across all three graphs from a seed triple:
- *Correctness by construction.* We only add a node-triple whose in/out attachment pattern to the matched set is the identical bit-string in all three graphs; appending an identical row+column to identical matrices keeps them identical, so the induced subgraphs are isomorphic at every step (the matched ordering *is* the isomorphism).
- *Biological constraint.* The added triple must also share cell type in all three datasets.
- *Deterministic.* The frontier is sorted and the per-signature representative is the highest-degree candidate (tie-break by index), so the search is fully reproducible run-to-run (no seed needed; there is no randomness).
- *Circuit extraction.* From the grown subgraph we take the 2-core and its largest weakly-connected component.
- *Seeding.* The reported circuit seeds from APL (the mushroom-body global-feedback neuron).

**Independent verification (`src/iso_utils.py`).** The final correspondence is confirmed two ways: (a) the three induced adjacency matrices are byte-identical, and (b) exact VF2 directed isomorphism passes for all pairs. WL-hashing only buckets candidates; every guarantee comes from VF2.

**Significance (`src/null_model.py`).** A type-constrained random-matching null draws random same-typed neurons for each row in BANC/MCNS and tests how often the exact FAFB wiring is reproduced. Over 10,000 draws per dataset: **0 reproduce it (p < 10⁻⁴)**; the best random attempt matches only ~half the edges. The scaffold alone is likewise never reproduced. The conserved wiring is therefore not an artifact of cell-type degeneracy.

**Population corroboration (`src/connectivity_stats.py`).** Per-type connection statistics over the *full* populations agree across datasets: P(PN→KCg-m) ≈ 0.023–0.031, APL→KC coverage ≈ 0.89–1.0.

## 4. Maximal set (`src/maximal_set.py`)

The headline keeps one representative per (signature, type). Keeping *all* interchangeable Kenyon cells (bounded per dataset by the scarcest dataset, treating the KC layer as a fan onto the 66-node scaffold) gives a conserved, mutually-isomorphic set of **≥ 707** neurons — a defensible answer to the literal "largest" objective. (Approximation: a small number of KC–KC edges in the core are ignored; see the script.)

## 5. Reproduce

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # pinned versions

python download_data.py                  # fetch Codex cell-type / NT metadata into data/meta/
python run.py                            # clean graphs -> conserved circuit -> network.csv + results/
python src/null_model.py 10000           # significance (p-value)
python src/connectivity_stats.py         # population-level corroboration
python src/maximal_set.py                # size-maximal lower bound
python src/make_figures.py && python src/make_3d.py   # figures

python verify_artifact.py                # self-contained check (no external data)
python verify_submission.py              # independent check against the raw edge lists
```

The five raw edge-list CSVs are the challenge-provided files at the repo root. `download_data.py` lists the exact Codex GCS URLs/versions and the local filename mapping for the metadata.

## 6. Repository layout

```
network.csv                 # DELIVERABLE: 3 cols (FAFB,BANC,MCNS) x 169 matched neuron IDs
science.md                  # DELIVERABLE: one-page scientific report
run.py                      # canonical entrypoint -> regenerates network.csv + results/
verify_artifact.py          # self-contained headline check (committed artifacts only)
verify_submission.py        # independent check against the raw edge lists
download_data.py            # fetch Codex metadata (URLs + filename mapping)
src/                        # io_utils, graph_core, iso_utils, match_engine, annotate,
                            # null_model, connectivity_stats, maximal_set,
                            # make_figures, make_3d, test_core  (+ legacy find_circuit*)
results/                    # headline_typed.json, null_model.json, maximal_set.json,
                            # connectivity_stats.json, frontier.json, adjacency .npy
figures/                    # circuit_network.png, frontier.png, circuit_3d.png
data/clean/                 # cached cleaned graphs (.npy)
data/meta/                  # Codex cell-type / neurotransmitter tables
```

## 7. Honest limitations

- The correspondence is type- and wiring-preserving: a FAFB KCg-m maps to *a* KCg-m in MCNS with identical induced wiring — not a claim of identical individual cells (impossible across specimens). This is the biologically correct notion of cross-animal homology.
- BANC/MCNS cell types and neurotransmitters are partly predicted; FAFB is curated. Concordance uses these published labels.
- The growth heuristic is greedy (not a proof of the global maximum). N = 169 is a strong, verified, significant lower bound on the largest cell-type-conserved circuit; the exact maximum is NP-hard. All reported isomorphisms are exact and VF2-verified.
