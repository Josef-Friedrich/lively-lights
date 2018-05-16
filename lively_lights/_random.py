import random

shuffle = random.shuffle


def _float_range(min, max, decimal_places=1):
    base = 10 ** decimal_places
    min = min * base
    max = max * base
    return random.randint(min, max) / base


def brightness(min=1, max=254):
    return random.randint(min, max)


def hue(min=0, max=65535):
    return random.randint(min, max)


def time(min, max, is_transition_time=False, decimal_places=1):
    result = _float_range(min, max, decimal_places=1)
    if is_transition_time:
        result = int(round(result * 10))
    return result
