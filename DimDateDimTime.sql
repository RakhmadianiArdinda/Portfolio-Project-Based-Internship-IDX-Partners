CREATE TABLE DimDate (
    date_key        INT PRIMARY KEY,   -- format YYYYMMDD
    full_date       DATE NOT NULL,
    year            INT NOT NULL,
    quarter         INT NOT NULL,
    month           INT NOT NULL,
    month_name      VARCHAR(20),
    week_of_year    INT,
    day_of_month    INT NOT NULL,
    day_of_week     INT,               -- 1=Senin, 7=Minggu
    day_name        VARCHAR(20),
    is_weekend      BIT DEFAULT 0      -- 0 = false, 1 = true
);

;WITH DateSequence AS (
    SELECT CAST('2024-01-01' AS DATE) AS d
    UNION ALL
    SELECT DATEADD(DAY, 1, d)
    FROM DateSequence
    WHERE d < '2030-12-31'
)
INSERT INTO DimDate (
    date_key, full_date, year, quarter, month, month_name,
    week_of_year, day_of_month, day_of_week, day_name, is_weekend
)
SELECT
    YEAR(d) * 10000 + MONTH(d) * 100 + DAY(d) AS date_key,
    d AS full_date,
    YEAR(d) AS year,
    DATEPART(QUARTER, d) AS quarter,
    MONTH(d) AS month,
    DATENAME(MONTH, d) AS month_name,
    DATEPART(WEEK, d) AS week_of_year,
    DAY(d) AS day_of_month,
    DATEPART(WEEKDAY, d) AS day_of_week,
    DATENAME(WEEKDAY, d) AS day_name,
    CASE WHEN DATEPART(WEEKDAY, d) IN (1,7) THEN 1 ELSE 0 END AS is_weekend
FROM DateSequence
OPTION (MAXRECURSION 0);



CREATE TABLE DimTime (
    time_key        INT PRIMARY KEY,   -- format HHMMSS
    full_time       TIME NOT NULL,
    hour            INT NOT NULL,
    minute          INT NOT NULL,
    second          INT NOT NULL,
    period          VARCHAR(2),        -- AM / PM
    shift           VARCHAR(20)        -- misal Morning, Afternoon, Night
);

;WITH TimeSequence AS (
    SELECT CAST('00:00:00' AS TIME) AS t
    UNION ALL
    SELECT DATEADD(SECOND, 1, t)
    FROM TimeSequence
    WHERE t < '23:59:59'
)
INSERT INTO DimTime (
    time_key, full_time, hour, minute, second, period, shift
)
SELECT
    (DATEPART(HOUR, t) * 10000 +
     DATEPART(MINUTE, t) * 100 +
     DATEPART(SECOND, t)) AS time_key,
    t AS full_time,
    DATEPART(HOUR, t) AS hour,
    DATEPART(MINUTE, t) AS minute,
    DATEPART(SECOND, t) AS second,
    CASE WHEN DATEPART(HOUR, t) < 12 THEN 'AM' ELSE 'PM' END AS period,
    CASE
        WHEN DATEPART(HOUR, t) BETWEEN 6 AND 11 THEN 'Morning'
        WHEN DATEPART(HOUR, t) BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Night'
    END AS shift
FROM TimeSequence
OPTION (MAXRECURSION 0);

select top 1000 * from DimTime
select top 1000 * from DimDate
