# A Sex- and Region-Invariant Olfactory → Mushroom-Body Circuit

### Conserved (exactly isomorphic) and statistically significant across the FAFB, BANC and MCNS connectomes

**Summary.** From connectivity alone we identified a directed induced subgraph of **169 neurons / 1,045 synaptic edges** that is **exactly isomorphic** (byte-identical adjacency, VF2-verified) across three independent *Drosophila* connectomes — female brain (FAFB v783), female brain + nerve cord (BANC v626), and male CNS (MCNS v0.9). Every matched neuron is the same annotated cell type in all three datasets. It is the canonical olfactory associative-memory pathway, conserved across sex and CNS region. A null model shows this exact correspondence is **not reproducible by chance** (p < 10⁻⁴; §3).

**What is a constraint, and what is a finding.** We *require* matched neurons to share cell type — so "169/169 cell-type concordant" is an imposed constraint, not a discovered fact. The non-trivial finding is that, under that constraint, **a 169-node weakly-connected circuit with byte-identical directed wiring exists in all three connectomes, and that this exact wiring is statistically significant rather than an artifact of having many interchangeable same-typed neurons.**

**The circuit (Fig. 1).** The matched neurons form the early-olfactory-to-memory cascade:
**sensory receptor neurons → antennal-lobe projection + local neurons → Kenyon cells ↔ APL global feedback.**
Two further mushroom-body-associated neurons (MBON30, CRE075) are also matched and weakly connected — but within this induced subgraph they feed *into* APL (MBON30 → APL, MBON30 → CRE075 → APL), they do **not** read out the Kenyon cells. We therefore do not claim a complete KC → MBON output stage; the conserved core is the ORN → PN/LN → KC ↔ APL feedback loop.

| Layer | Example cell types (FAFB) | n | NT |
|---|---|---|---|
| Sensory | `ORN_*` (DA1, DM1/2, VA2, VC3, VM5…), `HRN_VP4` | 37 | ACh |
| Antennal-lobe LN | `lLN1_bc`, `lLN2F/T/X`, `ALIN1` | 23 | GABA / 5-HT / Glu |
| Projection | `VP1m_l2PN`, `VP1d+VP4_l2PN1`, `VC3_adPN` | 3 | ACh |
| Memory | `KCg-m` (γ-main), `KCab-p`, `KCg-d` Kenyon cells | 103 | ACh |
| Feedback | `APL` (Anterior Paired Lateral) | 1 | GABA |
| MB-assoc. (→APL) | `MBON30`, `CRE075` | 2 | Glu |

Neurotransmitters are internally coherent: a cholinergic feedforward spine (ORN → PN → KC), shaped by GABAergic / serotonergic lateral inhibition and a single GABAergic global-feedback neuron (APL); two glutamatergic MB-associated neurons (MBON30, CRE075) additionally feed *into* APL within this subgraph. APL is the highest-degree node (108 in / 106 out; 448 reciprocal pairs within the circuit) — the structural basis for the negative feedback that sparsens and decorrelates odor codes (Lin et al. 2014; Amin et al. 2020).

## Significance — the conserved wiring is not expected by chance

The fair objection is that with thousands of interchangeable same-typed neurons per dataset (≈ 2,200 KCg-m in FAFB alone), *some* same-typed selection might reproduce this sparse wiring by accident. We tested this directly with a **type-constrained random-matching null**: fixing FAFB's induced adjacency as the template, we drew, for each of the 169 rows, a *random* neuron of the required cell type in BANC / MCNS, rebuilt the induced subgraph, and compared. Over **10,000 draws per dataset**:

| Test | Reproduces exact wiring | p | Best edge-Jaccard of 10,000 draws |
|---|---|---|---|
| Full 169-node circuit (BANC) | 0 / 10,000 | < 10⁻⁴ | 0.57 |
| Full 169-node circuit (MCNS) | 0 / 10,000 | < 10⁻⁴ | 0.53 |
| 66-node scaffold only (BANC) | 0 / 10,000 | < 10⁻⁴ | 0.69 |
| 66-node scaffold only (MCNS) | 0 / 10,000 | < 10⁻⁴ | 0.67 |

Not one random same-typed assignment — of 10,000, in either dataset — reproduces the circuit, and the *best* random attempt matches barely half of its 1,045 edges, whereas the real matched circuit matches all of them (Jaccard = 1.0). The same holds for the projection/local/feedback scaffold considered alone. **The exact correspondence is therefore a real biological signal, not a consequence of cell-type degeneracy.**

## Population-level corroboration (non-circular)

Within the matched circuit, per-type wiring is identical across datasets *by construction*. As an independent check we computed connection statistics over the **entire neuron populations** of each type in each full connectome (the prediction we raised, now run):

| Statistic | FAFB | BANC | MCNS |
|---|---|---|---|
| P(PN → KCg-m) | 0.031 | 0.023 | 0.031 |
| APL → KCg-m coverage | 1.00 | 0.89 | 1.00 |
| KCg-m → APL coverage | 1.00 | 0.70 | 1.00 |

The sparse PN→KC convergence rate (≈ 2–3%) and the near-universal APL coverage agree across all three connectomes — the conserved motif holds at the population level, even though, per Caron et al. (2013), the *specific* PN→KC partners are idiosyncratic. (Lower BANC coverage tracks its lower reconstruction completeness.)

## The degeneracy frontier

Taken literally, "maximize N of mutually isomorphic induced subgraphs" is degenerate: any independent set (empty graph) or clique is trivially isomorphic. We therefore report a *frontier* and its meaningful point.

| Tier | Structure | N | Verdict |
|---|---|---|---|
| 0 | Common independent set (empty graph) | ≥ 20,000 | trivial |
| 1 | Common induced out-star | 772 | trivial-ish |
| 2a | Largest structural-only circuit | 37 (0/37 same type) | topological coincidence |
| **2b** | **Cell-type-conserved rich 2-core circuit** | **169** | **reported headline (significant, p < 10⁻⁴)** |
| 2c | Maximal cell-type-conserved set (KC fan expanded, VF2-verified) | ≥ 221 | size-maximal verified lower bound |

Tier 2a vs 2b is the key contrast: a purely topological match of 37 neurons is exactly isomorphic yet **0/37 are the same cell type** — topological isomorphism alone is not homology. The 169-node headline circuit is *itself* a valid structural match (byte-identical regardless of labels), so the cell-type constraint does **not** enlarge it — a constraint can only restrict the eligible candidates at each step. Rather, it *guides* the search toward a biologically coherent, denser region and lets us interpret the match as a conserved circuit and then test its significance; the 37-vs-169 gap is an artifact of different seeds (degree-signature sweep vs. APL-seeded growth), not a benefit of the constraint. Tier 2c addresses the literal "largest" objective with a *verified* number: starting from the 66-node scaffold we add Kenyon cells as an independent fan and **re-confirm byte-identity + VF2 isomorphism** across all three datasets, giving a conserved set of **≥ 221** neurons. (A naive interchangeable-slot count gives 707, but that ignores the KC↔KC block and is not isomorphic as built — it overcounts ≈ 3.2×; we report only the verified figure.)

## Observations

1. **Developmental canalization.** Identical wiring *and* cell types in two female nervous systems and one male, each reconstructed by a different pipeline, indicate a hard-wired circuit conserved across sex and body region. The conserved core spans multiple sensory modalities — thermo/hygrosensory VP projection neurons and olfactory PNs both converge on the mushroom body.
2. **APL feedback is the structural heart.** APL is the highest-degree node and is reciprocally connected to the Kenyon-cell pool — the anatomical basis for the global inhibition that produces sparse, decorrelated odor codes for selective learning.
3. **Topology ≠ homology.** The 37-neuron structural-only match (0/37 concordant) versus the 169-neuron type-conserved circuit shows that a coincidental isomorphism is not a conserved circuit; homology must be imposed and then *tested* for significance — which we do.

**Hypothesis.** The ORN → PN/LN → KC ↔ APL motif is a conserved computational primitive: sparsen sensory input and regulate it by global feedback inhibition, the substrate for selective associative learning. The motif is under strong stabilizing constraint while individual PN→KC partners remain free (Caron et al. 2013) — conserved computation, idiosyncratic instances.

**Data note.** The provided edge lists contain no synapse weights (two columns: source, target), so per the rules we use each released directed connection as-is; no weight threshold is applied or applicable. We drop self-loops and collapse any duplicate ordered pairs. BANC/MCNS cell types and neurotransmitters are partly predicted (FAFB is curated); concordance uses these published labels.

**References.** 1. Dorkenwald et al. (2024) *Neuronal wiring diagram of an adult brain.* Nature 634:124. 2. Schlegel et al. (2024) *Whole-brain annotation… of Drosophila.* Nature 634:139. 3. Li et al. (2020) *Connectome of the adult Drosophila mushroom body.* eLife 9:e62576. 4. Lin et al. (2014) *Sparse, decorrelated odor coding…* Nat. Neurosci. 17:559. 5. Caron et al. (2013) *Random convergence of olfactory inputs…* Nature 497:113. 6. Amin et al. (2020) *Localized inhibition in the Drosophila mushroom body.* eLife 9:e56954. 7. Marin et al. (2020) *Thermo/hygrosensory neurons of the adult Drosophila brain.* Curr. Biol. 30:3167.
