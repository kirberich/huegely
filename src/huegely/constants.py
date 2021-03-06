# Maps huegely attribute names to hue API naming scheme
HUEGELY_TO_HUE_MAPPING = {
    # huegely_name: hue_name,
    'brightness': 'bri',
    'saturation': 'sat',
    'temperature': 'ct',
    'is_reachable': 'reachable',
    'coordinates': 'xy',
    'color_mode': 'colormode',
    'transition_time': 'transitiontime',
    'last_updated': 'lastupdated',
}

# Maps hue attribute names to huegely ones (reverse mapping of the above)
HUE_TO_HUEGELY_MAPPING = {v: k for k, v in HUEGELY_TO_HUE_MAPPING.items()}
