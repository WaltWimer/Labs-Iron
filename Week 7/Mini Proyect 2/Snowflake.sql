-- 1. Setup Context
CREATE DATABASE IF NOT EXISTS brewbeats_db;
USE DATABASE brewbeats_db;
CREATE SCHEMA IF NOT EXISTS raw_data;
USE SCHEMA raw_data;

-- 2. Create target table for coffee_sales
CREATE OR REPLACE TABLE coffee_sales (
    date DATE,
    datetime TIMESTAMP,
    cash_type STRING,
    card STRING,
    money FLOAT,
    coffee_name STRING
);

-- 3. Create target table for Spotify_data
CREATE OR REPLACE TABLE spotify_table (
    acousticness FLOAT,
    danceability FLOAT,
    duration_ms INT,
    energy FLOAT,
    instrumentalness FLOAT,
    key INT,
    liveness FLOAT,
    loudness FLOAT,
    mode INT,
    speechiness FLOAT,
    tempo FLOAT,
    time_signature INT,
    valence FLOAT,
    target INT,
    song_title STRING,
    artist STRING
);


-- Q1 & Q3: Create a stage with a specific file format
CREATE OR REPLACE FILE FORMAT csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';

CREATE OR REPLACE STAGE brewbeats_stage
    FILE_FORMAT = csv_format; 





-- Q1. Load coffee_sales.csv into a Snowflake table
COPY INTO coffee_sales 
FROM '@brewbeats_stage/coffee_sales.csv';

-- Q2. Write a query to find the top 3 coffee types by revenue.
SELECT coffee_name, SUM(money) AS total_revenue 
FROM coffee_sales 
GROUP BY coffee_name 
ORDER BY total_revenue DESC 
LIMIT 3;

-- Q3. Load Spotify data into a Snowflake table (Ignorando la columna extra)
COPY INTO spotify_table 
FROM (
    SELECT $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
    FROM '@brewbeats_stage/Spotify data.csv'
)
FILE_FORMAT = csv_format;

-- Q4. Write a query to find the top 3 songs by Drake.
SELECT song_title, artist 
FROM spotify_table 
WHERE artist = 'Drake' 
ORDER BY energy DESC 
LIMIT 3;

-- tests

SELECT song_title, artist 
FROM spotify_table 
LIMIT 10;