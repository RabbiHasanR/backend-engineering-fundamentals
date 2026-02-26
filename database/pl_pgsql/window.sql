
-- 1. RANK()
-- Used to assign rankings within groups. If two values tie, they get the same rank — and the next rank skips.
-- Scenario: Find employee salary rank within each department (with gaps for ties)
SELECT employee_id, department, salary,
       RANK() OVER(PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;

-- 2. DENSE_RANK()
-- Like RANK(), but no gaps when values tie.
-- Scenario: Rank employees by salary within departments, no gaps for ties
SELECT employee_id, department, salary,
       DENSE_RANK() OVER(PARTITION BY department ORDER BY salary DESC) AS dept_dense_rank
FROM employees;

-- 3. ROW_NUMBER()
-- Gives a unique number to every row in a group, even if values are the same.
-- Scenario: Get the most recent sale for each customer
SELECT *
FROM (
  SELECT customer_id, sale_date, amount,
         ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY sale_date DESC) AS rn
  FROM sales
) t
WHERE rn = 1;

-- 4. SUM(), AVG(), MAX(), MIN()
-- These aggregate functions can be used in a window to add up or analyze rows inside each group, but still display each row’s individual data.
-- Scenario: Show employee salary along with total department salary
SELECT employee_id, department, salary,
       SUM(salary) OVER(PARTITION BY department) AS dept_total_salary,
       AVG(salary) OVER(PARTITION BY department) AS dept_avg_salary,
       MAX(salary) OVER(PARTITION BY department) AS dept_max_salary,
       MIN(salary) OVER(PARTITION BY department) AS dept_min_salary
FROM employees;

-- 5. COUNT()
-- Counts the number of rows in each partition.
-- Scenario: Show number of employees per department next to each employee
SELECT employee_id, department,
       COUNT(*) OVER(PARTITION BY department) AS employee_count
FROM employees;

-- 6. LAG()
-- Lets you access the value from the previous row in a partition.
-- Scenario: Compare current price to previous month’s price for each product
SELECT product_id, price_date, price,
       LAG(price, 1, 0) OVER(PARTITION BY product_id ORDER BY price_date) AS previous_price
FROM product_prices;

-- 7. LEAD()
-- Opposite of LAG() — it accesses the value from the next row.
-- Scenario: Show what a product’s price will be next month
SELECT product_id, price_date, price,
       LEAD(price, 1, NULL) OVER(PARTITION BY product_id ORDER BY price_date) AS next_price
FROM product_prices;