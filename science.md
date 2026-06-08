# A Sex- and Region-Invariant Olfactory → Mushroom-Body Circuit

### Conserved (exactly isomorphic) across the FAFB, BANC and MCNS connectomes

**Summary.** From connectivity alone, validated against Codex cell-type annotations, we identified a directed induced subgraph of 155 neurons / 1,074 synaptic edges that is exactly isomorphic across three independent *Drosophila* connectomes — female brain (FAFB v783), female brain + nerve cord (BANC v626), and male CNS (MCNS v0.9) — with all 155 matched neurons sharing cell type (155/155). It is the canonical olfactory associative-memory pathway, conserved across sex and CNS region.

**The circuit (Fig. 1).** The matched neurons form the complete early-olfactory-to-memory cascade: **olfactory/hygrosensory receptor neurons → antennal-lobe projection + local neurons → Kenyon cells → APL feedback.**

|Layer|Cell types (FAFB)|n|NT|
|-|-|-|-|
|Sensory|`ORN\_\*` (DA1, DM1/2, VA2, VC3, VM5…), `HRN\_VP4`|\~38|ACh|
|Antennal lobe|`lLN1\_bc`, `lLN2F/T/X`, `ALIN1`|\~23|GABA / 5-HT / Glu|
|Projection|`VP1m\_l2PN`, `VP1d+VP4\_l2PN1`, `VC3\_adPN`, `DP1m\_adPN`|4|ACh|
|Memory|`KCg-m` (γ-main Kenyon cells)|89|ACh|
|Feedback|`APL` (Anterior Paired Lateral)|1|GABA|

Neurotransmitters are internally coherent. The circuit follows a cholinergic excitatory pathway, moving from ORNs to PNs to KCs, while being shaped by GABAergic and serotonergic lateral inhibition, along with a single GABAergic global-feedback neuron, APL. Figures 2 and 3 show the neurons’ Codex 3D skeletons in brain space and the degeneracy frontier, which supports N = 155 as the most meaningful result. Observations**.**

1. **Developmental canalization.** Finding this circuit with identical wiring and cell types in two female nervous systems and one male nervous system, each reconstructed through different pipelines, suggests that it is hard-wired and consistent across sex and body region. The conserved core also spans multiple sensory modalities. Thermo- and hygrosensory VP projection neurons, along with olfactory projection neurons, all converge on the mushroom body.
2. **APL feedback is the structural heart.** APL is the highest-degree node, with approximately 93 incoming and 93 outgoing connections. It is reciprocally connected to the Kenyon-cell pool, making it the anatomical basis for the negative feedback that creates sparse and decorrelated odor codes needed for selective learning (Lin et al. 2014; Amin et al. 2020).
3. **Topology does not equal homology.** A purely structural match identified 37 exactly isomorphic neurons, but 0 out of 37 shared the same cell type. Requiring cell-type identity both confirmed homology and expanded the circuit from 37 to 155 neurons. This shows that real conserved wiring is more extensive and reproducible than a coincidental structural match. Hypothesis. 



The ORN to PN/LN to KC to APL motif appears to be a conserved computational primitive. In simple terms, the circuit first sparsens sensory input, then regulates it through global inhibition before it is stored for associative memory. This suggests that the motif is under strong stabilizing constraint.



One prediction is that per-cell-type connection probabilities, such as PN-to-KC convergence and APL-to-KC coverage, should match across datasets within the expected limits of reconstruction noise. At the same time, the specific PN-to-KC partners may remain more idiosyncratic, reflecting random wiring as described by Caron et al. 2013. In other words, the overall motif is conserved, even if each individual instance of the wiring is not exactly the same.



**References.** 1. Dorkenwald et al. (2024) *Neuronal wiring diagram of an adult brain.* Nature 634:124. 2. Schlegel et al. (2024) *Whole-brain annotation… of Drosophila.* Nature 634:139. 3. Li et al. (2020) *Connectome of the adult Drosophila mushroom body.* eLife 9:e62576. 4. Lin et al. (2014) *Sparse, decorrelated odor coding…* Nat. Neurosci. 17:559. 5. Caron et al. (2013) *Random convergence of olfactory inputs…* Nature 497:113. 6. Amin et al. (2020) *Localized inhibition in the Drosophila mushroom body.* eLife 9:e56954. 7. Marin et al. (2020) *Thermo/hygrosensory neurons of the adult Drosophila brain.* Curr. Biol. 30:3167.

