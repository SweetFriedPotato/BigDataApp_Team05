-- Implementation: Codex. Run as the pre-provisioned team05 account; no administrative SQL.
USE team05;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE TABLE locations (
 location_id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
 location_code VARCHAR(20) NOT NULL UNIQUE,
 name_en VARCHAR(40) NOT NULL, name_ko VARCHAR(40) NOT NULL,
 requested_latitude DECIMAL(9,6) NOT NULL,
 requested_longitude DECIMAL(10,6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE daily_temperatures (
 location_id TINYINT UNSIGNED NOT NULL,
 weather_date DATE NOT NULL,
 tmean DECIMAL(6,2) NULL, tmax DECIMAL(6,2) NULL, tmin DECIMAL(6,2) NULL,
 PRIMARY KEY (location_id, weather_date),
 KEY idx_weather_date_location (weather_date, location_id),
 CONSTRAINT fk_weather_location FOREIGN KEY (location_id) REFERENCES locations(location_id),
 CONSTRAINT chk_temperature_order CHECK (
  (tmin IS NULL OR tmean IS NULL OR tmin <= tmean) AND
  (tmean IS NULL OR tmax IS NULL OR tmean <= tmax) AND
  (tmin IS NULL OR tmax IS NULL OR tmin <= tmax))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE solar_terms (
 term_date DATE NOT NULL PRIMARY KEY, term_name VARCHAR(20) NOT NULL,
 source_url VARCHAR(1024) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE monthly_food_guides (
 guide_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 month_no TINYINT UNSIGNED NOT NULL, food_name VARCHAR(80) NOT NULL,
 source_url VARCHAR(1024) NOT NULL,
 UNIQUE KEY uq_month_food (month_no, food_name),
 CONSTRAINT chk_food_month CHECK (month_no BETWEEN 1 AND 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE saved_plans (
 plan_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 plan_name VARCHAR(100) NOT NULL, start_date DATE NOT NULL, end_date DATE NOT NULL,
 max_temp_threshold DECIMAL(6,2) NOT NULL, max_temp_range DECIMAL(6,2) NOT NULL,
 memo TEXT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 KEY idx_plan_updated (updated_at, plan_id),
 CONSTRAINT chk_plan_dates CHECK (start_date <= end_date),
 CONSTRAINT chk_plan_range CHECK (max_temp_range >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE plan_locations (
 plan_id BIGINT UNSIGNED NOT NULL, location_id TINYINT UNSIGNED NOT NULL,
 PRIMARY KEY (plan_id, location_id), KEY idx_plan_location (location_id),
 CONSTRAINT fk_plan_parent FOREIGN KEY (plan_id) REFERENCES saved_plans(plan_id) ON DELETE CASCADE,
 CONSTRAINT fk_plan_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
