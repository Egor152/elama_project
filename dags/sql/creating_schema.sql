CREATE SCHEMA IF NOT EXISTS stg;

CREATE TABLE IF NOT EXISTS stg.adv (
daily_time_spent_on_site float,
age SMALLINT,
area_income float,
daily_internet_usage float,
ad_topic_line VARCHAR,
city VARCHAR,
male SMALLINT,
country VARCHAR,
timestamp timestamp,
clicked_on_ad SMALLINT
);