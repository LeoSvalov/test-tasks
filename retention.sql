-- SQL query for retention of 1st,3rd and 7th day
-- PostgreSQL syntax

SELECT t2.month_number AS month_number, 
	   t2.day1/t2.total::FLOAT AS day1_retention, 
	   t2.day3/t2.total::FLOAT AS day3_retention,
	   t2.day7/t2.total::FLOAT AS day7_retention
FROM(
	SELECT
  		t1.month_number AS month_number,
        COUNT(DISTINCT t1.user_id) AS total,
        SUM(case when t1.difference = 1 then 1 else 0 end) AS day1,
        SUM(case when t1.difference = 3 then 1 else 0 end) AS day3,
        SUM(case when t1.difference = 7 then 1 else 0 end) AS day7   
    FROM(
          SELECT u.user_id AS user_id, 
      			 DATE_PART('day', AGE(DATE(cs.created_at),u.installed_at)) AS difference, 
      			 EXTRACT(MONTH FROM u.installed_at) AS month_number 
          FROM "user" AS u -- user is keyword in postgre, that's why it is in ""
          LEFT JOIN client_session AS cs ON u.user_id = cs.user_id 
      	  WHERE u.installed_at >= '01-01-2020' -- starting from january,2020
    ) AS t1
  	GROUP BY month_number -- grouping by month
) AS t2
ORDER BY month_number;

