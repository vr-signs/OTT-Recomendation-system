# StreamGlass · OTT Intelligence & Personalized Recommendation System

> **JNTUK R23 Curriculum · II B.Tech I Sem Academic Project · TEAM-18**

StreamGlass is a production-grade, full-stack OTT recommendation and subscriber analytics intelligence platform. It brings the subscriber, media catalog, relational transactional storage, and hybrid recommendation engine into a cohesive, high-performance web experience built with modern web technologies and deployed seamlessly to **Vercel**.

---

## 🌟 Architecture & Technology Stack

StreamGlass is engineered as a modern decoupled monorepo:

```
d:\Projects\OTT Project 3\
├── api/                        # Python Serverless API (FastAPI + Mangum)
│   ├── index.py                # 15 REST endpoints + OpenAPI documentation
│   ├── database.py             # 3NF SQLite database layer & connection factory
│   ├── recommender.py          # Hybrid KNN + Collaborative + Graph Recommender
│   ├── graph_engine.py         # NetworkX co-watch weighted topology engine
│   ├── discrete_math.py        # Axiom verification (Reflexivity, Symmetry, Transitivity)
│   ├── sample_data/            # Seed data JSONs & CSVs
│   └── requirements.txt        # Pinned Python dependencies
│
├── frontend/                   # Modern React + Vite SPA
│   ├── src/
│   │   ├── components/         # Reusable Liquid Glass UI components
│   │   │   ├── TopNav.jsx      # Semantic iOS/macOS floating glass navigation
│   │   │   ├── MetricCard.jsx  # Telemetry indicator surfaces
│   │   │   ├── TitleCard.jsx   # Media card with accent posters & match badges
│   │   │   ├── ProofCard.jsx   # Discrete math verified axiom cards
│   │   │   ├── PipelineStep.jsx# 4-stage academic intelligence pipeline
│   │   │   ├── DataTable.jsx   # Responsive relational data grid
│   │   │   ├── Formula.jsx     # Live mathematical KaTeX equation renderer
│   │   │   └── PlotWrapper.jsx # Responsive, theme-aware Plotly charts
│   │   ├── pages/              # 6 Complete Module Pages
│   │   │   ├── Overview.jsx    # Project dossier, motivation, pipeline
│   │   │   ├── Coursework.jsx  # DBMS, DMGT, ADSA, and OOPJ proofs & formulas
│   │   │   ├── Data.jsx        # Live SQLite storage telemetry & table explorer
│   │   │   ├── ModelLab.jsx    # Real-time α / k hyperparameter tuning & force graph
│   │   │   ├── Studio.jsx      # Side-by-side feed comparison & viewing simulator
│   │   │   └── Analytics.jsx   # Sunburst partitions, centrality, utility matrix
│   │   ├── styles/globals.css  # Apple Liquid Glass design tokens (Light/Dark/System)
│   │   ├── api.js              # Centralized type-safe API client
│   │   └── App.jsx             # Shell container, theme state, and router
│   ├── index.html              # Inter typography + KaTeX CDN
│   ├── vite.config.js          # Dev proxy routing /api -> FastAPI
│   └── package.json            # React 19, Plotly, KaTeX
│
├── vercel.json                 # Vercel monorepo deployment config
└── .env.example                # Configuration template
```

---

## 🚀 Running Locally

### 1. Backend (FastAPI)
In a terminal window:
```bash
cd api
pip install -r requirements.txt
uvicorn index:app --host 127.0.0.1 --port 8000 --reload
```
The interactive Swagger API documentation will be accessible at: `http://127.0.0.1:8000/docs`

### 2. Frontend (React + Vite)
In a second terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser. All `/api/*` network requests are automatically proxied to the FastAPI server running on port 8000.

---

## ☁️ Deploying to Vercel

StreamGlass is pre-configured for **zero-configuration single-project deployment** on Vercel:

1. Push this repository to GitHub or GitLab.
2. In the [Vercel Dashboard](https://vercel.com), click **Add New** → **Project**.
3. Import your repository.
4. Leave all build settings at default (`vercel.json` automatically orchestrates frontend build and serverless Python functions).
5. Click **Deploy**.

Vercel will:
- Build the React SPA into static assets hosted on Vercel Edge Network.
- Host `api/index.py` as an elastic Python Serverless Function responding to `/api/*`.

---

## 📚 Academic Modules Covered

1. **DBMS (Database Management Systems)**:
   - 3NF relational normalization across `users`, `movies`, and `watch_history`.
   - Functional dependency validation ($F_1, F_2, F_3$).
   - Live query explorer and storage footprint monitoring.

2. **DMGT (Discrete Mathematics & Graph Theory)**:
   - Equivalence relation verification: $R = \{(x,y) \mid \text{Genre}(x)=\text{Genre}(y) \land \text{Language}(x)=\text{Language}(y)\}$.
   - Live mathematical proofs for **Reflexivity**, **Symmetry**, and **Transitivity**.
   - Partition Theorem proof and quotient set validation.

3. **ADSA (Advanced Data Structures & Algorithms)**:
   - Weighted co-watch adjacency graph built from interaction records.
   - Breadth-First Search (BFS) graph traversal ($O(|V| + |E|)$).
   - Degree centrality calculation identifying bridge titles connecting regional content clusters.

4. **OOPJ & Machine Learning**:
   - Cosine vector similarity over normalized movie interaction embeddings.
   - Hybrid ranking engine:
     $$\text{Score}(u,i) = \left[\alpha \cdot \frac{\widehat{r}_{u,i}}{5.0} + (1-\alpha) \cdot \frac{C_D(i)}{\max_k C_D(k)}\right] \times \beta_{\text{lang}}(u,i) \times \gamma_{\text{genre}}(u,i)$$
   - Real-time interaction recording with dynamic catalog reranking.

---

## 👥 Project Team (JNTUK R23 · TEAM-18)
- **Kovvuri Venkata Reddy** (`25B21A4502`)
- **Pantadi H. Durga Prasad** (`25B21A4503`)
- **Battula Sravan Kumar** (`25B21A4501`)
- **Bodireddy Kanaka Mani** (`25B21A4504`)
- **Kapa Kumar** (`25B21A4506`)
