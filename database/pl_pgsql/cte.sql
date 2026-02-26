-- CTE examples
-- Simple CTE
-- This CTE calculates the average salary of employees and selects those with a salary above the average.

with avg_salary as (
      select avg(salary) as avg_sal
      from employees
    )

    select employee_id, name
    from employees
    cross join avg_salary
    where employees.salary > avg_salary.avg_sal;

-- Chained CTEs
-- This example uses chained CTEs to first calculate the average salary per department and 
-- then selects employees from departments with an average salary above a certain threshold.

WITH avg_salaries AS (
  SELECT department_id, AVG(salary) AS avg_salary
  FROM employee
  GROUP BY department_id
),

high_avg_departments AS (
  SELECT department_id
  FROM avg_salaries
  WHERE avg_salary > 60000
)

SELECT e.employee_id, e.name, e.salary, d.department_name
FROM employee e
JOIN high_avg_departments h ON e.department_id = h.department_id
JOIN department d ON e.department_id = d.department_id;

-- Recursive CTE
-- This example Retrieve the full employee hierarchy starting from top-level managers, 
-- including each employee’s level in the organizational structure

WITH RECURSIVE emp_hierarchy AS (
  SELECT employee_id, name, manager_id, 1 AS level
  FROM employee
  WHERE manager_id IS NULL

  UNION ALL

  SELECT e.employee_id, e.name, e.manager_id, eh.level + 1
  FROM employee e
  JOIN emp_hierarchy eh ON e.manager_id = eh.employee_id
)

SELECT *
FROM emp_hierarchy;