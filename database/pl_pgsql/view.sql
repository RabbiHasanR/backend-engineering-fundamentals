-- These SQL script demonstrates the creation and usage of a view and a materialized view in a database.
-- These SQL script creates a view and materialized view that summarizes sales data by month.
-- It aggregates the total sales amount for each month and provides a simplified view of the data.
-- This is useful for reporting and analysis, allowing users to easily query monthly sales totals without needing to write complex queries each time.

-- View Example
-- create view
CREATE VIEW monthly_sales AS
SELECT 
  DATE_TRUNC('month', sale_date) AS month,
  SUM(amount) AS total
FROM sales
GROUP BY DATE_TRUNC('month', sale_date);

-- run view
SELECT * FROM monthly_sales;


-- Materialized View Example
-- create materialized view
CREATE MATERIALIZED VIEW monthly_sales_mv AS
SELECT 
  DATE_TRUNC('month', sale_date) AS month,
  SUM(amount) AS total
FROM sales
GROUP BY DATE_TRUNC('month', sale_date);

-- run materialized view
SELECT * FROM monthly_sales;

-- refresh materialized view
REFRESH MATERIALIZED VIEW monthly_sales_mv;