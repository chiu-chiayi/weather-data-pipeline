-- 強制設定連線編碼
SET NAMES utf8mb4;

-- #################################################
-- ## 區塊 0: 建立資料庫 (Database Level)
-- #################################################

DROP DATABASE IF EXISTS weather_data;

CREATE DATABASE IF NOT EXISTS weather_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE weather_data;

-- #################################################
-- ## 區塊 1: 維度表 (Dimension Tables) 建立
-- #################################################

-- 1.1 建立 Dim_Location: 地點維度
CREATE TABLE IF NOT EXISTS dim_location (
    sk INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL UNIQUE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '氣象預報地點的維度表';

-- 1.2 建立 Dim_Date: 日期維度
CREATE TABLE IF NOT EXISTS dim_date (
    id INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    month TINYINT NOT NULL,
    day TINYINT NOT NULL,
    day_of_week TINYINT NOT NULL,
    is_weekend BOOLEAN DEFAULT FALSE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '日期維度表，用於時間層次分析';

-- 1.3 建立 Dim_Time: 時間維度
CREATE TABLE IF NOT EXISTS dim_time (
    id INT PRIMARY KEY,
    full_time TIME NOT NULL UNIQUE,
    hour TINYINT NOT NULL,
    minute TINYINT NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '時間維度表，用於時間粒度分析';

-- #################################################
-- ## 區塊 2: 事實表 (Fact Table) 建立
-- #################################################

-- 2.1 建立 Fact_WeatherForecast: 核心事實表
CREATE TABLE IF NOT EXISTS fact_weather_forecast (
    sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- 外鍵 (FKs) - 連結到各維度
    location_sk INT NOT NULL,
    start_date_id INT NOT NULL,
    start_time_id INT NOT NULL,
    end_date_id INT NOT NULL,
    end_time_id INT NOT NULL,
    wx VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    pop DECIMAL(5, 2),
    mint DECIMAL(5, 2),
    maxt DECIMAL(5, 2),
    ci VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    data_pull_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_location FOREIGN KEY (location_sk) REFERENCES dim_location (sk),
    CONSTRAINT fk_start_date FOREIGN KEY (start_date_id) REFERENCES dim_date (id),
    CONSTRAINT fk_start_time FOREIGN KEY (start_time_id) REFERENCES dim_time (id),
    CONSTRAINT fk_end_date FOREIGN KEY (end_date_id) REFERENCES dim_date (id),
    CONSTRAINT fk_end_time FOREIGN KEY (end_time_id) REFERENCES dim_time (id),
    -- 索引區 --
    INDEX idx_pull_time (data_pull_time),
    INDEX idx_location (location_sk),
    -- 定義複合唯一鍵以避免重複記錄 --
    CONSTRAINT uq_fcst UNIQUE (
        location_sk,
        start_date_id,
        start_time_id,
        end_date_id,
        end_time_id
    )
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '每時段的氣象預報數據事實表';

-- #################################################
-- ## 區塊 3: 初始化基礎資料 (Initial Data)
-- #################################################

-- ============ 預先填入台灣縣市資料 ============
INSERT IGNORE INTO
    dim_location (location_name)
VALUES ('臺北市'),
    ('新北市'),
    ('桃園市'),
    ('臺中市'),
    ('臺南市'),
    ('高雄市'),
    ('基隆市'),
    ('新竹縣'),
    ('新竹市'),
    ('苗栗縣'),
    ('彰化縣'),
    ('南投縣'),
    ('雲林縣'),
    ('嘉義縣'),
    ('嘉義市'),
    ('屏東縣'),
    ('宜蘭縣'),
    ('花蓮縣'),
    ('臺東縣'),
    ('澎湖縣'),
    ('金門縣'),
    ('連江縣');

-- ============ 預先填入 Dim_Date 資料 ============
-- 建立一個存儲過程來填充 Dim_Date 表
DELIMITER //

CREATE PROCEDURE PopulateDimDate()
BEGIN
    DECLARE current_dt DATE DEFAULT '2026-01-01';
    DECLARE end_dt DATE DEFAULT '2026-12-31';
    WHILE current_dt <= end_dt DO
        INSERT IGNORE INTO dim_date (
            id, full_date, year, month, day, day_of_week, is_weekend
        ) VALUES (
            CAST(DATE_FORMAT(current_dt, '%Y%m%d') AS UNSIGNED),
            current_dt,
            YEAR(current_dt),
            MONTH(current_dt),
            DAY(current_dt),
            WEEKDAY(current_dt) + 1,
            IF(WEEKDAY(current_dt) >= 5, TRUE, FALSE)
        );
        SET current_dt = DATE_ADD(current_dt, INTERVAL 1 DAY);
    END WHILE;
END //

CREATE PROCEDURE PopulateDimTime()
BEGIN
    DECLARE h INT DEFAULT 0;
    DECLARE m INT DEFAULT 0;
    WHILE h < 24 DO
        SET m = 0;
        WHILE m < 60 DO
            INSERT IGNORE INTO dim_time (id, full_time, hour, minute)
            VALUES (
                h * 100 + m,
                MAKETIME(h, m, 0),
                h,
                m
            );
            SET m = m + 1;
        END WHILE;
        SET h = h + 1;
    END WHILE;
END //

DELIMITER ;

CALL PopulateDimDate ();
CALL PopulateDimTime ();

DROP PROCEDURE PopulateDimDate;
DROP PROCEDURE PopulateDimTime;