"""
DMGT Module: Discrete Mathematics & Graph Theory (Unit 2: Relations & Partitions)
Curriculum: JNTUK R23 Regulation - II B.Tech I Sem (AI & DS)
Subject: Discrete Mathematics and Graph Theory (DMGT)
Project Code: 26 | Team: TEAM-18

Theoretical Focus:
Formal verification of Equivalence Relation R on Catalog Items:
R = { (x, y) ∈ S × S | Genre(x) = Genre(y) ∧ Language(x) = Language(y) }
Computation of Equivalence Classes [x]_R and Quotient Set S/R.
Proof of Partition Properties: Disjointness and Exhaustive Union.
"""

from typing import List, Dict, Tuple, Any, Set


def is_related(item_a: Dict[str, Any], item_b: Dict[str, Any]) -> bool:
    """
    Evaluates whether (item_a, item_b) ∈ R.
    Binary Relation Condition:
    item_a R item_b <=> (Genre(item_a) == Genre(item_b)) ∧ (Language(item_a) == Language(item_b))
    """
    same_genre = item_a.get("primary_genre") == item_b.get("primary_genre")
    same_language = item_a.get("language") == item_b.get("language")
    return same_genre and same_language


def verify_reflexivity(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Formal Proof of Reflexivity:
    A relation R on set S is reflexive iff ∀ x ∈ S, (x, x) ∈ R.
    """
    tested_count = len(items)
    violations = []

    for item in items:
        if not is_related(item, item):
            violations.append(item.get("movie_id"))

    is_valid = len(violations) == 0
    return {
        "property": "Reflexivity",
        "formula": "∀ x ∈ S, (x R x)",
        "is_satisfied": is_valid,
        "items_tested": tested_count,
        "violations": violations,
        "mathematical_proof": (
            "Let x ∈ S be an arbitrary media item with Primary Genre G_x and Language L_x. "
            "By the reflexive axiom of algebraic equality, G_x = G_x and L_x = L_x. "
            "Therefore, by definition of relation R, (x, x) ∈ R holds ∀ x ∈ S. Q.E.D."
        )
    }


def verify_symmetry(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Formal Proof of Symmetry:
    A relation R on set S is symmetric iff ∀ x, y ∈ S, (x R y) => (y R x).
    """
    violations = []
    pairs_tested = 0

    for i in range(len(items)):
        for j in range(len(items)):
            x = items[i]
            y = items[j]
            pairs_tested += 1
            if is_related(x, y):
                if not is_related(y, x):
                    violations.append((x.get("movie_id"), y.get("movie_id")))

    is_valid = len(violations) == 0
    return {
        "property": "Symmetry",
        "formula": "∀ x, y ∈ S, (x R y) ⟹ (y R x)",
        "is_satisfied": is_valid,
        "pairs_tested": pairs_tested,
        "violations": violations,
        "mathematical_proof": (
            "Assume x, y ∈ S such that (x, y) ∈ R. By definition of R, "
            "Genre(x) = Genre(y) and Language(x) = Language(y). "
            "By the symmetric property of identity equality (=), Genre(y) = Genre(x) and "
            "Language(y) = Language(x). Consequently, (y, x) ∈ R holds. Q.E.D."
        )
    }


def verify_transitivity(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Formal Proof of Transitivity:
    A relation R on set S is transitive iff ∀ x, y, z ∈ S, ((x R y) ∧ (y R z)) => (x R z).
    """
    violations = []
    triplets_tested = 0

    for x in items:
        for y in items:
            for z in items:
                triplets_tested += 1
                if is_related(x, y) and is_related(y, z):
                    if not is_related(x, z):
                        violations.append((x.get("movie_id"), y.get("movie_id"), z.get("movie_id")))

    is_valid = len(violations) == 0
    return {
        "property": "Transitivity",
        "formula": "∀ x, y, z ∈ S, ((x R y) ∧ (y R z)) ⟹ (x R z)",
        "is_satisfied": is_valid,
        "triplets_tested": triplets_tested,
        "violations": violations,
        "mathematical_proof": (
            "Assume x, y, z ∈ S such that (x R y) and (y R z). "
            "Then Genre(x) = Genre(y) and Genre(y) = Genre(z). By transitivity of equality, Genre(x) = Genre(z). "
            "Similarly, Language(x) = Language(y) and Language(y) = Language(z) yields Language(x) = Language(z). "
            "Hence, (x R z) ∈ R holds ∀ x, y, z ∈ S. Q.E.D."
        )
    }


def compute_equivalence_classes(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Computes the quotient set S/R = { [x]_R | x ∈ S },
    where [x]_R = { y ∈ S | y R x }.
    Returns a mapping of partition identifier to list of items.
    """
    quotient_set: Dict[str, List[Dict[str, Any]]] = {}

    for item in items:
        lang = item.get("language", "Unknown")
        genre = item.get("primary_genre", "Unknown")
        class_key = f"[{lang} :: {genre}]"

        if class_key not in quotient_set:
            quotient_set[class_key] = []
        quotient_set[class_key].append(item)

    return quotient_set


def verify_partition_theorem(items: List[Dict[str, Any]], quotient_set: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Verifies the Fundamental Theorem of Equivalence Relations:
    1. Disjointness: ∀ A, B ∈ S/R where A ≠ B, A ∩ B = ∅.
    2. Exhaustive Coverage: ⋃ [x] = S.
    3. Non-emptiness: ∀ A ∈ S/R, A ≠ ∅.
    """
    all_movie_ids = {item["movie_id"] for item in items}
    union_of_classes: Set[str] = set()
    pairwise_intersections = []
    class_keys = list(quotient_set.keys())

    # Check non-emptiness and pairwise disjointness
    for i in range(len(class_keys)):
        set_a = {item["movie_id"] for item in quotient_set[class_keys[i]]}
        union_of_classes.update(set_a)

        for j in range(i + 1, len(class_keys)):
            set_b = {item["movie_id"] for item in quotient_set[class_keys[j]]}
            intersection = set_a.intersection(set_b)
            if intersection:
                pairwise_intersections.append({
                    "class_a": class_keys[i],
                    "class_b": class_keys[j],
                    "overlap": list(intersection)
                })

    is_disjoint = len(pairwise_intersections) == 0
    is_exhaustive = union_of_classes == all_movie_ids
    non_empty = all(len(items_list) > 0 for items_list in quotient_set.values())

    return {
        "is_valid_partition": is_disjoint and is_exhaustive and non_empty,
        "num_classes": len(quotient_set),
        "total_universe_size": len(all_movie_ids),
        "union_coverage_size": len(union_of_classes),
        "disjoint_condition": is_disjoint,
        "exhaustive_condition": is_exhaustive,
        "non_empty_condition": non_empty,
        "intersections": pairwise_intersections
    }


def get_stratified_catalog_distribution(quotient_set: Dict[str, List[Dict[str, Any]]], top_n_per_class: int = 1) -> List[Dict[str, Any]]:
    """
    Algorithmic Application in OTT Personalization:
    Mitigates catalog starvation and regional homogenization by sampling
    the highest-rated content from each disjoint equivalence class.
    """
    stratified_feed = []
    for class_key, class_items in quotient_set.items():
        # Sort by popularity and avg_rating
        sorted_items = sorted(
            class_items,
            key=lambda x: (x.get("avg_rating", 0.0), x.get("popularity_score", 0.0)),
            reverse=True
        )
        stratified_feed.extend(sorted_items[:top_n_per_class])
    return stratified_feed


if __name__ == "__main__":
    from database import get_all_movies, seed_database
    seed_database()
    movies_df = get_all_movies()
    movie_records = movies_df.to_dict(orient="records")

    print("[DMGT Engine] Verifying Equivalence Relation Axioms...")
    ref_res = verify_reflexivity(movie_records)
    sym_res = verify_symmetry(movie_records)
    trn_res = verify_transitivity(movie_records)
    print(f" - Reflexivity: {'PASSED' if ref_res['is_satisfied'] else 'FAILED'}")
    print(f" - Symmetry: {'PASSED' if sym_res['is_satisfied'] else 'FAILED'}")
    print(f" - Transitivity: {'PASSED' if trn_res['is_satisfied'] else 'FAILED'}")

    quotient = compute_equivalence_classes(movie_records)
    partition_res = verify_partition_theorem(movie_records, quotient)
    print(f" - Partition Theorem Verified: {partition_res['is_valid_partition']} (Classes: {partition_res['num_classes']})")
