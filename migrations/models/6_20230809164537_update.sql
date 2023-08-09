-- upgrade --
ALTER TABLE "users" ADD "address_nonce" VARCHAR(200);
ALTER TABLE "users" ADD "encrypted_address" TEXT;
ALTER TABLE "users" ADD "encrypted_number" TEXT;
ALTER TABLE "users" ADD "address_salt" VARCHAR(200);
ALTER TABLE "users" ADD "address_tag" VARCHAR(200);
ALTER TABLE "users" ADD "number_salt" VARCHAR(200);
ALTER TABLE "users" ADD "number_tag" VARCHAR(200);
ALTER TABLE "users" ADD "number_nonce" VARCHAR(200);
ALTER TABLE "users" DROP COLUMN "address";
ALTER TABLE "users" DROP COLUMN "contact_number";
-- downgrade --
ALTER TABLE "users" ADD "address" VARCHAR(150);
ALTER TABLE "users" ADD "contact_number" VARCHAR(18);
ALTER TABLE "users" DROP COLUMN "address_nonce";
ALTER TABLE "users" DROP COLUMN "encrypted_address";
ALTER TABLE "users" DROP COLUMN "encrypted_number";
ALTER TABLE "users" DROP COLUMN "address_salt";
ALTER TABLE "users" DROP COLUMN "address_tag";
ALTER TABLE "users" DROP COLUMN "number_salt";
ALTER TABLE "users" DROP COLUMN "number_tag";
ALTER TABLE "users" DROP COLUMN "number_nonce";
