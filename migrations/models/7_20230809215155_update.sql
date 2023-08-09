-- upgrade --
ALTER TABLE "users" DROP COLUMN "number_tag";
ALTER TABLE "users" DROP COLUMN "number_nonce";
ALTER TABLE "users" DROP COLUMN "address_salt";
ALTER TABLE "users" DROP COLUMN "address_tag";
ALTER TABLE "users" DROP COLUMN "number_salt";
ALTER TABLE "users" DROP COLUMN "address_nonce";
ALTER TABLE "users" ALTER COLUMN "encrypted_address" TYPE BYTEA USING "encrypted_address"::BYTEA;
ALTER TABLE "users" ALTER COLUMN "encrypted_number" TYPE BYTEA USING "encrypted_number"::BYTEA;
-- downgrade --
ALTER TABLE "users" ADD "number_tag" VARCHAR(200);
ALTER TABLE "users" ADD "number_nonce" VARCHAR(200);
ALTER TABLE "users" ADD "address_salt" VARCHAR(200);
ALTER TABLE "users" ADD "address_tag" VARCHAR(200);
ALTER TABLE "users" ADD "number_salt" VARCHAR(200);
ALTER TABLE "users" ADD "address_nonce" VARCHAR(200);
ALTER TABLE "users" ALTER COLUMN "encrypted_address" TYPE TEXT USING "encrypted_address"::TEXT;
ALTER TABLE "users" ALTER COLUMN "encrypted_number" TYPE TEXT USING "encrypted_number"::TEXT;
