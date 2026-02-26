--  Scalar Subquery Example
    -- This query retrieves the names of employees whose salary is greater than the average salary of all employees. 
    -- One row with one column subquery example.
    SELECT
        employee_id,
        name,
        salary
    FROM
        employee
    WHERE
        salary > (
            SELECT
                AVG(salary)
            FROM
                employee
        );

    -- This query retrieves all employees whose department_id and job_id match the employee named 'Alice'.
    -- This is an example of a subquery that returns multiple rows and one column.
    SELECT
        *
    FROM
        employees
    WHERE
        (department_id, job_id) = (
            SELECT
                department_id,
                job_id
            FROM
                employees
            WHERE
                name = 'Alice'
        );

-- Multi-row Subquery
    -- This query retrieves the names of departments that have at least one employee.
    -- This is an example of a subquery that returns multiple rows and one column.
    SELECT
        department_name
    FROM
        department
    WHERE
        department_id IN (
            SELECT DISTINCT
                department_id
            FROM
                employee
        );


    -- This query retrieves the names of employees who work in the same department and job as any employee in the promotions table.
    -- This is an example of a subquery that returns multiple rows and multiple columns.

    SELECT
        employee_id,
        name,
        department_id,
        job_id
    FROM
        employees
    WHERE
        (department_id, job_id) IN (
            SELECT
                department_id,
                job_id
            FROM
                promotions
        );


-- Correlated Subquery
    -- This query retrieves the names of employees whose salary is greater than the average salary of their respective department.
    -- This is an example of a correlated subquery.
    SELECT
        employee_id,
        name,
        salary
    FROM
        employee e1
    WHERE
        salary > (
            SELECT
                AVG(salary)
            FROM
                employee e2
            WHERE
                e1.department_id = e2.department_id
        );