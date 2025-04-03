-- Create databases
CREATE DATABASE customer_db;
CREATE DATABASE order_db;
CREATE DATABASE delivery_db;
CREATE DATABASE recommendation_db;

-- -- Switch to customer_db and create tables
-- \c customer_db;

-- CREATE TABLE IF NOT EXISTS customers (
--     customer_id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Switch to order_db and create tables
-- \c order_db;

-- CREATE TABLE IF NOT EXISTS orders (
--     order_id VARCHAR(255)L PRIMARY KEY,
--     customer_id VARCHAR(255) NOT NULL,
--     total_amount DECIMAL(10, 2) NOT NULL,
--     status VARCHAR(50) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Switch to delivery_db and create tables
\c delivery_db;

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    parts_list JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Switch to recommendation_db and create tables
-- \c recommendation_db;

-- CREATE TABLE IF NOT EXISTS recommendations (
--     recommendation_id SERIAL PRIMARY KEY,
--     customer_id INT NOT NULL,
--     product_id INT NOT NULL,
--     score DECIMAL(5, 2) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );