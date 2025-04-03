-- Create databases
CREATE DATABASE customer_db;
CREATE DATABASE order_db;
CREATE DATABASE delivery_db;
CREATE DATABASE recommendation_db;

-- Switch to customer_db and create tables
\c customer_db;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(255) PRIMARY KEY, -- Matches the "customer_id" field in app.py
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL, -- Added "address" field to match app.py
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Switch to order_db and create tables
\c order_db;

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(255) PRIMARY KEY, -- Matches the "order_id" field in app.py
    customer_id VARCHAR(255) NOT NULL, -- Matches the "customer_id" field in app.py
    parts_list JSONB NOT NULL,         -- Matches the "parts_list" field in app.py
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- Matches the "status" field in app.py
    timestamp TIMESTAMP NOT NULL       -- Matches the "timestamp" field in app.py
);

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
\c recommendation_db;

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR(255) PRIMARY KEY, -- Matches the "recommendation_id" field in app.py
    customer_id VARCHAR(255) NOT NULL,         -- Matches the "customer_id" field in app.py
    parts_list JSONB NOT NULL,                 -- Matches the "parts_list" field in app.py
    timestamp TIMESTAMP NOT NULL               -- Matches the "timestamp" field in app.py
);