"""Validate the input values"""


def brightness(value):
    """Brightness of the light. This is a scale from the minimum brightness the
    light is capable of, 1, to the maximum capable brightness, 254."""
    value = int(value)
    if value < 1 or value > 254:
        raise ValueError('Minimum brightness is 1, to the maximum 254')
    return value


def hue(value):
    """Hue of the light. This is a wrapping value between 0 and 65535."""
    value = int(value)
    if value < 0 or value > 65535:
        raise ValueError('Hue is a value between 0 and 65535')
    return value


def saturation(value):
    """Saturation of the light. 254 is the most saturated (colored) and 0 is
    the least saturated (white)."""
    value = int(value)
    if value < 0 or value > 254:
        raise ValueError('Minimum saturation is 0, to the maximum 254')
    return value
