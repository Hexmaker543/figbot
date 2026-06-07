import re

def get_comma_list(list_string: str):
    if not isinstance(list_string, str): raise ValueError(
        "'list_string' must be a string")
    return [item.strip() for item in list_string.split(',')]

def extract_value(pattern, string):
    match = re.search(pattern, string)
    return int(match.group(1)) if match else 0

