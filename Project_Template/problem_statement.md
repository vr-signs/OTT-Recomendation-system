# Academic Problem Statement & Architectural Dossier
**JNTUK R23 Regulation — II B.Tech I Semester (Artificial Intelligence & Data Science)**  
**Team**: TEAM-18 | **Project Code**: 26  
**Project Title**: OTT Subscriber & Personalized Recommendation System (StreamGlass)

---

## 1. Project Team Dossier

| S.No | Student ID Number | Student Name | Role & Core Contribution |
| :--- | :--- | :--- | :--- |
| 1 | **25B21A4502** | **KOVVURI VENKATA REDDY** | Lead System Architect & Collaborative Filtering Engine (OOPJ/Python) |
| 2 | **25B21A4503** | **PANTADI HEMANTH DURGA PRASAD** | DMGT Formal Proofs & Equivalence Partitioning Specialist |
| 3 | **25B21A4501** | **BATTULA SRAVAN KUMAR** | ADSA Graph Algorithms & Co-Watch Topology Engineer |
| 4 | **25B21A4504** | **BODIREDDY KANAKA MANI SINDHURA DEVI** | DBMS Relational Schema, 3NF Normalization & SQLite Lead |
| 5 | **25B21A4506** | **KAPA KUMAR** | UI/UX Liquid Glass Dock & Full-Stack Frontend Integration |

---

## 2. Problem Statement Definition

> *"A regional streaming app shows the same most-popular list to everyone, with no personalization."*

### 2.1 The Regional Streaming Crisis
Regional Over-The-Top (OTT) platforms serving the Indian subcontinent cater to linguistically diverse demographics speaking Telugu, Tamil, Hindi, Malayalam, Kannada, and English. Unlike monolingual Western streaming services, subscriber consumption behavior in regional markets is heavily shaped by:
1. **Linguistic Affinity**: Strong preference for native tongue content with selective cross-linguistic migration.
2. **Genre Granularity**: Significant taste divergences ranging from commercial mass-action masala films to realistic indie dramas and neo-noir thrillers.
3. **Multi-generational Co-viewing**: Co-existence of family subscribers and individual digital-native youth on the same subscription account.

### 2.2 Core Failures of Static Popularity Systems
When a regional streaming platform implements a naive "Top 10 Most Popular" or "Trending Now" ranking metric based strictly on total view counts:
- **Homogeneity Bias & Winner-Take-All Dynamics**: Heavyweight commercial blockbusters (e.g., mega-budget action epics) capture high raw view counts simply due to extensive theatrical marketing, dominating the landing feed 24/7.
- **Regional Language Alienation**: A native Telugu subscriber who exclusively watches localized mystery thrillers and family dramas is repeatedly recommended Hindi blockbusters or English sci-fi releases with which they share zero affinity.
- **Niche & Localized Starvation**: High-caliber regional cinema (e.g., Tamil socio-political dramas, Telugu situational comedies) never breaches the global view count threshold required to appear on the homepage, remaining buried deep in the catalog.
- **Viewer Fatigue & Churn**: Inability of subscribers to discover content that matches their specific taste profile leads to decision paralysis, app abandonment, and subscription churn within the first 30 days of registration.

---

## 3. Engineering & Mathematical Objectives

To resolve this challenge, Team-18 built **StreamGlass**, a production-grade academic system integrating all core curriculum subjects prescribed under **JNTUK R23 Regulation (II B.Tech I Sem - AI & DS)**:

```
+-----------------------------------------------------------------------------------+
|                            STREAMGLASS ARCHITECTURE                               |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ DBMS (U1 & U2) ]         --> 3NF Relational Data Warehouse (SQLite)            |
|                                 (Users, Movies, Granular Watch Percentages)       |
|                                         |                                         |
|  [ DMGT (Unit 2) ]          --> Equivalence Relation: x R y <=> Lang & Genre Match|
|                                 Quotient Partitions S/R for Anti-Starvation       |
|                                         |                                         |
|  [ ADSA (Unit 2) ]          --> Undirected Weighted Co-Watch Graph G = (V,E,W)    |
|                                 BFS Horizon Discovery & Degree Centrality         |
|                                         |                                         |
|  [ OOPJ & Python ML ]       --> Item-Based Cosine Collaborative Filtering (k-NN)  |
|                                 Hybrid Formula: Score = a*kNN + (1-a)*Centrality  |
|                                         |                                         |
|  [ UI/UX Delivery ]         --> Streamlit Liquid Glass Dock with Live Watch&Rate  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

1. **Relational Data Integrity (DBMS)**: Replace ad-hoc flat files with an ACID-compliant, 3NF normalized SQLite schema with strict foreign keys and index optimization.
2. **Axiomatic Fairness Partitioning (DMGT)**: Formally prove that equating items across $(Genre \times Language)$ forms an Equivalence Relation. Partition the catalog into disjoint quotient classes $S/R$ to guarantee cold-start coverage.
3. **Topological Co-Viewership Modeling (ADSA)**: Structure viewer overlap as a custom adjacency-list graph $G = (V, E, W)$. Employ Breadth-First Search (BFS) for localized multi-hop discovery and compute Degree Centrality to identify cross-linguistic bridge titles.
4. **Personalized Hybrid Inference (OOPJ / Python)**: Formulate clean object-oriented classes (`ContentItem`, `Subscriber`, `InteractionMatrix`, `KNNRecommender`) that compute high-dimensional Cosine Similarity over sparse utility vectors, blending personal affinity with catalog centrality.
5. **Empirical Side-by-Side Validation**: Provide a live, side-by-side interactive laboratory contrasting the static popularity baseline with the dynamic personalized AI feed in real time.
