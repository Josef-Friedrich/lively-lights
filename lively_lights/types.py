"""Validate the input values"""


def _range(value, inner_type):
    value = tuple(value)
    if len(value) != 2:
        raise ValueError('Range can only contain 2 elements.')

    min = inner_type(value[0])
    max = inner_type(value[1])

    if min >= max:
        raise ValueError('max isn’t allowed to be smaller than min.')

    return (min, max)


def _list(value, inner_type):
    value = list(value)
    out = []

    for entry in value:
        out.append(inner_type(entry))

    return out


def brightness(value):
    """Brightness of the light. This is a scale from the minimum brightness the
    light is capable of, 1, to the maximum capable brightness, 254."""
    value = int(value)
    if value < 1 or value > 254:
        raise ValueError('Minimum brightness is 1, to the maximum 254')
    return value


def brightness_range(value):
    return _range(value, brightness)


def hue(value):
    """Hue of the light. This is a wrapping value between 0 and 65535."""
    value = int(value)
    if value < 0 or value > 65535:
        raise ValueError('Hue is a value between 0 and 65535')
    return value


def hue_range(value):
    return _range(value, hue)


def hue_list(value):
    return _list(value, hue)


def light_id(value):
    """Light IDS are integer values starting with 1."""
    value = int(value)
    if value < 1:
        raise ValueError('Light IDS are greater or equal to 1')
    return value


def time(seconds):
    seconds = float(seconds)
    if seconds < 0:
        raise ValueError('Time must be greater or equal than 0')
    return seconds


def time_range(value):
    return _range(value, time)


def transition_time(seconds):
    transition_time = float(seconds) * 10
    transition_time = int(round(transition_time))
    if transition_time < 0 or transition_time > 65535:
        raise ValueError('transition_time is a value between 0 and 65535')
    return transition_time


def saturation(value):
    """Saturation of the light. 254 is the most saturated (colored) and 0 is
    the least saturated (white)."""
    value = int(value)
    if value < 0 or value > 254:
        raise ValueError('Minimum saturation is 0, to the maximum 254')
    return value
