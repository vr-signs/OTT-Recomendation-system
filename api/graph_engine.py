"""
ADSA Module: Advanced Data Structures & Algorithms (Unit 2: Graph Data Structures & Traversals)
Curriculum: JNTUK R23 Regulation - II B.Tech I Sem (AI & DS)
Subject: Advanced Data Structures and Algorithms (ADSA)
Project Code: 26 | Team: TEAM-18

Data Structure Implementation:
- Custom Undirected Weighted Graph: G = (V, E, W) using Adjacency Lists.
- Vertex Set V: Unique regional catalog titles.
- Edge Set E: Co-watch relationships established by mutual subscriber viewership.
- Weight Function W(u, v): Mutual viewer frequency adjusted by ratings & completion percentages.
- Graph Algorithms: Custom Breadth-First Search (BFS), Normalized Degree Centrality, and Plotly 2D Force Layout.
"""

from collections import deque
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx
import plotly.graph_objects as go
import pandas as pd


class CoWatchGraph:
    """
    Custom Adjacency List Graph Data Structure conforming to ADSA Unit 2 formalisms.
    Stores undirected weighted edges W(u, v) representing subscriber co-viewership affinity.
    """

    def __init__(self):
        # adj_list[node_u][node_v] = weight
        self.adj_list: Dict[str, Dict[str, float]] = {}
        self.node_metadata: Dict[str, Dict[str, Any]] = {}

    def add_node(self, movie_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Adds a vertex v ∈ V to the graph."""
        if movie_id not in self.adj_list:
            self.adj_list[movie_id] = {}
            self.node_metadata[movie_id] = metadata or {}

    def add_edge(self, u: str, v: str, weight: float) -> None:
        """
        Adds an undirected edge (u, v) ∈ E with symmetric weight W(u, v) = W(v, u).
        Self-loops (u == v) are rejected to preserve simple graph topology.
        """
        if u == v:
            return
        self.add_node(u)
        self.add_node(v)

        # Undirected symmetric edge assignment
        self.adj_list[u][v] = round(weight, 3)
        self.adj_list[v][u] = round(weight, 3)

    def get_neighbors(self, u: str) -> Dict[str, float]:
        """Returns adjacent vertices and edge weights for node u."""
        return self.adj_list.get(u, {})

    def breadth_first_search(self, start_movie_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        ADSA Unit 2: Breadth-First Search (BFS) Traversal using a FIFO Queue.
        Time Complexity: O(|V| + |E|)
        Space Complexity: O(|V|)
        Returns:
            - visited_order: List of nodes in order of discovery
            - levels: Distance horizon from start_movie_id
            - tree_edges: Spanning tree discovery edges
        """
        if start_movie_id not in self.adj_list:
            return {"visited_order": [], "levels": {}, "tree_edges": []}

        visited = {start_movie_id}
        queue = deque([(start_movie_id, 0)])
        visited_order = []
        levels = {start_movie_id: 0}
        tree_edges = []

        while queue:
            current, depth = queue.popleft()
            visited_order.append(current)

            if depth < max_depth:
                # Sort neighbors by highest weight for prioritized traversal
                sorted_neighbors = sorted(
                    self.adj_list[current].items(),
                    key=lambda item: item[1],
                    reverse=True
                )

                for neighbor, weight in sorted_neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        levels[neighbor] = depth + 1
                        tree_edges.append((current, neighbor, weight))
                        queue.append((neighbor, depth + 1))

        return {
            "visited_order": visited_order,
            "levels": levels,
            "tree_edges": tree_edges
        }

    def calculate_degree_centrality(self) -> Dict[str, float]:
        """
        Calculates Normalized Weighted Degree Centrality:
        C_D(v) = ∑ W(v, u) / (|V| - 1)
        Identifies catalog hub movies that bridge distinct regional subscriber communities.
        """
        num_vertices = len(self.adj_list)
        if num_vertices <= 1:
            return {node: 0.0 for node in self.adj_list}

        centrality = {}
        normalizer = num_vertices - 1

        for node, neighbors in self.adj_list.items():
            total_weight = sum(neighbors.values())
            centrality[node] = round(total_weight / normalizer, 4)

        return centrality

    def get_graph_metrics(self) -> Dict[str, Any]:
        """Calculates topological summary metrics for the co-watch network."""
        num_v = len(self.adj_list)
        num_e = sum(len(neighbors) for neighbors in self.adj_list.values()) // 2
        possible_e = (num_v * (num_v - 1)) / 2 if num_v > 1 else 1
        density = round(num_e / possible_e, 4) if possible_e > 0 else 0.0

        centralities = self.calculate_degree_centrality()
        top_hub = max(centralities.items(), key=lambda x: x[1]) if centralities else ("None", 0.0)

        return {
            "num_nodes": num_v,
            "num_edges": num_e,
            "density": density,
            "top_hub_movie": top_hub[0],
            "top_hub_centrality": top_hub[1]
        }

    def to_networkx(self) -> nx.Graph:
        """Converts the custom Adjacency List into a NetworkX Graph."""
        G = nx.Graph()
        for node, meta in self.node_metadata.items():
            G.add_node(node, **meta)

        for u, neighbors in self.adj_list.items():
            for v, weight in neighbors.items():
                if u < v:  # Add undirected edge once
                    G.add_edge(u, v, weight=weight)
        return G

    def generate_plotly_network(self, highlight_nodes: Optional[List[str]] = None) -> go.Figure:
        """
        Renders an interactive 2D Force-Directed Graph using Plotly with
        custom node sizes based on centrality and edge thickness by co-watch weight.
        """
        G = self.to_networkx()
        if len(G.nodes) == 0:
            fig = go.Figure()
            fig.update_layout(title="No Co-Watch Interactions Available")
            return fig

        pos = nx.spring_layout(G, k=0.45, seed=42)
        centralities = self.calculate_degree_centrality()

        # Build Edge Traces
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in G.edges(data=True):
            u, v, data = edge
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(f"{u} ↔ {v} (Weight: {data.get('weight', 1.0)})")

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.2, color='rgba(255, 255, 255, 0.20)'),
            hoverinfo='none',
            mode='lines'
        )

        # Build Node Traces
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_hover_texts = []
        node_labels = []

        lang_color_map = {
            "Telugu": "#FF6B6B",
            "Tamil": "#4ECDC4",
            "Hindi": "#FFE66D",
            "English": "#A78BFA"
        }

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            meta = self.node_metadata.get(node, {})
            title = meta.get("title", node)
            language = meta.get("language", "Telugu")
            genre = meta.get("primary_genre", "Action")
            cent = centralities.get(node, 0.0)

            node_labels.append(title[:14] + ("…" if len(title) > 14 else ""))

            # Emphasize highlighted nodes
            if highlight_nodes and node in highlight_nodes:
                node_colors.append("#00F0FF")
                node_sizes.append(32 + cent * 40)
            else:
                node_colors.append(lang_color_map.get(language, "#94A3B8"))
                node_sizes.append(18 + cent * 30)

            hover_text = (
                f"<b>{title}</b> ({meta.get('release_year', 'N/A')})<br>"
                f"Language: {language} | Genre: {genre}<br>"
                f"Degree Centrality: {cent:.4f}<br>"
                f"Rating: {meta.get('avg_rating', 0.0)} ★"
            )
            node_hover_texts.append(hover_text)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_labels,
            textposition="top center",
            textfont=dict(size=9, color="#E2E8F0"),
            hoverinfo='text',
            hovertext=node_hover_texts,
            marker=dict(
                showscale=False,
                color=node_colors,
                size=node_sizes,
                line=dict(width=1.5, color='rgba(255, 255, 255, 0.60)')
            )
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=20, t=30),
            plot_bgcolor='rgba(15, 23, 42, 0.0)',
            paper_bgcolor='rgba(15, 23, 42, 0.0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=480
        )
        return fig


def build_cowatch_graph_from_db(db_path: str = None) -> CoWatchGraph:
    """
    Constructs the co-watch network from SQLite interactions:
    For every pair of movies watched by subscriber s, compute co-viewership affinity:
    Affinity(u, v) = ∑_s [ (rating_{s,u} + rating_{s,v}) / 10 * min(watch_pct_{s,u}, watch_pct_{s,v}) / 100 ]
    """
    from database import get_connection, get_all_movies
    conn = get_connection(db_path)

    movies_df = get_all_movies(db_path)
    movie_dict = {row["movie_id"]: row.to_dict() for _, row in movies_df.iterrows()}

    graph = CoWatchGraph()
    for m_id, meta in movie_dict.items():
        graph.add_node(m_id, meta)

    # Query all subscriber watch records
    query = """
    SELECT user_id, movie_id, rating, watch_percentage
    FROM watch_history
    ORDER BY user_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Group by subscriber to generate co-watch pairs
    user_groups = df.groupby("user_id")

    co_watch_weights: Dict[Tuple[str, str], float] = {}

    for user_id, group in user_groups:
        records = group.to_dict(orient="records")
        num_watched = len(records)

        for i in range(num_watched):
            for j in range(i + 1, num_watched):
                item_u = records[i]
                item_v = records[j]
                m_u, m_v = item_u["movie_id"], item_v["movie_id"]

                # Ensure canonical pair ordering
                pair = (min(m_u, m_v), max(m_u, m_v))

                # Weight calculation factoring in rating and completion percentage
                r_factor = (item_u["rating"] + item_v["rating"]) / 10.0
                pct_factor = min(item_u["watch_percentage"], item_v["watch_percentage"]) / 100.0
                edge_contrib = r_factor * pct_factor

                co_watch_weights[pair] = co_watch_weights.get(pair, 0.0) + edge_contrib

    # Insert computed edges into custom graph
    for (u, v), weight in co_watch_weights.items():
        graph.add_edge(u, v, weight)

    return graph


if __name__ == "__main__":
    from database import seed_database
    seed_database()
    cw_graph = build_cowatch_graph_from_db()
    metrics = cw_graph.get_graph_metrics()
    print(f"[ADSA Engine] Co-Watch Graph Metrics: {metrics}")

    # Test BFS from hub movie
    bfs_result = cw_graph.breadth_first_search("M101", max_depth=2)
    print(f"[ADSA Engine] BFS Discovery from M101: {bfs_result['visited_order']}")
