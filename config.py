COLOR_UNDER_ROLE = "===== FigBot Color Roles ====="

SWATCH_SETTINGS = {
    "font_path": "assets/GohuFont14NerdFontMono-Regular.ttf",
    "font_size": 24,
    "canvas_width": 400,
    "canvas_height": 300,
    "padding": (1, 1, 1, 1),

    # Separates lines of text based off height of text
    # multiplied by this value
    "line_spacing": 1.5,
    "word_spacing": 2 # How many spaces should be printed between each word
}

DATABASE_TEMPLATE ="""
CREATE TABLE IF NOT EXISTS reminders (
    user_id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    datetime TEXT NOT NULL,
    repeat_key TEXT
);
"""
