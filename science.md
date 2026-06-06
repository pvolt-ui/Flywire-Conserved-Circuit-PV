# A Sex- and Region-Invariant Olfactory → Mushroom-Body Circuit
### Conserved (exactly isomorphic) across the FAFB, BANC and MCNS connectomes

**Summary.** From connectivity alone, validated against Codex cell-type annotations, we identified a directed induced subgraph of **155 neurons / 1,074 synaptic edges** that is **exactly isomorphic** across three independent *Drosophila* connectomes — female brain (FAFB v783), female brain + nerve cord (BANC v626), and male CNS (MCNS v0.9) — with **all 155 matched neurons sharing cell type** (155/155). It is the canonical **olfactory associative-memory pathway**, conserved across **sex** and **CNS region**.

**The circuit (Fig. 1).** The matched neurons form the complete early-olfactory-to-memory cascade: **olfactory/hygrosensory receptor neurons → antennal-lobe projection + local neurons → Kenyon cells → APL feedback.**

| Layer | Cell types (FAFB) | n | NT |
|---|---|---|---|
| Sensory | `ORN_*` (DA1, DM1/2, VA2, VC3, VM5…), `HRN_VP4` | ~38 | ACh |
| Antennal lobe | `lLN1_bc`, `lLN2F/T/X`, `ALIN1` | ~23 | GABA / 5-HT / Glu |
| Projection | `VP1m_l2PN`, `VP1d+VP4_l2PN1`, `VC3_adPN`, `DP1m_adPN` | 4 | ACh |
| Memory | `KCg-m` (γ-main Kenyon cells) | 89 | ACh |
| Feedback | `APL` (Anterior Paired Lateral) | 1 | GABA |

Neurotransmitters are internally coherent: a cholinergic excitatory spine (ORN→PN→KC) shaped by GABA/serotonergic lateral inhibition and a single GABAergic global-feedback neuron (APL). Figs. 2–3 show the neurons’ Codex 3D skeletons in brain space and the degeneracy frontier justifying N=155 as the meaningful answer.

**Observations.**
1. **Developmental canalization.** Recovering this circuit with *identical* wiring and cell types in two female and one male nervous system — reconstructed by different pipelines — argues it is hard-wired and invariant to sex and body region. The conserved core spans modalities: thermo/hygrosensory VP PNs alongside olfactory PNs converge on the mushroom body.
2. **APL feedback is the structural heart.** APL is the highest-degree node (in/out ≈ 93/93), reciprocally wired to the Kenyon-cell pool — the anatomical substrate of the negative feedback that enforces **sparse, decorrelated odor codes** required for selective learning (Lin et al. 2014; Amin et al. 2020).
3. **Topology ≠ homology.** A purely structural match gave 37 exactly-isomorphic neurons but **0/37** shared cell type. Requiring cell-type identity both guaranteed homology and *enlarged* the circuit (155 > 37) — real conserved wiring is more extensive and reproducible than coincidental wiring.

**Hypothesis.** The ORN→(PN/LN)→KC→APL motif is a **conserved computational primitive** — “sparsen sensory input, then gate it with global inhibition before associative storage” — under strong stabilizing constraint. Prediction: per-cell-type connection *probabilities* (PN→KC convergence, APL→KC coverage) match across datasets within reconstruction noise, while individual PN→KC partners stay idiosyncratic (random wiring; Caron et al. 2013) — the **motif** is conserved even though the **instance** is not.

**References.** 1. Dorkenwald et al. (2024) *Neuronal wiring diagram of an adult brain.* Nature 634:124. 2. Schlegel et al. (2024) *Whole-brain annotation… of Drosophila.* Nature 634:139. 3. Li et al. (2020) *Connectome of the adult Drosophila mushroom body.* eLife 9:e62576. 4. Lin et al. (2014) *Sparse, decorrelated odor coding…* Nat. Neurosci. 17:559. 5. Caron et al. (2013) *Random convergence of olfactory inputs…* Nature 497:113. 6. Amin et al. (2020) *Localized inhibition in the Drosophila mushroom body.* eLife 9:e56954. 7. Marin et al. (2020) *Thermo/hygrosensory neurons of the adult Drosophila brain.* Curr. Biol. 30:3167.
