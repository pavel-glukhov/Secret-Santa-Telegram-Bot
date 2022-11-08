-- upgrade --
ALTER TABLE "game_results" ALTER COLUMN "assigned_at" SET NOT NULL;
ALTER TABLE "game_results" ALTER COLUMN "assigned_at" TYPE TIMESTAMPTZ USING "assigned_at"::TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "game_results" ALTER COLUMN "assigned_at" DROP NOT NULL;
ALTER TABLE "game_results" ALTER COLUMN "assigned_at" TYPE TIMESTAMPTZ USING "assigned_at"::TIMESTAMPTZ;
