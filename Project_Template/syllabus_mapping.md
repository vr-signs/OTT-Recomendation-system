# Curriculum Syllabus Mapping & Academic Alignment
**Curriculum**: JNTUK R23 Regulation — II B.Tech I Semester  
**Branch**: Artificial Intelligence & Data Science (AI & DS)  
**Team**: TEAM-18 | **Project Code**: 26 | **System**: StreamGlass OTT Engine

---

## Academic Syllabus Mapping Matrix

| Curriculum Subject | JNTUK R23 Unit / Module | Specific Syllabus Topics Covered | Implementation File in Codebase | Concrete Practical Application in Project |
| :--- | :--- | :--- | :--- | :--- |
| **Database Management Systems (DBMS)** | **Unit 1 & Unit 2** | • Entity-Relationship (ER) Modeling<br>• Relational Schema Representation<br>• Functional Dependencies & Candidate Keys<br>• 1NF, 2NF, 3NF Normalization<br>• Relational Integrity (PK/FK/CHECK)<br>• SQLite B-Tree Indexing | [`code/database.py`](file:///d:/Projects/OTT%20Project%203/Project_Template/code/database.py) | Designed 3NF schema for `users`, `movies`, and `watch_history` tables. Enforced foreign keys, check constraints on watch % and ratings, and created composite B-tree indexes for low-latency queries. |
| **Discrete Mathematics & Graph Theory (DMGT)** | **Unit 2** | • Binary Relations on Sets<br>• Properties of Relations (Reflexive, Symmetric, Transitive)<br>• Equivalence Relations & Proofs<br>• Equivalence Classes $[x]_R$<br>• Quotient Sets $S/R$<br>• Partitioning Theorem | [`code/discrete_math.py`](file:///d:/Projects/OTT%20Project%203/Project_Template/code/discrete_math.py) | Defined equivalence relation $x R y \iff \text{Genre}(x)=\text{Genre}(y) \land \text{Lang}(x)=\text{Lang}(y)$. Implemented algorithmic proofs of reflexivity, symmetry, and transitivity. Partitioned the catalog into quotient sets $S/R$ to eliminate regional starvation. |
| **Advanced Data Structures & Algorithms (ADSA)** | **Unit 2** | • Graph Representations (Adjacency List)<br>• Undirected Weighted Graphs $G=(V, E, W)$<br>• Breadth-First Search (BFS) Traversal<br>• FIFO Queue Frontier Management<br>• Graph Density & Connectedness<br>• Normalized Degree Centrality | [`code/graph_engine.py`](file:///d:/Projects/OTT%20Project%203/Project_Template/code/graph_engine.py) | Created a custom memory-efficient Adjacency List graph where edge weights reflect mutual co-viewership intensity. Implemented custom BFS traversal for radial neighborhood discovery and computed normalized degree centrality to discover cross-regional catalog bridge titles. |
| **Object-Oriented Programming (OOPJ)** | **Unit 1 & Unit 2** | • Encapsulation & Data Invariants<br>• Domain Entity Modeling<br>• Separation of Concerns<br>• Modular Class Hierarchies | [`code/recommender.py`](file:///d:/Projects/OTT%20Project%203/Project_Template/code/recommender.py) | Architected object-oriented classes (`ContentItem`, `Subscriber`, `InteractionMatrix`, `KNNRecommender`, `HybridScoringEngine`) ensuring data abstraction, maintainability, and clean decoupling of algorithmic logic from persistence layers. |
| **Python for AI & Collaborative Filtering** | **Applied Data Science** | • Sparse Utility Matrix Manipulation<br>• High-Dimensional Vector Math<br>• Item-Based Cosine Similarity Metric<br>• $k$-Nearest Neighbors ($k$-NN) Rating Prediction<br>• Hybrid Blended Scoring Model | [`code/recommender.py`](file:///d:/Projects/OTT%20Project%203/Project_Template/code/recommender.py) | Formulated item-based collaborative filtering using cosine distance across user rating vectors. Formulated the master hybrid scoring equation $\text{Score} = \alpha \cdot \text{kNN} + (1-\alpha) \cdot \text{Centrality}$ with cold-start fallback. |

---

## Detailed Unit-by-Unit Theoretical Deep-Dive

### 1. DBMS (Units 1 & 2)
The database eliminates data anomalies (insertion, deletion, update) through formal normalization:
- **Relational Representation**:
  $$\text{Users}(\underline{\text{user\_id}}, \text{name}, \text{age}, \text{primary\_language}, \text{secondary\_language}, \text{preferred\_genres})$$
  $$\text{Movies}(\underline{\text{movie\_id}}, \text{title}, \text{release\_year}, \text{language}, \text{primary\_genre}, \text{director}, \text{avg\_rating}, \text{popularity\_score})$$
  $$\text{WatchHistory}(\underline{\text{history\_id}}, \text{user\_id}^*, \text{movie\_id}^*, \text{watch\_percentage}, \text{rating}, \text{watched\_at})$$
- **Third Normal Form (3NF) Compliance**:
  - All non-prime attributes in `Users` depend strictly on the candidate key `user_id`.
  - All non-prime attributes in `Movies` depend strictly on `movie_id`.
  - In `WatchHistory`, `watch_percentage` and `rating` represent an instance of a subscriber interacting with a movie. Neither movie metadata nor user preferences are duplicated inside `WatchHistory`, eliminating transitive functional dependencies $X \rightarrow Y \rightarrow Z$.

### 2. DMGT (Unit 2)
- **Equivalence Relation Formalism**:
  Let $S$ be the universe of catalog media items. For any $x, y \in S$:
  $$(x, y) \in R \iff \text{Genre}(x) = \text{Genre}(y) \land \text{Language}(x) = \text{Language}(y)$$
- **Axiomatic Proofs**:
  1. **Reflexivity**: $\forall x \in S$, $\text{Genre}(x) = \text{Genre}(x)$ and $\text{Language}(x) = \text{Language}(x)$ by identity of equality. Hence $(x, x) \in R$.
  2. **Symmetry**: If $(x, y) \in R$, then $\text{Genre}(x) = \text{Genre}(y) \implies \text{Genre}(y) = \text{Genre}(x)$ and $\text{Language}(x) = \text{Language}(y) \implies \text{Language}(y) = \text{Language}(x)$, so $(y, x) \in R$.
  3. **Transitivity**: If $(x, y) \in R$ and $(y, z) \in R$, then by transitivity of equality over genres and languages, $\text{Genre}(x) = \text{Genre}(z)$ and $\text{Language}(x) = \text{Language}(z)$, proving $(x, z) \in R$.
- **Quotient Set Partitioning**:
  $$S/R = \{ [x]_R \mid x \in S \}$$
  Guarantees that the catalog is subdivided into non-empty, pairwise disjoint equivalence classes whose union covers the entire universe:
  $$\forall A, B \in S/R, A \neq B \implies A \cap B = \emptyset \quad \text{and} \quad \bigcup_{[x] \in S/R} [x] = S$$

### 3. ADSA (Unit 2)
- **Undirected Weighted Co-Watch Graph**:
  $$G = (V, E, W)$$
  $$W(u, v) = \sum_{s \in S_{uv}} \left[ \left(\frac{r_{s,u} + r_{s,v}}{10}\right) \times \left(\frac{\min(w_{s,u}, w_{s,v})}{100}\right) \right]$$
- **Breadth-First Search (BFS) Traversal**:
  Uses an explicit FIFO Queue data structure to expand the search frontier radially from a given seed movie $u$, exploring level-1 (direct co-viewed titles) and level-2 (latent multi-hop related titles) with time complexity $\mathcal{O}(|V| + |E|)$.
- **Normalized Degree Centrality**:
  $$C_D(v) = \frac{\sum_{u \in V, u \neq v} W(v, u)}{|V| - 1}$$
  Titles with high $C_D(v)$ function as bridge hubs, connecting disparate linguistic communities.

### 4. OOPJ & Python Collaborative Filtering
- **Item-Based Vector Cosine Similarity**:
  $$\text{Cosine}(i, j) = \frac{\vec{v}_i \cdot \vec{v}_j}{\|\vec{v}_i\|_2 \|\vec{v}_j\|_2}$$
- **Master Hybrid Scoring Formulation**:
  $$\text{Score}(u, i) = \left[ \alpha \cdot \frac{\widehat{r}_{u, i}}{5.0} + (1 - \alpha) \cdot \frac{C_D(i)}{\max_k C_D(k)} \right] \times \beta_{\text{lang}}(u, i) \times \gamma_{\text{genre}}(u, i)$$
  Balancing individual niche preferences with macro-network connectivity.
