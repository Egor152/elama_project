--Запрос, который создает схему и таблицу в БД

CREATE SCHEMA IF NOT EXISTS stg;

CREATE TABLE IF NOT EXISTS stg.adv (
daily_time_spent_on_site float,
age SMALLINT,
area_income NUMERIC(7, 2),
daily_internet_usage float,
ad_topic_line VARCHAR(55),
city VARCHAR(30),
male SMALLINT,
country VARCHAR(60),
timestamp timestamp,
clicked_on_ad SMALLINT
);