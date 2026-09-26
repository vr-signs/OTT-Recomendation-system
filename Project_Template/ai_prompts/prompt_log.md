# AI & LLM Interaction Prompt Log & Engineering Lifecycle
**Project Title**: OTT Subscriber & Personalized Recommendation System (StreamGlass)  
**Curriculum**: JNTUK R23 Regulation — II B.Tech I Semester (AI & DS)  
**Team**: TEAM-18 | **Project Code**: 26

---

## 1. Prompt Design Philosophy & Objectives

In accordance with the **JNTUK R23 Evaluation Rubric (20% Weightage for AI/LLM Usage)**, Team-18 utilized an iterative, multi-stage prompt engineering workflow to design, mathematically verify, and implement the StreamGlass platform.

The prompt strategy followed four rigorous phases:
1. **Curriculum Grounding & Constraint Formulation**: Ensuring all outputs strictly complied with JNTUK R23 course outcomes across DBMS, DMGT, ADSA, and OOPJ.
2. **Mathematical Proof Generation & Boundary Testing**: Formulating symbolic logic and programmatic proofs for equivalence relations and quotient sets.
3. **Architectural Synthesis & Clean Code Generation**: Creating fully typed, modular Python classes without placeholders or pseudo-code.
4. **Refinement, Error Mitigation & Academic Defense**: Stress-testing edge cases such as cold-start sparsity, zero-norm cosine denominators, and Windows character encoding compatibility.

---

## 2. Iterative Prompt Engineering History

### Phase 1: Problem Decomposition & Curriculum Mapping Prompt
- **System Prompt**:
  > *"You are an elite Principal AI Engineer and University Computer Science Professor specializing in the JNTUK R23 curriculum. Your goal is to map the problem statement 'A regional streaming app shows the same most-popular list to everyone, with no personalization' to 4 specific B.Tech subjects: DBMS (U1 & U2), DMGT (U2), ADSA (U2), and OOPJ/Python."*
- **User Prompt**:
  > *"How can we mathematically formulate the regional streaming problem such that DMGT equivalence classes solve catalog starvation, ADSA co-watch graphs uncover hidden community bridges, and DBMS 3NF schemas maintain transaction integrity? Provide the formal relation definitions."*
- **Model Output & Architectural Insight**:
  The LLM proposed defining the equivalence relation $R$ over $\text{Genre} \times \text{Language}$ on the set of catalog titles $S$. This allowed deriving disjoint quotient sets $S/R$, proving mathematically that a static Top-10 list samples from at most 2 or 3 equivalence classes, completely starving the remaining partitions.

---

### Phase 2: DMGT Equivalence Relation & Formal Proof Prompt
- **System Prompt**:
  > *"You are a Discrete Mathematics Professor. Enforce formal mathematical rigor with step-by-step proofs for reflexivity, symmetry, and transitivity."*
- **User Prompt**:
  > *"Write a Python script that takes a list of movie records and formally verifies whether the relation (x R y <=> Genre(x) == Genre(y) and Language(x) == Language(y)) satisfies all equivalence relation axioms. Also verify the Fundamental Theorem of Equivalence Relations (pairwise disjointness and exhaustive union)."*
- **Refinement Cycle**:
  - *Initial Bug Encountered*: The initial model draft tested reflexivity and symmetry, but omitted testing the non-emptiness condition and pairwise disjointness $\forall A \neq B, A \cap B = \emptyset$.
  - *Correction Prompt*: *"Refine `verify_partition_theorem` to explicitly perform set intersection across all $\binom{n}{2}$ pairs of equivalence classes to programmatically guarantee zero overlap."*
  - *Outcome*: Added complete intersection testing across all pairs, confirming $0$ overlapping titles across $16$ quotient partitions.

---

### Phase 3: ADSA Co-Watch Graph & Adjacency List Prompt
- **System Prompt**:
  > *"Act as an Advanced Data Structures and Algorithms instructor. Do not use generic high-level libraries for core traversals; implement graph representations using custom adjacency lists."*
- **User Prompt**:
  > *"Implement a custom class `CoWatchGraph` using `dict[str, dict[str, float]]`. Edges must represent mutual viewer affinity weighted by watch percentages and ratings. Provide an explicit BFS traversal using a FIFO queue (`collections.deque`) and a method to compute normalized degree centrality."*
- **Validation**:
  The output correctly implemented BFS with level tracking ($\mathcal{O}(|V| + |E|)$ complexity) and degree centrality $C_D(v) = \frac{\sum W(v, u)}{|V| - 1}$.

---

### Phase 4: OOPJ & Hybrid Recommender Prompt
- **System Prompt**:
  > *"You are an enterprise software architect specializing in Clean Architecture and Object-Oriented design principles."*
- **User Prompt**:
  > *"Design an item-based collaborative filtering recommender with clean domain entities: `ContentItem`, `Subscriber`, `InteractionMatrix`, and `KNNRecommender`. Combine k-NN predicted ratings with Graph Degree Centrality via an alpha-weighted hybrid equation: $\text{Score} = \alpha \cdot \text{kNN} + (1-\alpha) \cdot \text{Centrality}$. How do you handle cold-start users with zero prior watch history?"*
- **Refinement Cycle**:
  - *Edge Case Identified*: If a new subscriber (e.g., U110 Meera Nair) registers with zero watch history, standard k-NN collaborative filtering outputs an empty dictionary because the set of watched neighbors is empty.
  - *Solution Formulated*: Implemented an automatic cold-start fallback to DMGT quotient partitions, selecting the top-rated title from each language-genre equivalence class boosted by the user's stated language preference.

---

### Phase 5: UI/UX Styling & Liquid Glass Navigation Prompt
- **User Prompt**:
  > *"Design a modern Apple iOS/macOS inspired Liquid Frosted Glass Floating Dock in Streamlit using custom injected CSS. Use `backdrop-filter: blur(35px) saturate(210%)`, floating pill indicators, SF Pro typography, and dark nebula colors (`#07090E`). Integrate all 6 curriculum modules into an interactive single-page app."*
- **Model Output**:
  Produced `LIQUID_GLASS_CSS` with custom styling for sticky dock containers, glass cards, neon match confidence badges, and smooth hover micro-animations.

---

## 3. Critical Reflections & Learnings

1. **Prompt Precision Matters**: Generic prompts like *"build a recommendation app"* yield naive toy projects with fake data and non-standard architecture. Enforcing curriculum bounds (JNTUK R23 Unit 1 & Unit 2) compelled the LLM to write mathematically rigorous, academically grounded code.
2. **Verification over Blind Acceptance**: Running terminal tests on generated code immediately revealed environment-specific constraints (e.g., Windows console character encoding `cp1252` failing on mathematical symbols `\u2200`). This was resolved by reconfiguring `sys.stdout` to UTF-8.
3. **Hybrid AI as a Teaching Catalyst**: Collaborating with LLMs enabled Team-18 to grasp the deep mathematical connections between abstract theoretical concepts (quotient sets in DMGT, BFS spanning trees in ADSA, 3NF in DBMS) and real-world industrial software engineering.
