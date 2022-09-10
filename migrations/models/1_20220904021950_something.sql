-- upgrade --
ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(256) USING "username"::VARCHAR(256);
ALTER TABLE "users" ALTER COLUMN "last_name" TYPE VARCHAR(128) USING "last_name"::VARCHAR(128);
ALTER TABLE "users" ALTER COLUMN "first_name" TYPE VARCHAR(128) USING "first_name"::VARCHAR(128);
ALTER TABLE "users" ALTER COLUMN "contact_number" TYPE VARCHAR(18) USING "contact_number"::VARCHAR(18);
CREATE UNIQUE INDEX "uid_users_usernam_266d85" ON "users" ("username");
-- downgrade --
DROP INDEX "idx_users_usernam_266d85";
ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(64) USING "username"::VARCHAR(64);
ALTER TABLE "users" ALTER COLUMN "last_name" TYPE VARCHAR(64) USING "last_name"::VARCHAR(64);
ALTER TABLE "users" ALTER COLUMN "first_name" TYPE VARCHAR(64) USING "first_name"::VARCHAR(64);
ALTER TABLE "users" ALTER COLUMN "contact_number" TYPE VARCHAR(12) USING "contact_number"::VARCHAR(12);
