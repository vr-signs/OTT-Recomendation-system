"""
StreamGlass — FastAPI Backend
Exposes all recommendation, database, analytics, and graph engine logic as REST endpoints.
Frontend (React + Vite) consumes these routes.
"""

import os
import sys
import json
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── make local modules importable when running from api/ ──────────────────────
sys.path.insert(0, os.path.dirname(__file__))

import database
import recommender as rec_module
import graph_engine
import discrete_math

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="StreamGlass API", version="1.0.0")

# CORS — allow the Vite dev server and Vercel-hosted frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev
        "http://localhost:3000",
        "https://*.vercel.app",
        os.environ.get("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Module-level engine singleton (cached per function instance) ──────────────
_engine: Optional[rec_module.HybridScoringEngine] = None

def get_engine() -> rec_module.HybridScoringEngine:
    global _engine
    if _engine is None:
        _engine = rec_module.HybridScoringEngine(k_neighbors=5, alpha=0.60)
    return _engine


# ═══════════════════════════════════════════════════════════════════════════════
# 1  HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "StreamGlass API v1.0"}


# ═══════════════════════════════════════════════════════════════════════════════
# 2-5  DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/db/metrics")
def db_metrics():
    m = database.get_db_metrics()
    return {
        "user_count": m["user_count"],
        "movie_count": m["movie_count"],
        "interaction_count": m["interaction_count"],
        "database_size_kb": m["database_size_kb"],
        "sqlite_version": m["sqlite_version"],
        "python_version": sys.version.split()[0],
    }


@app.get("/api/db/users")
def db_users():
    df = database.get_all_users()
    # preferred_genres stored as JSON string — parse for readability
    records = df.to_dict(orient="records")
    for r in records:
        if isinstance(r.get("preferred_genres"), str):
            try:
                r["preferred_genres"] = json.loads(r["preferred_genres"])
            except Exception:
                pass
    return {"columns": list(df.columns), "rows": records}


@app.get("/api/db/movies")
def db_movies():
    df = database.get_all_movies()
    records = df.to_dict(orient="records")
    for r in records:
        if isinstance(r.get("cast_members"), str):
            try:
                r["cast_members"] = json.loads(r["cast_members"])
            except Exception:
                pass
    return {"columns": list(df.columns), "rows": records}


@app.get("/api/db/watch_history")
def db_watch_history():
    conn = database.get_connection()
    df = pd.read_sql_query(
        "SELECT history_id, user_id, movie_id, watch_percentage, rating, watched_at "
        "FROM watch_history ORDER BY watched_at DESC;",
        conn,
    )
    conn.close()
    return {"columns": list(df.columns), "rows": df.to_dict(orient="records")}


# ═══════════════════════════════════════════════════════════════════════════════
# 6-7  COURSEWORK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/coursework/dmgt")
def coursework_dmgt():
    movies_df = database.get_all_movies()
    records = movies_df.to_dict(orient="records")

    ref = discrete_math.verify_reflexivity(records)
    sym = discrete_math.verify_symmetry(records)
    trn = discrete_math.verify_transitivity(records)
    quotient = discrete_math.compute_equivalence_classes(records)
    partition = discrete_math.verify_partition_theorem(records, quotient)

    # Build a JSON-safe quotient summary (just sizes, not full item lists)
    quotient_summary = {k: len(v) for k, v in quotient.items()}

    return {
        "reflexivity": ref,
        "symmetry": sym,
        "transitivity": trn,
        "partition": partition,
        "quotient_summary": quotient_summary,
    }


@app.get("/api/coursework/adsa")
def coursework_adsa():
    graph = graph_engine.build_cowatch_graph_from_db()
    metrics = graph.get_graph_metrics()
    return {
        "num_nodes": metrics["num_nodes"],
        "num_edges": metrics["num_edges"],
        "density": round(metrics["density"], 6),
        "top_hub_movie": metrics["top_hub_movie"],
        "top_hub_centrality": round(metrics["top_hub_centrality"], 6),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 8-10  RECOMMENDATIONS + INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/recommendations/popular")
def popular_feed(limit: int = Query(6, ge=1, le=20)):
    engine = get_engine()
    return {"feed": engine.get_static_popular_feed(limit=limit)}


@app.get("/api/recommendations/personalized/{user_id}")
def personalized_feed(
    user_id: str,
    k: int = Query(5, ge=2, le=8),
    alpha: float = Query(0.60, ge=0.0, le=1.0),
    limit: int = Query(6, ge=1, le=20),
):
    engine = get_engine()
    engine.set_hyperparameters(k, alpha)

    users_df = database.get_all_users()
    row = users_df[users_df["user_id"] == user_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    user_dict = row.iloc[0].to_dict()
    subscriber = rec_module.Subscriber.from_dict(user_dict)
    history = database.get_user_watch_history(user_id)
    subscriber.load_history(history.to_dict(orient="records"))

    recs = engine.get_personalized_recommendations(subscriber, limit=limit)
    return {"user_id": user_id, "recommendations": recs}


@app.get("/api/users/{user_id}/profile")
def user_profile(user_id: str):
    """Full subscriber profile including watch history."""
    users_df = database.get_all_users()
    row = users_df[users_df["user_id"] == user_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    user_dict = row.iloc[0].to_dict()
    if isinstance(user_dict.get("preferred_genres"), str):
        try:
            user_dict["preferred_genres"] = json.loads(user_dict["preferred_genres"])
        except Exception:
            pass

    history = database.get_user_watch_history(user_id)
    watched_ids = history["movie_id"].tolist() if not history.empty else []

    # Unwatched movies for the interaction form
    all_movies = database.get_all_movies()
    unwatched = [
        {"movie_id": r["movie_id"], "label": f'{r["title"]} · {r["language"]} · {r["primary_genre"]}'}
        for _, r in all_movies.iterrows()
        if r["movie_id"] not in watched_ids
    ]

    return {
        "profile": user_dict,
        "history_count": len(history),
        "history": history.to_dict(orient="records"),
        "unwatched": unwatched,
    }


class InteractionRequest(BaseModel):
    user_id: str
    movie_id: str
    watch_percentage: float
    rating: float


@app.post("/api/interactions")
def record_interaction(body: InteractionRequest):
    if not (0 <= body.watch_percentage <= 100):
        raise HTTPException(status_code=422, detail="watch_percentage must be 0-100")
    if not (1.0 <= body.rating <= 5.0):
        raise HTTPException(status_code=422, detail="rating must be 1.0-5.0")

    history_id = database.record_user_interaction(
        body.user_id, body.movie_id, body.watch_percentage, body.rating
    )

    # Refresh engine so next recommendation call reflects the new interaction
    get_engine().refresh()

    return {"history_id": history_id, "status": "committed"}


# ═══════════════════════════════════════════════════════════════════════════════
# 11-12  MODEL LAB
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/model/similarity")
def model_similarity(
    movie_a: str = Query(...),
    movie_b: str = Query(...),
):
    engine = get_engine()
    result = engine.knn.get_stepwise_vector_math(movie_a, movie_b)
    return result


@app.get("/api/model/network")
def model_network():
    """Returns the co-watch force graph as a Plotly JSON figure."""
    graph = graph_engine.build_cowatch_graph_from_db()
    fig = graph.generate_plotly_network()
    fig.update_traces(
        selector=dict(mode="lines"),
        line=dict(color="rgba(60,60,67,.24)"),
    )
    fig.update_traces(
        selector=dict(mode="markers+text"),
        textfont=dict(color="#424245"),
        marker=dict(line=dict(color="#ffffff", width=1.3)),
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=11),
        margin=dict(l=0, r=0, t=0, b=0),
        height=510,
    )
    return json.loads(fig.to_json())


# ═══════════════════════════════════════════════════════════════════════════════
# 13-15  ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/analytics/partitions")
def analytics_partitions():
    movies_df = database.get_all_movies()
    sunburst = px.sunburst(
        movies_df,
        path=["language", "primary_genre", "title"],
        values="popularity_score",
        color="language",
        color_discrete_map={
            "Telugu": "#5b8ec7",
            "Tamil": "#58a496",
            "Hindi": "#d29652",
            "English": "#8a7bc4",
        },
    )
    sunburst.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=11),
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
    )
    return json.loads(sunburst.to_json())


@app.get("/api/analytics/centrality")
def analytics_centrality():
    movies_df = database.get_all_movies()
    graph = graph_engine.build_cowatch_graph_from_db()
    centralities = graph.calculate_degree_centrality()
    movie_names = {row["movie_id"]: row["title"] for _, row in movies_df.iterrows()}

    centrality_df = pd.DataFrame(
        [
            {"Title": movie_names.get(mid, mid), "Centrality": score}
            for mid, score in centralities.items()
        ]
    ).sort_values("Centrality", ascending=True)

    bar = px.bar(
        centrality_df,
        x="Centrality",
        y="Title",
        orientation="h",
        color_discrete_sequence=["#0071e3"],
    )
    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=11),
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        yaxis=dict(tickfont=dict(size=10)),
    )
    return json.loads(bar.to_json())


@app.get("/api/analytics/matrix")
def analytics_matrix():
    matrix = rec_module.InteractionMatrix()
    sparsity = matrix.get_sparsity()

    if matrix.matrix_df.empty:
        return {"sparsity": sparsity, "figure": None}

    movies_df = database.get_all_movies()
    users_df = database.get_all_users()

    user_order = sorted(users_df["user_id"].tolist(), key=lambda uid: int(uid[1:]))
    movie_order = sorted(movies_df["movie_id"].tolist(), key=lambda mid: int(mid[1:]))

    utility = matrix.matrix_df.reindex(index=user_order, columns=movie_order)

    hover_labels = utility.map(
        lambda r: "Unobserved" if pd.isna(r) else f"{float(r):.1f} / 5"
    )

    heat = go.Figure(
        data=go.Heatmap(
            z=utility.fillna(0.0).values,
            x=utility.columns.tolist(),
            y=utility.index.tolist(),
            customdata=hover_labels.values,
            colorscale=[
                [0, "#f3f6f9"],
                [0.18, "#e2edf8"],
                [0.55, "#79afe2"],
                [1, "#0071e3"],
            ],
            zmin=0,
            zmax=5,
            xgap=2,
            ygap=2,
            colorbar=dict(
                title="Rating",
                tickvals=[0, 1, 2, 3, 4, 5],
                ticktext=["—", "1", "2", "3", "4", "5"],
            ),
            hovertemplate=(
                "Subscriber: %{y}<br>Title: %{x}<br>Rating: %{customdata}<extra></extra>"
            ),
        )
    )
    heat.update_xaxes(title="Movie", tickangle=-45, side="bottom")
    heat.update_yaxes(title="Subscriber", autorange="reversed")
    heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=11),
        margin=dict(l=0, r=0, t=40, b=0),
        height=535,
    )
    return {"sparsity": sparsity, "figure": json.loads(heat.to_json())}


# ── Vercel serverless handler (supports both ASGI direct and Mangum adapter) ──
try:
    from mangum import Mangum
    handler = Mangum(app)
except Exception:
    handler = app
