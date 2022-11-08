-- upgrade --
ALTER TABLE "rooms" RENAME COLUMN "finished_at" TO "closed_at";
ALTER TABLE "rooms" RENAME COLUMN "is_started" TO "is_closed";
-- downgrade --
ALTER TABLE "rooms" RENAME COLUMN "closed_at" TO "finished_at";
ALTER TABLE "rooms" RENAME COLUMN "is_closed" TO "is_started";
