# Part I — Introduction {-}

This part frames the multi-stream policy-inference problem and
surveys the prior work on which the framework builds.  Two chapters:

The Free Energy Principle enters this manuscript as a disciplined
variational framing rather than as a slogan: adaptive systems can be
modeled as maintaining tractable beliefs that bound sensory surprise,
while active inference turns that variational bound into a process
theory of perception, action, learning, and policy selection
[@friston-2006; @friston-2010; @buckley-2017; @parr-2022;
@pezzulo-2024-sentient].  That framing has also drawn careful scope
critiques, especially around Markov blankets and the temptation to
treat FEP as a theory of everything rather than as a modeling
principle with explicit assumptions [@aguilera-2021; @raja-2021;
@menary-gillett-2022].  The finite POMDP setting used here is
therefore intentionally narrow: expected free energy supplies the
policy objective, `pymdp` supplies a reproducible implementation
substrate, and the contribution of this manuscript is to ask what
happens when the *policy posterior itself* is allowed to carry explicit
cross-stream dependence [@friston-2017; @parr-friston-2017-uncertainty;
@kaplan-friston-2018; @dacosta-2020; @smith-2022; @heins-2022].

* **[[SECREF:motivation]]** — *why* parametric coupling is needed.
  Real agents juggle many concurrent policy streams; strict mean-field
  factorization can discard cross-stream structure that is directly
  visible in the motivating examples of [[SECREF:motivation]].
  A single tunable coupling parameter recovers strict factorization at
  one limit and arbitrary joint structure at the other.
* **[[SECREF:background]]** — *what already exists* in active
  inference, control theory, information geometry, and tensor
  networks that this framework relates to exactly, parametrically, or
  analogically.  Eight axes of antecedents are surveyed (discrete-time POMDP
  AIF; mean-field variational families; hierarchical / deep /
  sophisticated AIF; information geometry; tensor networks; KL /
  path-integral control and RL; multi-agent inference and
  renormalization; formal verification and reproducible scientific
  software).  The later recovery ledger separates exact recoveries
  (for example mean-field AIF and single-stream KL control) from
  parametric embeddings (for example explicit factor-graph policy
  factors, options, copula VI, and multi-agent coupling) and
  structural analogies (for example hierarchical, sophisticated,
  branching-time, renormalization-group, and Markov-blanket readings).
  The specific mappings are cataloged in [[SECREF:connections]]
  through [[SECREF:connections_multi_agent_geometry]].

After Part I a reader has the motivating examples, the literature
context, and the conceptual frame within which the analytical
content of [[SECREF:setup]] onward is developed.  Every symbol used in
this manuscript is cataloged in [[SECREF:notation]] across all four
tracks (manuscript, LaTeX preamble, Python, Lean), with status notes
flagging where a track diverges (e.g. unicode-vs-ASCII identifier
conventions). The Lean track ships in two complementary packages:
`MathlibProofs/`, which machine-checks the central
S01 free-energy identity ([[THMREF:thm_4_1]]) in $\mathbb{R}$ with
foundational-only `#print axioms` (`propext`, `Classical.choice`,
`Quot.sound`; two independent negative controls audited on every
build), and `lean/ActinfPolicyEntanglement/`, a stock-Lean
[[VAR:lean_toolchain_version]] boundary fragment that ships the
[[VAR:theorem_registry_count]]-row theorem surface as a typed API
for the Python computational layer and the manuscript registry;
[[SECREF:lean_plan]] carries the per-row content table and
`docs/reference/veridical_status.md` the running audit.

**Repository artifact.** All four tracks (prose, equations, Python /
pymdp, Lean 4) are maintained as a single working repository artifact
[@friedman-2026-actinf-policy-entanglement]. The public Zenodo DOI
(`10.5281/zenodo.20419431`) and source repository are recorded in
[`manuscript/config.yaml`](config.yaml) and [`CITATION.cff`](../CITATION.cff).
The entire build — rendered PDF, pymdp
1.0.1 numerical sidecars, dashboard invariants, and the `MathlibProofs`
$\mathbb{R}$-level discharge — regenerates from a single command
(`./run.sh --pipeline` or `python scripts/run_all.py`), and the
repository's machine-readable `CITATION.cff` provides the preferred
citation form.

---
