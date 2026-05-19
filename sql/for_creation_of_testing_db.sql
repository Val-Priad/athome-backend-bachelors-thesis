DROP DATABASE IF EXISTS estate_v2_test;

CREATE DATABASE estate_v2_test WITH TEMPLATE estate_v2 OWNER postgres;

BEGIN;
TRUNCATE TABLE
    estate_apartments,
    estate_details,
    estate_houses,
    estate_listings,
    estate_locations,
    estate_pricing,
    estate_utilities,
    estates,
    email_verification_tokens,
    password_reset_tokens,
    users
    RESTART IDENTITY CASCADE;
COMMIT;