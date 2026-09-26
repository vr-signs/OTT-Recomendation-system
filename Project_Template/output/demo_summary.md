# StreamGlass Interface Walkthrough & Demonstration Summary
**Project Title**: OTT Subscriber & Personalized Recommendation System  
**Curriculum**: JNTUK R23 Regulation — II B.Tech I Semester (AI & DS)  
**Team**: TEAM-18 | **Project Code**: 26  
**System Name**: StreamGlass OTT Engine

---

## 1. Executive Summary & Interface Philosophy

**StreamGlass** is an enterprise-caliber academic application designed to solve regional OTT catalog homogenization. Built in Python and Streamlit, the application eliminates standard generic UI widgets in favor of an **Apple iOS/macOS inspired Liquid Frosted Glass Floating Dock** featuring:
- High-refraction backdrop blur (`backdrop-filter: blur(35px) saturate(210%)`).
- Floating frosted glass pills with hairline borders (`1px solid rgba(255, 255, 255, 0.45)`) and ambient glow shadows.
- A dark nebula palette (`#07090E`) with high-contrast neon accents (Cyan `#00F0FF`, Indigo `#6366F1`, Emerald `#10B981`).
- Six dedicated curriculum modules representing the academic syllabus of **DBMS**, **DMGT**, **ADSA**, and **OOPJ / Python ML**.

---

## 2. Interactive Navigation Modules Breakdown

```
+---------------------------------------------------------------------------------------------------------+
|                                    LIQUID FROSTED GLASS FLOATING DOCK                                   |
|   [⎋ Command Center] [∫ Theoretical Core] [⌗ Engineering Stack] [∿ Model Lab] [▷ Live Studio] [⌖ BI Dash] |
+---------------------------------------------------------------------------------------------------------+
```

### Module 1: ⎋ Command Center
- **Translucent Hero Glass Banner**: Displays official project identification, JNTUK R23 curriculum accreditation, project code (26), and team credentials.
- **Problem Statement Callout**: Interactively contrasts the failure modes of static popularity feeds against personalized multi-regional feeds.
- **Team-18 Dossier**: Presents student IDs, full legal names, and individual engineering ownership areas.
- **4-Stage Pipeline Architecture**: Visual floating cards summarizing the complete workflow:
  1. Relational Ingestion (DBMS)
  2. Quotient Partitioning (DMGT)
  3. Co-Watch Topology (ADSA)
  4. Hybrid AI Engine (OOPJ & ML)

### Module 2: ∫ Theoretical Core & Math
Contains dedicated tabs with rendered LaTeX formulas, formal proofs, and interactive proof verifications:
1. **DBMS (U1 & U2)**: Relational schemas, candidate keys, Functional Dependency sets ($F_1, F_2, F_3$), and formal proofs of 3NF compliance.
2. **DMGT (U2)**: Live execution proving that the relation:
   $$(x, y) \in R \iff \text{Genre}(x) = \text{Genre}(y) \land \text{Language}(x) = \text{Language}(y)$$
   satisfies Reflexivity ($\forall x \in S, x R x$), Symmetry ($x R y \implies y R x$), and Transitivity ($(x R y \land y R z) \implies x R z$). Displays the quotient set $S/R$ forming 16 pairwise disjoint equivalence classes covering 100% of the catalog.
3. **ADSA (U2)**: Adjacency list representation, undirected weighted graph $G = (V, E, W)$, BFS time complexity $\mathcal{O}(|V| + |E|)$, and degree centrality formula.
4. **OOPJ & Python**: Cosine similarity formula over high-dimensional user vectors and the master hybrid scoring equation.

### Module 3: ⌗ Engineering & Data Stack
- **Live Database Telemetry**: Displays real-time metrics for users, movies, watch transactions, and SQLite database storage size.
- **Interactive Table Explorer**: Allows examiners to inspect raw tables (`users`, `movies`, `watch_history`) directly from SQLite.
- **Runtime Environment Diagnostics**: Confirms installed versions of Python (3.14.6), Streamlit (1.64.0), SQLite (3.50.4), Scikit-learn (1.9.1), and NetworkX (3.6.1).

### Module 4: ∿ Neural & Graph Engine (Model Lab)
- **Hyperparameter Control Island**:
  - Slider for $k$-Nearest Neighbors ($k \in [2, 8]$).
  - Slider for Hybrid Weight $\alpha \in [0.0, 1.0]$, balancing Collaborative Filtering vs. Graph Degree Centrality.
- **Step-by-Step Vector Math Visualizer**: Allows selecting any two movies (e.g., *Kalki 2898 AD* vs. *RRR*) to view their raw user rating vectors, dot product, L2 vector norms, and exact calculated Cosine Similarity ($0.6634$).
- **Interactive 2D Co-Watch Network**: Plotly force-directed network diagram with node size scaled by Degree Centrality and edge opacity by mutual viewer weight.

### Module 5: ▷ StreamGlass Live Studio
- **Active Subscriber Persona Switcher**: Switch dynamically between 10 regional personas:
  - *Ravi Kumar (U101)*: Telugu Action/Thriller enthusiast.
  - *Priya Sundaram (U102)*: Tamil Drama/Romance admirer.
  - *Meera Nair (U110)*: Cold-start subscriber with zero watch history.
- **Side-by-Side Live Viewport**:
  - **Left Column: Default Platform Feed**: Static Top-10 popular titles, showing how a Telugu viewer is bombarded with mismatched content.
  - **Right Column: StreamGlass AI Feed**: Dynamic personalized feed featuring Liquid Glass cards, % match confidence badges (e.g., `⚡ 99% Match Confidence`), language/genre tags, and transparent "Why Recommended" chips.
- **Live "Watch & Rate" Drawer**: Select any unwatched title, set completion percentage and a star rating (1.0 to 5.0), click *Record Interaction*, and immediately witness the ACID SQLite insertion and live re-ranking of the recommendation feed.

### Module 6: ⌖ Intelligence Dashboards
- **Equivalence Class Sunburst Chart**: Hierarchical visualization of movies partitioned by Language $\rightarrow$ Primary Genre $\rightarrow$ Title.
- **Co-Watch Degree Centrality Chart**: Horizontal bar chart identifying bridge titles (*Hi Nanna* $C_D = 0.8418$, *Jailer* $C_D = 0.6974$).
- **User-Item Sparsity Heatmap**: 2D color intensity matrix illustrating observed vs. unobserved ratings across the subscriber base (Sparsity: $72.78\%$).

---

## 3. How to Launch & Present Locally

### Prerequisites
Ensure Python is installed on your machine.

### Terminal Commands
```powershell
# 1. Navigate to the project root directory
cd "d:/Projects/OTT Project 3"

# 2. Activate the virtual environment
.venv\Scripts\activate

# 3. Launch the Streamlit application
streamlit run Project_Template/code/app.py
```

The application will launch at:  
`Local URL: http://localhost:8501`  
`Network URL: http://192.168.x.x:8501`
