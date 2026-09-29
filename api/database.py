"""
DBMS Module: Relational Schema, Normalization & SQLite Storage Engine
Curriculum: JNTUK R23 Regulation - II B.Tech I Sem (AI & DS)
Subjects: Database Management Systems (U1: ER Model, U2: Relational Schema & 3NF)
Project Code: 26 | Team: TEAM-18
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "ott_platform.db")
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Returns a SQLite connection with Foreign Key constraints enabled and WAL mode."""
    target_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(target_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None) -> None:
    """
    Initializes the 3NF relational schema for the OTT Platform:
    - Users (Entity)
    - Movies (Entity)
    - WatchHistory (Relational Transaction with Composite Business Key)
    """
    target_path = db_path or DEFAULT_DB_PATH
    conn = get_connection(target_path)
    cursor = conn.cursor()

    cursor.executescript("""
    -- Table 1: Users Entity (3NF Compliant)
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK (age >= 10),
        primary_language TEXT NOT NULL,
        secondary_language TEXT,
        preferred_genres TEXT NOT NULL, -- JSON Array of genres
        persona_desc TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Table 2: Movies Entity (3NF Compliant)
    CREATE TABLE IF NOT EXISTS movies (
        movie_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        release_year INTEGER NOT NULL CHECK (release_year >= 1900),
        language TEXT NOT NULL,
        primary_genre TEXT NOT NULL,
        secondary_genre TEXT,
        director TEXT NOT NULL,
        cast_members TEXT NOT NULL, -- JSON Array of cast
        synopsis TEXT,
        avg_rating REAL DEFAULT 0.0 CHECK (avg_rating >= 0.0 AND avg_rating <= 5.0),
        popularity_score REAL DEFAULT 50.0 CHECK (popularity_score >= 0 AND popularity_score <= 100),
        duration_min INTEGER DEFAULT 120,
        accent_color TEXT DEFAULT '#4F46E5'
    );

    -- Table 3: WatchHistory Transaction Table (Relational Intersection)
    CREATE TABLE IF NOT EXISTS watch_history (
        history_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        movie_id TEXT NOT NULL,
        watch_percentage REAL NOT NULL CHECK (watch_percentage >= 0.0 AND watch_percentage <= 100.0),
        rating REAL NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
        watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
    );

    -- Table 4: UserMoviePreferences (Explicit Like/Dislike Feedback Signals)
    CREATE TABLE IF NOT EXISTS user_movie_preferences (
        pref_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        movie_id TEXT NOT NULL,
        preference TEXT NOT NULL CHECK (preference IN ('like', 'dislike')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
    );

    -- Relational Performance Optimization: B-Tree Indexes
    CREATE INDEX IF NOT EXISTS idx_watch_user ON watch_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_watch_movie ON watch_history(movie_id);
    CREATE INDEX IF NOT EXISTS idx_pref_user ON user_movie_preferences(user_id);
    CREATE INDEX IF NOT EXISTS idx_pref_movie ON user_movie_preferences(movie_id);
    CREATE INDEX IF NOT EXISTS idx_movie_lang_genre ON movies(language, primary_genre);
    CREATE INDEX IF NOT EXISTS idx_movie_popularity ON movies(popularity_score DESC);
    """)

    conn.commit()
    conn.close()


def seed_database(db_path: str = None, force: bool = False) -> None:
    """
    Automated transactional seeder: Ingests rich multi-regional datasets
    from sample_data/ (users.json, movies.json, watch_history.csv).
    """
    target_path = db_path or DEFAULT_DB_PATH
    init_db(target_path)
    conn = get_connection(target_path)
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]

    if user_count > 0 and not force:
        conn.close()
        return

    if force:
        cursor.execute("DELETE FROM user_movie_preferences;")
        cursor.execute("DELETE FROM watch_history;")
        cursor.execute("DELETE FROM movies;")
        cursor.execute("DELETE FROM users;")
        conn.commit()

    users_file = os.path.join(SAMPLE_DATA_DIR, "users.json")
    movies_file = os.path.join(SAMPLE_DATA_DIR, "movies.json")
    history_file = os.path.join(SAMPLE_DATA_DIR, "watch_history.csv")

    # 1. Ingest Users
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            users_data = json.load(f)
            for u in users_data:
                cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, name, age, primary_language, secondary_language, preferred_genres, persona_desc)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    u["user_id"],
                    u["name"],
                    u["age"],
                    u["primary_language"],
                    u.get("secondary_language"),
                    json.dumps(u["preferred_genres"]),
                    u.get("persona_desc", "")
                ))

    # 2. Ingest Movies
    if os.path.exists(movies_file):
        with open(movies_file, "r", encoding="utf-8") as f:
            movies_data = json.load(f)
            for m in movies_data:
                cursor.execute("""
                INSERT OR REPLACE INTO movies
                (movie_id, title, release_year, language, primary_genre, secondary_genre,
                 director, cast_members, synopsis, avg_rating, popularity_score, duration_min, accent_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    m["movie_id"],
                    m["title"],
                    m["release_year"],
                    m["language"],
                    m["primary_genre"],
                    m.get("secondary_genre"),
                    m["director"],
                    json.dumps(m["cast"]),
                    m.get("synopsis", ""),
                    m.get("avg_rating", 0.0),
                    m.get("popularity_score", 50.0),
                    m.get("duration_min", 120),
                    m.get("accent_color", "#4F46E5")
                ))

    # 3. Ingest Watch History
    if os.path.exists(history_file):
        df_history = pd.read_csv(history_file)
        for _, row in df_history.iterrows():
            cursor.execute("""
            INSERT OR REPLACE INTO watch_history
            (history_id, user_id, movie_id, watch_percentage, rating, watched_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (
                str(row["history_id"]),
                str(row["user_id"]),
                str(row["movie_id"]),
                float(row["watch_percentage"]),
                float(row["rating"]),
                str(row["watched_at"])
            ))

    conn.commit()
    conn.close()


def get_all_users(db_path: str = None) -> pd.DataFrame:
    """Retrieves all registered subscribers as a pandas DataFrame."""
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM users ORDER BY user_id ASC;", conn)
    conn.close()
    return df


def get_all_movies(db_path: str = None) -> pd.DataFrame:
    """Retrieves catalog movies with full metadata as a pandas DataFrame."""
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM movies ORDER BY popularity_score DESC;", conn)
    conn.close()
    return df


def get_user_watch_history(user_id: str, db_path: str = None) -> pd.DataFrame:
    """Joins watch_history with movies to retrieve a specific subscriber's watched catalog."""
    conn = get_connection(db_path)
    query = """
    SELECT 
        h.history_id,
        h.user_id,
        h.movie_id,
        m.title,
        m.language,
        m.primary_genre,
        m.accent_color,
        h.watch_percentage,
        h.rating,
        h.watched_at
    FROM watch_history h
    JOIN movies m ON h.movie_id = m.movie_id
    WHERE h.user_id = ?
    ORDER BY h.watched_at DESC;
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df


def get_interaction_matrix(db_path: str = None) -> pd.DataFrame:
    """Constructs the User-Item Rating Utility Matrix (rows: users, cols: movies)."""
    conn = get_connection(db_path)
    query = """
    SELECT user_id, movie_id, rating
    FROM watch_history;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        return pd.DataFrame()
    return df.pivot(index="user_id", columns="movie_id", values="rating")


def record_user_interaction(user_id: str, movie_id: str, watch_percentage: float, rating: float, db_path: str = None) -> str:
    """
    Records a live user interaction, maintaining ACID properties,
    and dynamically recomputes the movie's aggregate rating.
    """
    history_id = f"H{int(datetime.now().timestamp() * 1000)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO watch_history (history_id, user_id, movie_id, watch_percentage, rating, watched_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (history_id, user_id, movie_id, float(watch_percentage), float(rating), now_str))

        # Recompute average rating for this movie
        cursor.execute("""
        UPDATE movies
        SET avg_rating = (
            SELECT ROUND(AVG(rating), 2)
            FROM watch_history
            WHERE movie_id = ?
        )
        WHERE movie_id = ?;
        """, (movie_id, movie_id))

        conn.commit()
        return history_id
    finally:
        conn.close()


def set_user_movie_preference(user_id: str, movie_id: str, preference: str, db_path: str = None):
    """
    Records or toggles a subscriber's movie preference ('like' or 'dislike').
    If preference is already set to the same value, clicking it toggles/removes it.
    If clicked to the opposite value, it updates.
    Returns the new state: 'like', 'dislike', or None (if removed).
    """
    pref_clean = str(preference).strip().lower()
    if pref_clean not in ("like", "dislike"):
        return None

    target_path = db_path or DEFAULT_DB_PATH
    init_db(target_path)
    conn = get_connection(target_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT preference FROM user_movie_preferences WHERE user_id = ? AND movie_id = ?;",
            (user_id, movie_id)
        )
        row = cursor.fetchone()
        if row:
            current_pref = row[0]
            if current_pref == pref_clean:
                cursor.execute(
                    "DELETE FROM user_movie_preferences WHERE user_id = ? AND movie_id = ?;",
                    (user_id, movie_id)
                )
                conn.commit()
                return None
            else:
                cursor.execute(
                    "UPDATE user_movie_preferences SET preference = ?, created_at = CURRENT_TIMESTAMP WHERE user_id = ? AND movie_id = ?;",
                    (pref_clean, user_id, movie_id)
                )
                conn.commit()
                return pref_clean
        else:
            pref_id = f"P{int(datetime.now().timestamp() * 1000)}"
            cursor.execute(
                "INSERT INTO user_movie_preferences (pref_id, user_id, movie_id, preference) VALUES (?, ?, ?, ?);",
                (pref_id, user_id, movie_id, pref_clean)
            )
            conn.commit()
            return pref_clean
    finally:
        conn.close()


def get_user_movie_preferences(user_id: str, db_path: str = None) -> dict:
    """Retrieves all movie preferences for a subscriber as a dict: {movie_id: 'like' | 'dislike'}."""
    if not user_id:
        return {}
    target_path = db_path or DEFAULT_DB_PATH
    init_db(target_path)
    conn = get_connection(target_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT movie_id, preference FROM user_movie_preferences WHERE user_id = ?;",
            (user_id,)
        )
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    finally:
        conn.close()


def get_db_metrics(db_path: str = None) -> dict:
    """Returns relational database diagnostic telemetry."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users;")
    u_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM movies;")
    m_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM watch_history;")
    h_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA page_count;")
    page_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA page_size;")
    page_size = cursor.fetchone()[0]

    db_size_kb = round((page_count * page_size) / 1024, 2)

    conn.close()
    return {
        "user_count": u_count,
        "movie_count": m_count,
        "interaction_count": h_count,
        "database_size_kb": db_size_kb,
        "sqlite_version": sqlite3.sqlite_version
    }


def get_er_schema_metadata() -> dict:
    """
    Returns structured academic schema metadata for JNTUK R23 DBMS unit presentation.
    """
    return {
        "entities": [
            {
                "name": "Users",
                "type": "Strong Entity",
                "primary_key": "user_id",
                "attributes": ["user_id (PK)", "name", "age", "primary_language", "secondary_language", "preferred_genres", "persona_desc", "created_at"],
                "cardinality": "1 : N with WatchHistory"
            },
            {
                "name": "Movies",
                "type": "Strong Entity",
                "primary_key": "movie_id",
                "attributes": ["movie_id (PK)", "title", "release_year", "language", "primary_genre", "secondary_genre", "director", "cast_members", "avg_rating", "popularity_score", "duration_min", "accent_color"],
                "cardinality": "1 : N with WatchHistory"
            },
            {
                "name": "WatchHistory",
                "type": "Relational Intersection / Associative Entity",
                "primary_key": "history_id",
                "attributes": ["history_id (PK)", "user_id (FK -> Users)", "movie_id (FK -> Movies)", "watch_percentage", "rating", "watched_at"],
                "cardinality": "N : 1 with Users, N : 1 with Movies"
            }
        ],
        "normalization": {
            "1NF": "All attributes contain atomic scalar values; multi-valued fields (genres/cast) serialized with standard accessors.",
            "2NF": "Every non-prime attribute is fully functionally dependent on the Primary Key. No partial functional dependencies exist.",
            "3NF": "No transitive dependencies ($X \\rightarrow Y, Y \\rightarrow Z$). Movie language and genre belong to Content, not WatchHistory."
        }
    }


def add_movie(
    title: str,
    release_year: int,
    language: str,
    primary_genre: str,
    director: str = "",
    secondary_genre: str = None,
    duration_min: int = 120,
    accent_color: str = None,
    db_path: str = None
) -> str:
    """
    Adds a new movie to the catalog with ACID transaction safety.
    Returns the newly assigned movie_id.
    """
    if not title or not str(title).strip():
        raise ValueError("Movie title cannot be empty.")
    title = str(title).strip()
    language = str(language).strip() if language else "Regional"
    primary_genre = str(primary_genre).strip() if primary_genre else "Drama"
    director = str(director).strip() if director else "Independent"
    try:
        release_year = int(release_year)
    except (ValueError, TypeError):
        release_year = datetime.now().year
    try:
        duration_min = int(duration_min)
    except (ValueError, TypeError):
        duration_min = 120

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT movie_id FROM movies WHERE movie_id LIKE 'M%';")
    rows = cursor.fetchall()
    max_num = 0
    for (mid,) in rows:
        try:
            num = int(mid[1:])
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    movie_id = f"M{max_num + 1:02d}"

    if not accent_color:
        genre_colors = {
            "Action": "#e05638",
            "Drama": "#0071e3",
            "Thriller": "#8e44ad",
            "Comedy": "#f39c12",
            "Romance": "#e84393",
            "Sci-Fi": "#0984e3",
            "Crime": "#2d3436",
            "Horror": "#2c3e50"
        }
        accent_color = genre_colors.get(primary_genre, "#5f789c")

    cursor.execute("""
    INSERT INTO movies
    (movie_id, title, release_year, language, primary_genre, secondary_genre,
     director, cast_members, synopsis, avg_rating, popularity_score, duration_min, accent_color)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        movie_id,
        title,
        release_year,
        language,
        primary_genre,
        secondary_genre or None,
        director,
        json.dumps([director]),
        f"Catalog title: {title} directed by {director}.",
        0.0,
        55.0,
        duration_min,
        accent_color
    ))
    conn.commit()
    conn.close()
    return movie_id


def get_or_create_demo_subscriber(identifier: str, db_path: str = None) -> str:
    """
    Finds or creates a subscriber profile matching the login identifier.
    Supports email, user_id (e.g. U101), or username.
    """
    if not identifier:
        return "U101"
    ident = str(identifier).strip()
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Exact match on user_id
    cursor.execute("SELECT user_id FROM users WHERE LOWER(user_id) = LOWER(?);", (ident,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        conn.close()
        return user_id

    # 2. Match on name
    cursor.execute("SELECT user_id FROM users WHERE LOWER(name) = LOWER(?);", (ident,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        conn.close()
        return user_id

    # 3. If email like "user@domain.com", check if name matches prefix
    name_part = ident.split("@")[0].replace(".", " ").title()
    cursor.execute("SELECT user_id FROM users WHERE LOWER(name) = LOWER(?);", (name_part,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        conn.close()
        return user_id

    # 4. Generate a unique user_id for new subscriber
    cursor.execute("SELECT user_id FROM users WHERE user_id LIKE 'U%';")
    all_uids = cursor.fetchall()
    max_num = 100
    for (uid,) in all_uids:
        try:
            num = int(uid[1:])
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    new_user_id = f"U{max_num + 1}"
    display_name = name_part if name_part else ident

    cursor.execute("""
    INSERT INTO users (user_id, name, age, primary_language, secondary_language, preferred_genres, persona_desc)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (
        new_user_id,
        display_name,
        25,
        "Telugu",
        "English",
        json.dumps(["Drama", "Action"]),
        f"Signed-in subscriber account for {display_name}."
    ))
    conn.commit()
    conn.close()
    return new_user_id


# Auto-seed upon direct execution or import if database not present
if __name__ == "__main__":
    print("[DBMS Engine] Initializing and Seeding Database...")
    seed_database(force=True)
    metrics = get_db_metrics()
    print(f"[DBMS Engine] Setup Complete: {metrics}")
