-- upgrade --
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(256)  UNIQUE,
    "first_name" VARCHAR(128),
    "last_name" VARCHAR(128),
    "email" VARCHAR(64),
    "address" VARCHAR(150),
    "contact_number" VARCHAR(18),
    "registered_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "rooms" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(12) NOT NULL,
    "number" INT NOT NULL UNIQUE,
    "budget" VARCHAR(12) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_closed" BOOL NOT NULL  DEFAULT False,
    "started_at" TIMESTAMPTZ,
    "closed_at" TIMESTAMPTZ,
    "owner_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "game_results" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "assigned_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "recipient_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
    "room_id" INT NOT NULL REFERENCES "rooms" ("id") ON DELETE CASCADE,
    "sender_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "wishes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "wish" VARCHAR(256) NOT NULL,
    "room_id" INT NOT NULL REFERENCES "rooms" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE,
    CONSTRAINT "uid_wishes_room_id_c60911" UNIQUE ("room_id", "user_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "rooms_users" (
    "rooms_id" INT NOT NULL REFERENCES "rooms" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("user_id") ON DELETE CASCADE
);
