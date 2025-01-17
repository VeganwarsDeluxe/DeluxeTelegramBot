import math


def get_k(rating):
    if rating > 2400:
        return 10
    if 2400 > rating > 1100:
        return 20
    return 40


def outcome(a, b, a_s, b_s):
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
