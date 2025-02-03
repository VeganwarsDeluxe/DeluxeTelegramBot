import math


def get_k(rating):
    if rating > 2400:
        return 10
    if 2400 > rating > 1100:
        return 20
    return 40


def old_outcome(a, b, a_s, b_s):
    """
    a - user A
    b - user B
    a_s - user A score
    b_s - user B score
    """
    EWP_a = 1 / (1 + (10 ** ((b.rating - a.rating) / 400)))
    EWP_b = 1 / (1 + (10 ** ((a.rating - b.rating) / 400)))

    AWP_a = 0.5
    AWP_b = 0.5

    if a_s > b_s:
        AWP_a = 1
        AWP_b = 0
    elif b_s > a_s:
        AWP_a = 0
        AWP_b = 1

    K_a, K_b = get_k(a.rating), get_k(b.rating)

    R_a = a.rating + K_a * (AWP_a - EWP_a)
    R_b = b.rating + K_b * (AWP_b - EWP_b)

    return int(math.ceil(R_a)), int(math.ceil(R_b))


def outcome(a_rating: int, b_rating: int, a_score: int, b_score: int) -> tuple:
    """Calculate new Elo ratings considering score margin (integer-based).

    Args:
        a_rating (int): Player A's rating.
        b_rating (int): Player B's rating.
        a_score (int): Goals/points scored by A.
        b_score (int): Goals/points scored by B.

    Returns:
        tuple: (new_rating_A, new_rating_B) as integers.
    """

    def expected_score(rating, opponent_rating):
        return 1 / (1 + 10 ** ((opponent_rating - rating) / 400))

    # Compute expected scores
    expected_a = expected_score(a_rating, b_rating)
    expected_b = 1 - expected_a  # Complement

    # Determine actual score outcome
    if a_score > b_score:
        actual_a, actual_b = 1, 0  # A wins
    elif a_score < b_score:
        actual_a, actual_b = 0, 1  # B wins
    else:
        actual_a, actual_b = 0.5, 0.5  # Draw

    # Goal difference scaling
    goal_diff = abs(a_score - b_score)
    goal_factor = 1 + math.log2(1 + goal_diff)

    # Get K-factors for both players
    k_a = get_k(a_rating)
    k_b = get_k(b_rating)

    # Adjusted K-factors
    k_a_adjusted = int(k_a * goal_factor)
    k_b_adjusted = int(k_b * goal_factor)

    # Update ratings (integer rounding)
    new_a_rating = round(a_rating + k_a_adjusted * (actual_a - expected_a))
    new_b_rating = round(b_rating + k_b_adjusted * (actual_b - expected_b))

    return new_a_rating, new_b_rating
