-- Recursive CTE Examples
-- 1. Show integers from 1 to 10 in a num column without using built-in functions:
-- This example uses a recursive CTE to generate a sequence of numbers from 1 to 10.
-- It starts with the number 1 and recursively adds 1 until it reaches 10.
-- This is useful for generating a series of numbers without relying on built-in functions.
with recursive nums as (
      select 1 as num
      union
      select num + 1 from nums where num < 10
    )

select num
from nums;

-- 2. Employee hierarchy: Get manager-to-employee structure including level (depth):
-- This example retrieves the full employee hierarchy starting from top-level managers,
-- including each employee’s level in the organizational structure.
-- It uses a recursive CTE to traverse the employee table, starting from employees with no manager (top-level).
-- The CTE recursively joins the employee table to itself, incrementing the level for each employee found.
with recursive emp_hiararchy as (
      select employee_id, name, manager_id, 1 as lavel
      from employees
      where manager_id is null

      union all

      select  employee_id, name, manager_id, lavel + 1
      from employees e
      join emp_hiararchy eh on e.manager_id = eh.employee_id 
    )

select * 
from emp_hiararchy
order by level;