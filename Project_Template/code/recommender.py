"""
OOPJ & Python Module: Collaborative Filtering & Hybrid Recommendation Architecture
Curriculum: JNTUK R23 Regulation - II B.Tech I Sem (AI & DS)
Subjects: Object-Oriented Programming through Java (OOP Principles) & Python (k-NN Collaborative Filtering)
Project Code: 26 | Team: TEAM-18

Core Theoretical Components:
- Item-Based Collaborative Filtering using Cosine Similarity Metric:
  Sim(i, j) = (v_i · v_j) / (||v_i||_2 * ||v_j||_2)
- Hybrid Blended Scoring Model:
  Score(u, i) = α * Score_kNN(u, i) + (1 - α) * Centrality_Graph(i)
- Cold-Start Mitigation via DMGT Equivalence Class Stratification.
"""

import json
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from database import get_connection, get_all_movies, get_all_users, get_user_watch_history
from discrete_math import compute_equivalence_classes, get_stratified_catalog_distribution
from graph_engine import CoWatchGraph, build_cowatch_graph_from_db


class ContentItem:
    """
    OOP Entity: Encapsulates media catalog properties and behavioral invariants.
    """

    def __init__(self, movie_id: str, title: str, release_year: int,
                 language: str, primary_genre: str, secondary_genre: Optional[str],
                 director: str, cast_members: List[str], synopsis: str,
                 avg_rating: float, popularity_score: float,
                 duration_min: int = 120, accent_color: str = "#4F46E5"):
        self.movie_id = movie_id
        self.title = title
        self.release_year = release_year
        self.language = language
        self.primary_genre = primary_genre
        self.secondary_genre = secondary_genre
        self.director = director
        self.cast_members = cast_members
        self.synopsis = synopsis
        self.avg_rating = avg_rating
        self.popularity_score = popularity_score
        self.duration_min = duration_min
        self.accent_color = accent_color

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentItem":
        cast_raw = data.get("cast_members", "[]")
        cast_list = json.loads(cast_raw) if isinstance(cast_raw, str) else cast_raw
        return cls(
            movie_id=data["movie_id"],
            title=data["title"],
            release_year=data["release_year"],
            language=data["language"],
            primary_genre=data["primary_genre"],
            secondary_genre=data.get("secondary_genre"),
            director=data["director"],
            cast_members=cast_list,
            synopsis=data.get("synopsis", ""),
            avg_rating=float(data.get("avg_rating", 0.0)),
            popularity_score=float(data.get("popularity_score", 50.0)),
            duration_min=int(data.get("duration_min", 120)),
            accent_color=data.get("accent_color", "#4F46E5")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "release_year": self.release_year,
            "language": self.language,
            "primary_genre": self.primary_genre,
            "secondary_genre": self.secondary_genre,
            "director": self.director,
            "cast_members": self.cast_members,
            "synopsis": self.synopsis,
            "avg_rating": self.avg_rating,
            "popularity_score": self.popularity_score,
            "duration_min": self.duration_min,
            "accent_color": self.accent_color
        }


class Subscriber:
    """
    OOP Entity: Encapsulates subscriber profile, linguistic constraints, and watch interactions.
    """

    def __init__(self, user_id: str, name: str, age: int,
                 primary_language: str, secondary_language: Optional[str],
                 preferred_genres: List[str], persona_desc: str = ""):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.primary_language = primary_language
        self.secondary_language = secondary_language
        self.preferred_genres = preferred_genres
        self.persona_desc = persona_desc
        self.watch_history: List[Dict[str, Any]] = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscriber":
        genres_raw = data.get("preferred_genres", "[]")
        genres_list = json.loads(genres_raw) if isinstance(genres_raw, str) else genres_raw
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            age=data["age"],
            primary_language=data["primary_language"],
            secondary_language=data.get("secondary_language"),
            preferred_genres=genres_list,
            persona_desc=data.get("persona_desc", "")
        )

    def load_history(self, history_records: List[Dict[str, Any]]) -> None:
        self.watch_history = history_records

    def get_watched_movie_ids(self) -> List[str]:
        return [record["movie_id"] for record in self.watch_history]


class InteractionMatrix:
    """
    Manages the Sparse User-Item Utility Matrix R ∈ ℝ^{|U| × |M|}.
    Provides tensor normalization and sparsity diagnostic telemetry.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.matrix_df = pd.DataFrame()
        self.movie_ids: List[str] = []
        self.user_ids: List[str] = []
        self._build_matrix()

    def _build_matrix(self) -> None:
        conn = get_connection(self.db_path)
        query = "SELECT user_id, movie_id, rating FROM watch_history;"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            self.matrix_df = df.pivot(index="user_id", columns="movie_id", values="rating")
            self.user_ids = list(self.matrix_df.index)
            self.movie_ids = list(self.matrix_df.columns)

    def get_sparsity(self) -> float:
        """Calculates matrix sparsity: 1.0 - (Non-Zero Ratings / (Total Matrix Entries))."""
        if self.matrix_df.empty:
            return 1.0
        total_elements = self.matrix_df.shape[0] * self.matrix_df.shape[1]
        observed_ratings = self.matrix_df.count().sum()
        if total_elements == 0:
            return 1.0
        return round(1.0 - (observed_ratings / total_elements), 4)

    def get_item_vectors(self, fill_value: float = 0.0) -> pd.DataFrame:
        """Returns transposed item rating vectors (rows: movie_id, cols: user_id)."""
        if self.matrix_df.empty:
            return pd.DataFrame()
        return self.matrix_df.fillna(fill_value).T


class KNNRecommender:
    """
    Item-Based k-Nearest Neighbors Collaborative Filter.
    Computes pairwise Cosine Sim across user rating vectors.
    """

    def __init__(self, interaction_matrix: InteractionMatrix, k: int = 5):
        self.interaction_matrix = interaction_matrix
        self.k = k
        self.item_similarity_df = pd.DataFrame()
        self.item_vectors_df = pd.DataFrame()
        self._fit()

    def _fit(self) -> None:
        self.item_vectors_df = self.interaction_matrix.get_item_vectors(fill_value=0.0)
        if not self.item_vectors_df.empty:
            similarity_matrix = cosine_similarity(self.item_vectors_df.values)
            self.item_similarity_df = pd.DataFrame(
                similarity_matrix,
                index=self.item_vectors_df.index,
                columns=self.item_vectors_df.index
            )

    def get_movie_vector(self, movie_id: str) -> Optional[np.ndarray]:
        if movie_id in self.item_vectors_df.index:
            return self.item_vectors_df.loc[movie_id].values
        return None

    def get_stepwise_vector_math(self, movie_a: str, movie_b: str) -> Dict[str, Any]:
        """
        Step-by-Step Mathematical Decomposition of Cosine Similarity for the Model Lab:
        Sim(u, v) = (u · v) / (||u||_2 * ||v||_2)
        """
        vec_a = self.get_movie_vector(movie_a)
        vec_b = self.get_movie_vector(movie_b)

        if vec_a is None or vec_b is None:
            return {
                "error": "One or both movie vectors not found in utility matrix.",
                "cosine_similarity": 0.0
            }

        dot_product = float(np.dot(vec_a, vec_b))
        norm_a = float(np.linalg.norm(vec_a))
        norm_b = float(np.linalg.norm(vec_b))

        denominator = norm_a * norm_b
        similarity = float(dot_product / denominator) if denominator > 0 else 0.0

        user_labels = list(self.item_vectors_df.columns)
        return {
            "movie_a": movie_a,
            "movie_b": movie_b,
            "users": user_labels,
            "vector_a": [float(x) for x in vec_a],
            "vector_b": [float(x) for x in vec_b],
            "dot_product": round(dot_product, 4),
            "norm_a": round(norm_a, 4),
            "norm_b": round(norm_b, 4),
            "denominator": round(denominator, 4),
            "cosine_similarity": round(similarity, 4)
        }

    def predict_user_scores(self, user_id: str, watched_dict: Dict[str, float],
                           all_movie_ids: List[str]) -> Dict[str, float]:
        """
        Predicts ratings for unobserved items using top-k similar watched items.
        """
        if self.item_similarity_df.empty or not watched_dict:
            return {}

        predictions = {}
        unwatched_ids = [m for m in all_movie_ids if m not in watched_dict]

        for target_movie in unwatched_ids:
            if target_movie not in self.item_similarity_df.index:
                continue

            sim_series = self.item_similarity_df.loc[target_movie]

            # Filter to items the user has watched
            watched_sims = []
            for w_id, w_rating in watched_dict.items():
                if w_id in sim_series.index:
                    sim = sim_series[w_id]
                    if sim > 0:  # Positively correlated neighbors
                        watched_sims.append((w_id, sim, w_rating))

            if not watched_sims:
                continue

            # Sort by similarity and take top k
            watched_sims.sort(key=lambda x: x[1], reverse=True)
            top_neighbors = watched_sims[:self.k]

            numerator = sum(sim * rating for _, sim, rating in top_neighbors)
            denominator = sum(sim for _, sim, _ in top_neighbors)

            if denominator > 0:
                predictions[target_movie] = round(numerator / denominator, 3)

        return predictions


class HybridScoringEngine:
    """
    Hybrid Recommender blending:
    1. Item-Based k-NN Collaborative Filtering (Personalized Tastes)
    2. Co-Watch Graph Normalized Degree Centrality (Catalog Connectivity)
    3. Linguistic Affinity Boosting & DMGT Partition Cold-Start Fallback

    Mathematical Master Formula:
    Score(u, i) = α * Score_kNN(u, i) + (1 - α) * Centrality_Graph(i)
    """

    def __init__(self, k_neighbors: int = 5, alpha: float = 0.60, db_path: Optional[str] = None):
        self.k_neighbors = k_neighbors
        self.alpha = alpha
        self.db_path = db_path
        self.refresh()

    def refresh(self) -> None:
        """Reloads interaction states and re-fits algorithmic models."""
        self.matrix = InteractionMatrix(self.db_path)
        self.knn = KNNRecommender(self.matrix, k=self.k_neighbors)
        self.graph = build_cowatch_graph_from_db(self.db_path)
        self.all_movies = [ContentItem.from_dict(row) for _, row in get_all_movies(self.db_path).iterrows()]
        self.movie_map = {m.movie_id: m for m in self.all_movies}

    def set_hyperparameters(self, k_neighbors: int, alpha: float) -> None:
        self.k_neighbors = k_neighbors
        self.alpha = alpha
        self.knn.k = k_neighbors

    def get_static_popular_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Baseline Benchmark: Demonstrates the problem statement.
        Displays identical top-popularity titles to every user regardless of language or taste.
        """
        sorted_catalog = sorted(self.all_movies, key=lambda m: m.popularity_score, reverse=True)
        results = []
        for rank, item in enumerate(sorted_catalog[:limit], 1):
            d = item.to_dict()
            d["rank"] = rank
            d["recommendation_type"] = "Static Most Popular"
            d["why_recommended"] = f"Global Popularity Score: {item.popularity_score}/100"
            results.append(d)
        return results

    def get_personalized_recommendations(self, subscriber: Subscriber, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Produces the personalized StreamGlass AI feed:
        Evaluates k-NN score, graph centrality, linguistic affinity, and cold-start mitigations.
        """
        watched_records = subscriber.watch_history
        watched_dict = {rec["movie_id"]: float(rec["rating"]) for rec in watched_records}
        watched_ids = set(watched_dict.keys())

        centralities = self.graph.calculate_degree_centrality()
        max_cent = max(centralities.values()) if centralities and max(centralities.values()) > 0 else 1.0

        # Handle genuine Cold Start (e.g. U110 Meera Nair)
        if len(watched_dict) == 0:
            return self._get_cold_start_recommendations(subscriber, limit)

        # 1. Compute k-NN predicted scores
        all_ids = [m.movie_id for m in self.all_movies]
        knn_scores = self.knn.predict_user_scores(subscriber.user_id, watched_dict, all_ids)

        scored_candidates = []

        for movie in self.all_movies:
            if movie.movie_id in watched_ids:
                continue

            m_id = movie.movie_id
            knn_raw = knn_scores.get(m_id, 0.0)

            # Normalize kNN (rating 1-5 mapped to 0-1)
            norm_knn = (knn_raw / 5.0) if knn_raw > 0 else 0.20

            # Normalize Graph Centrality (0-1)
            norm_cent = centralities.get(m_id, 0.0) / max_cent

            # Linguistic & Genre Affinity Prior
            lang_boost = 1.0
            if movie.language == subscriber.primary_language:
                lang_boost = 1.25
            elif movie.language == subscriber.secondary_language:
                lang_boost = 1.10

            genre_boost = 1.0
            if movie.primary_genre in subscriber.preferred_genres:
                genre_boost = 1.20

            # Master Blended Score
            hybrid_score = (self.alpha * norm_knn + (1.0 - self.alpha) * norm_cent) * lang_boost * genre_boost
            confidence_pct = min(99, int(round(hybrid_score * 85, 0)))

            # Transparent reason chips
            reasons = []
            if knn_raw > 0:
                reasons.append(f"Predicted Rating: {knn_raw:.1f}★ (k-NN)")
            if norm_cent > 0.4:
                reasons.append("Catalog Network Hub")
            if movie.language == subscriber.primary_language:
                reasons.append(f"Primary Lang ({movie.language})")
            if movie.primary_genre in subscriber.preferred_genres:
                reasons.append(f"Favorite Genre ({movie.primary_genre})")

            why_text = " • ".join(reasons) if reasons else "Hybrid Co-Watch Discovery"

            item_dict = movie.to_dict()
            item_dict["hybrid_score"] = round(hybrid_score, 4)
            item_dict["confidence_pct"] = confidence_pct
            item_dict["why_recommended"] = why_text
            item_dict["norm_knn"] = round(norm_knn, 3)
            item_dict["norm_cent"] = round(norm_cent, 3)
            scored_candidates.append(item_dict)

        # Sort descending by hybrid score
        scored_candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return scored_candidates[:limit]

    def _get_cold_start_recommendations(self, subscriber: Subscriber, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Cold Start Mitigation via DMGT Equivalence Partitions:
        Guarantees diverse regional discovery across quotient classes.
        """
        all_dicts = [m.to_dict() for m in self.all_movies]
        quotient = compute_equivalence_classes(all_dicts)
        stratified = get_stratified_catalog_distribution(quotient, top_n_per_class=1)

        # Sort stratified items prioritizing subscriber's stated linguistic preference
        def cold_start_key(m):
            priority = 0
            if m["language"] == subscriber.primary_language:
                priority += 50
            if m["primary_genre"] in subscriber.preferred_genres:
                priority += 30
            return (priority, m["avg_rating"], m["popularity_score"])

        stratified.sort(key=cold_start_key, reverse=True)

        results = []
        for item in stratified[:limit]:
            item["hybrid_score"] = round(item["avg_rating"] / 5.0, 3)
            item["confidence_pct"] = int(item["avg_rating"] * 18)
            item["why_recommended"] = f"DMGT Partition Top Pick [{item['language']} :: {item['primary_genre']}]"
            results.append(item)
        return results


if __name__ == "__main__":
    from database import seed_database
    seed_database()
    engine = HybridScoringEngine()
    print("[OOPJ Engine] Recommender initialized successfully.")
    static_feed = engine.get_static_popular_feed(limit=5)
    print(f"[OOPJ Engine] Static Popular Feed Top 1: {static_feed[0]['title']}")
