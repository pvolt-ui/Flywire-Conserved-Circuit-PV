# A Sex- and Region-Invariant Olfactory → Mushroom-Body Circuit

### Conserved across FAFB, BANC, and MCNS

**Summary.** I identified a directed induced subgraph with 169 neurons and 1,045 synaptic edges that is exactly isomorphic across three independent *Drosophila* connectomes: FAFB v783 (female brain), BANC v626 (female brain + nerve cord), and MCNS v0.9 (male CNS) (FAFB connectome: Dorkenwald et al. 2024; Schlegel et al. 2024). The adjacency matrices are byte-identical and VF2 confirms the isomorphism. All 169 matched neurons share the same annotated cell type across datasets. A type-constrained null model never reproduced the wiring (0/10,000 trials; p < 10⁻⁴). The circuit corresponds to the canonical olfactory associative-memory pathway of the mushroom body (Li et al. 2020) and is conserved across sex and CNS region.

**Biological analysis below uses FAFB v783, the curated female-brain connectome. Cell-type names, neurotransmitter annotations, and circuit interpretation are anchored on FAFB, while conservation is tested across FAFB, BANC, and MCNS.**

## The conserved circuit

The matched neurons form an olfactory-to-memory pathway:

**sensory receptor neurons → antennal-lobe projection and local neurons → Kenyon cells ↔ APL global feedback**

![Figure 1. The conserved 169-neuron circuit as a directed network graph, identical across FAFB, BANC, and MCNS. Nodes are colored by neurotransmitter and arranged by pathway layer.](figures/circuit_network.png)

*Figure 1. The conserved 169-neuron circuit as a directed network graph, identical across FAFB, BANC, and MCNS (`figures/circuit_network.png`).*

Two additional mushroom-body-associated neurons, MBON30 and CRE075, are also matched. Within this induced subgraph they project into APL (MBON30 → APL and MBON30 → CRE075 → APL). They do not provide a KC → MBON output stage here. The conserved core is therefore the ORN → PN/LN → KC ↔ APL feedback loop.

| Layer            | Example cell types                  |   n |
| ---------------- | ----------------------------------- | --: |
| Sensory          | ORN_*, HRN_VP4                      |  37 |
| Antennal-lobe LN | lLN1_bc, lLN2F/T/X, ALIN1           |  23 |
| Projection       | VP1m_l2PN, VP1d+VP4_l2PN1, VC3_adPN |   3 |
| Memory           | KCg-m, KCab-p, KCg-d                | 103 |
| Feedback         | APL                                 |   1 |
| MB-associated    | MBON30, CRE075                      |   2 |

The neurotransmitter organization is consistent with known mushroom-body circuitry: a cholinergic ORN → PN → KC feedforward spine, a single GABAergic APL, and glutamatergic MBON30 and CRE075. APL is the highest-degree node (108 in, 106 out) and forms 448 reciprocal pairs within the circuit. This architecture supports global inhibition and sparse, decorrelated odor coding (Lin et al. 2014; Amin et al. 2020).

## Significance

Many neurons share the same cell type, so a random same-typed selection might reproduce the circuit by chance. I tested this with a type-constrained random-matching null. For each of the 169 matched rows, I selected a random neuron of the required cell type in BANC or MCNS and rebuilt the induced subgraph.

Across 10,000 draws per dataset, the exact wiring was reproduced 0 times (p < 10⁻⁴). The best random attempt matched only about half of the edges, whereas the real correspondence matches all 1,045 edges.

I also shuffled cell-type labels while preserving type frequencies and reran the identical growth procedure. Across 100 replicates, the conserved 2-core circuit collapsed to max 9 / mean 1.0 nodes versus the real 169 (0/100 ≥ 169, p ≈ 0.01).

The conserved wiring is therefore unlikely to arise from cell-type degeneracy or from the growth procedure itself.

## Population-level corroboration

Population-level connectivity statistics are consistent across datasets: P(PN→KCg-m) = 0.023–0.031, APL→KCg-m coverage = 0.89–1.0, and KCg-m→APL coverage = 0.70–1.0. These values support conservation beyond the matched subgraph itself.

## Degeneracy frontier

The literal objective is degenerate because large independent sets and stars are automatically isomorphic. I measured this directly: a common independent set of ≥ 20,000 neurons and a common induced out-star of 772 neurons both exist and are both valid under the literal rule. I therefore report the largest weakly connected, cell-type-conserved 2-core circuit.

A structural-only search finds a 37-neuron exact isomorphism with 0/37 cell-type agreement. The reported circuit contains 169 neurons with 169/169 cell-type agreement and exact wiring conservation across all three connectomes. An expanded Kenyon-cell fan yields a VF2-verified lower bound of ≥ 221 conserved neurons.

The 37-neuron result shows that topology alone does not establish homology. The 169-neuron circuit combines exact structural conservation with cell-type conservation and statistical significance.

## Observations and hypothesis

Identical wiring and cell types appear in two female nervous systems and one male nervous system reconstructed by different pipelines, indicating strong developmental conservation. APL forms the structural center of the circuit and provides the feedback architecture associated with sparse, decorrelated odor representations.

![Figure 2. Constituent neurons of the conserved circuit rendered from Codex 3D meshes in FAFB, colored by pathway layer.](figures/circuit_3d.png)

*Figure 2. A representative subset of the circuit's neurons rendered from Codex 3D skeletons in FAFB, colored by pathway layer (`figures/circuit_3d.png`).*

I hypothesize that the ORN → PN/LN → KC ↔ APL motif is a conserved computational primitive for associative learning. The computation is conserved even if individual PN→KC pairings remain variable across animals (Caron et al. 2013).

**Data note.** The released edge lists contain only source and target columns and no synapse weights. I therefore use every directed connection as provided, remove self-loops, and collapse duplicate ordered pairs.

**References**

1. Dorkenwald et al. (2024) *Nature* 634:124.
2. Schlegel et al. (2024) *Nature* 634:139.
3. Li et al. (2020) *eLife* 9:e62576.
4. Lin et al. (2014) *Nature Neuroscience* 17:559.
5. Caron et al. (2013) *Nature* 497:113.
6. Amin et al. (2020) *eLife* 9:e56954.