
# Largest Conserved Neuronal Circuit Across FlyWire Connectomes

**Result in one line.**

I found the canonical olfactory → mushroom-body associative-memory pathway as a directed induced subgraph with 169 neurons and 1,045 edges. The subgraph is exactly isomorphic across three independent connectomes. VF2 verifies the match and the adjacency matrices are byte-identical. All 169 matched neurons share the same annotated cell type. A type-constrained null model reproduced the result 0 times in 10,000 trials (p < 10⁻⁴). The datasets are FAFB, BANC, and MCNS. The circuit is therefore conserved across sex and CNS region.

`network.csv` contains 169 matched neuron IDs across FAFB, BANC, and MCNS.

`science.md` contains the scientific report.

## Verify the result

```bash
python verify_artifact.py
```

This checks weak connectivity, the 2-core property, and 169/169 cell-type concordance from the committed results.

---

# 1. Problem and the key assumption

The challenge asks for the largest set of neurons whose directed induced subgraphs are mutually isomorphic across at least three datasets, ignoring edge weights.

Taken literally, the objective is degenerate.

Any set of mutually non-adjacent neurons induces an empty graph. Empty graphs are trivially isomorphic. Large cliques have the same problem. I measured both effects. A common independent set with more than 20,000 neurons exists. A common out-star with 772 neurons also exists. Both satisfy the literal objective but are biologically uninformative.

I therefore report the largest subgraph that satisfies two additional requirements:

1. It is a weakly connected, richly connected core. I enforce an undirected 2-core, so every node has total degree at least 2 and no leaves remain.
2. Every matched neuron has the same annotated cell type in all three datasets.

Cell-type agreement is a constraint that I impose. It is not a discovery.

Under that constraint, I find a 169-node circuit with identical wiring across all three connectomes. The result is statistically significant. For readers interested only in size, I also report a VF2-verified lower bound of at least 221 neurons. A naive interchangeable-slot count gives 707, but that construction is not isomorphic and is not reported as a result.

## Degeneracy frontier

| Tier | Structure | N | Cell-type concordant? | Verdict |
|---|---|---:|---|---|
| 0 | Common independent set | ≥ 20,000 | — | Trivial |
| 1 | Common induced out-star | 772 | — | Trivial-ish |
| 2a | Largest structural-only induced circuit | 37 | 0 / 37 | Topological coincidence |
| 2b | Cell-type-conserved rich 2-core circuit | 169 | 169 / 169 | Reported result |
| 2c | Maximal cell-type-conserved set | ≥ 221 | All | Verified lower bound |

Tier 2a is important. The 37-node structural match is exactly isomorphic, but none of the matched neurons share cell type.

Topological isomorphism alone does not establish biological homology.

The 169-node circuit is itself a valid structural match. The cell-type constraint does not enlarge the result. Adding a constraint can only reduce the candidates available during growth. The constraint helps steer the search toward a biologically coherent and denser region. It also allows a meaningful significance test.

The difference between 37 and 169 comes from different search procedures. The 37-node result comes from a degree-signature seed sweep. The 169-node result comes from APL-seeded growth. The gap is not evidence that the constraint improves the structural optimum.

# 2. Datasets

I use FAFB, BANC, and MCNS because all three contain a full central brain. They also span both sexes.

FAFB is female brain.

BANC is female brain plus nerve cord.

MCNS is male CNS.

MANC contains only nerve cord. MAOL contains only optic lobe.

| Dataset | Sex / region | Nodes | Directed edges |
|---|---|---:|---:|
| FAFB v783 | Female brain | 138,584 | 3,732,460 |
| BANC v626 | Female brain + nerve cord | 112,885 | 2,676,592 |
| MCNS v0.9 | Male CNS | 165,820 | 6,239,094 |

# 3. Method

## Cleaning

I ignore edge weights as required. The released edge lists contain only source and target columns, so no synapse threshold can be applied.

I remove self-loops, collapse duplicate ordered pairs, and relabel root IDs to contiguous indices.

## Graph representation

I store CSR in- and out-adjacency structures together with a sorted packed-edge array. This supports O(log M) vectorized edge-existence checks for induced-subgraph queries on graphs with millions of edges.

I validated the implementation against NetworkX.

## Conserved-circuit search

I grow a common induced subgraph from a seed triple.

**Correctness by construction.**

I add a node triple only when its in- and out-attachment pattern to the current matched set is the same bit string in all three graphs.

The key invariant is simple. If three adjacency matrices are identical and I append the same row and the same column to each matrix, the matrices remain identical. The matched ordering therefore defines the isomorphism throughout growth.

**Biological constraint.**

Every added triple must share the same cell type across all three datasets.

**Determinism.**

I sort the frontier and choose the highest-degree representative for each signature. Ties break by index. The procedure contains no randomness and produces the same result every run.

**Circuit extraction.**

After growth, I take the 2-core and then the largest weakly connected component.

**Seed.**

The reported circuit starts from APL, the mushroom-body global-feedback neuron.

## Independent verification

I verify the final correspondence in two ways.

1. The induced adjacency matrices are byte-identical.
2. Directed VF2 isomorphism succeeds for every pair of datasets.

WL hashing is used only for candidate bucketing. All guarantees come from exact verification.

## Significance

I use a type-constrained random-matching null model.

For each row, I select a random same-typed neuron in BANC and MCNS. I then test whether the induced wiring reproduces the FAFB template.

Across 10,000 trials per dataset, the exact wiring appears 0 times.

p < 10⁻⁴.

The best random trial reproduces only about half of the edges.

I also test the search procedure itself. I keep the real graphs and the real APL seed. I then shuffle cell-type labels within each dataset while preserving type frequencies. This destroys the relationship between type and wiring.

Across 100 replicates, the conserved 2-core circuit collapses to a maximum of 9 nodes and a mean of 1.0 nodes.

The real result contains 169 nodes.

No shuffled run reaches 169.

0 / 100 ≥ 169.

p ≈ 0.01.

The raw common subgraph still grows large after shuffling, with mean full-N ≈ 216. The signal is therefore not that a common subgraph exists. The signal is the richly connected conserved circuit.

## Population-level corroboration

I also measure connection statistics across the full populations of each cell type.

P(PN → KCg-m) ≈ 0.023–0.031.

APL → KC coverage ≈ 0.89–1.0.

These values agree closely across datasets.

# 4. Maximal set

The headline result keeps one representative per signature and cell type.

Many neurons share the same scaffold-attachment signature. Hundreds of KCg-m neurons, for example, connect to APL in the same way. They are interchangeable candidates within the conserved structure.

A naive count suggests 707 neurons. That count ignores the KC↔KC block and is not isomorphic as constructed.

I therefore build the expanded set explicitly and verify it.

I start from the already identical 66-node scaffold.

I then add KC triples as an independent fan. Each added KC is non-adjacent to every previously added KC within its own graph. The KC↔KC block therefore remains empty in all three datasets.

I then re-check byte identity and VF2 isomorphism.

The verified result contains 221 neurons and 1,056 edges.

This is a genuine lower bound on the largest cell-type-conserved circuit.

The naive count overestimates the size by roughly 3.2×. I report only the verified value.

# 5. Reproduction

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

python download_data.py
python run.py

python src/null_model.py 10000
python src/null_grower.py 100
python src/connectivity_stats.py
python src/maximal_set.py

python src/make_figures.py && python src/make_3d.py

python verify_artifact.py
python verify_submission.py
```

# 6. Repository layout

```
network.csv                 # deliverable: 3 columns (FAFB, BANC, MCNS) x 169 matched neuron IDs
science.md                  # deliverable: one-page scientific report
run.py                      # entry point: clean graphs -> conserved circuit -> network.csv + results/
verify_artifact.py          # self-contained check (committed artifacts only, no data download)
verify_submission.py        # independent check against the raw edge lists
download_data.py            # fetch Codex cell-type / neurotransmitter metadata
src/                        # io_utils, graph_core, iso_utils, match_engine, annotate,
                            # null_model, null_grower, connectivity_stats, maximal_set,
                            # make_figures, make_3d, test_core  (+ legacy find_circuit*)
results/                    # headline_typed.json, null_model.json, null_grower.json,
                            # maximal_set.json, connectivity_stats.json, frontier.json, adjacency .npy
figures/                    # circuit_network.png, frontier.png, circuit_3d.png
data/clean/                 # cached cleaned graphs (.npy)
data/meta/                  # Codex cell-type / neurotransmitter tables
```

# 7. Limitations

The correspondence preserves both wiring and cell type. A FAFB KCg-m maps to a KCg-m in MCNS with identical induced wiring. I do not claim that individual cells are identical across animals. The result concerns cross-animal homology.

Some BANC and MCNS cell-type and neurotransmitter labels are predicted. FAFB labels are curated. I use the published annotations.

The growth procedure is greedy. It is not a proof of the global optimum. Finding the exact maximum is NP-hard.

The reported isomorphisms are exact. Every reported match is VF2-verified.
