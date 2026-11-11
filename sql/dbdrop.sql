-- Team responsibility: Nunnalin Heimvichit (2371001) — Data collection/validation; six-table ERD, normalization, keys/indexes; four SQL files, initialization and dump.
-- WARNING: deletes project tables including all saved plans. Back up first.
USE team05;
DROP TABLE IF EXISTS plan_locations;
DROP TABLE IF EXISTS saved_plans;
DROP TABLE IF EXISTS daily_temperatures;
DROP TABLE IF EXISTS monthly_food_guides;
DROP TABLE IF EXISTS solar_terms;
DROP TABLE IF EXISTS locations;
