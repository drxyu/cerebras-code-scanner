-- Sample SQL file with performance issues for testing the Cerebras Code Scanner

-- Using SELECT * (inefficient, retrieves unnecessary columns)
SELECT * FROM users WHERE status = 'active';

-- Non-SARGable condition (prevents index usage)
SELECT order_id, customer_id, order_date 
FROM orders 
WHERE YEAR(order_date) = 2023;

-- Missing WHERE clause (full table scan)
SELECT customer_id, name, email FROM customers;

-- Inefficient JOIN (missing index hint)
SELECT o.order_id, c.name, p.product_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Cartesian product (missing JOIN condition)
SELECT e.employee_name, d.department_name
FROM employees e, departments d;

-- Inefficient subquery (could use JOIN instead)
SELECT product_name, price
FROM products
WHERE product_id IN (
    SELECT product_id 
    FROM order_items 
    WHERE quantity > 10
);

-- Using OR instead of UNION (can prevent index usage)
SELECT * FROM sales 
WHERE region = 'North' OR region = 'South';

-- Inefficient sorting without index
SELECT customer_id, order_date, total_amount 
FROM orders 
ORDER BY order_date DESC;

-- Using DISTINCT unnecessarily
SELECT DISTINCT customer_id 
FROM orders 
WHERE order_date > '2023-01-01';

-- Inefficient aggregation without index
SELECT product_category, SUM(sales_amount) as total_sales
FROM sales
GROUP BY product_category;

-- Using a function on an indexed column (prevents index usage)
SELECT * FROM employees 
WHERE UPPER(last_name) = 'SMITH';

-- Inefficient DELETE without proper indexing
DELETE FROM order_items 
WHERE order_date < '2022-01-01';

-- Inefficient UPDATE without WHERE clause
UPDATE products 
SET in_stock = TRUE;

-- Using NOT IN with subquery (inefficient)
SELECT * FROM customers 
WHERE customer_id NOT IN (SELECT customer_id FROM orders);

-- Correlated subquery (inefficient for large tables)
SELECT product_name, 
       (SELECT MAX(order_date) 
        FROM order_items 
        WHERE order_items.product_id = products.product_id) as last_ordered
FROM products;