CREATE TABLE IF NOT EXISTS reminders (
	user_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	description TEXT,
	datetime TEXT NOT NULL,
	repeat_key TEXT,
	channel_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS  user_settings (
	user_id INTEGER NOT NULL,
	timezone TEXT
)
