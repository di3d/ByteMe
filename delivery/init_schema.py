import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "delivery_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5444"),
}

def ensure_database_exists():
    """Ensure the delivery_db database exists"""
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Connect to the default 'postgres' database
            user=DB_PARAMS["user"],
            password=DB_PARAMS["password"],
            host=DB_PARAMS["host"],
            port=DB_PARAMS["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'delivery_db'")
        exists = cursor.fetchone()

        if not exists:
            print("Creating database 'delivery_db'...")
            cursor.execute("CREATE DATABASE delivery_db")
            print("Database 'delivery_db' created successfully")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring database exists: {str(e)}")
        raise

def initialize_tables():
    """Initialize the database tables for delivery service"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # Create the deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id VARCHAR PRIMARY KEY,
                order_id VARCHAR NOT NULL,
                customer_id VARCHAR NOT NULL,
                parts_list JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Delivery tables initialized successfully")
    except Exception as e:
        print(f"Error initializing delivery tables: {str(e)}")
        raise

if __name__ == "__main__":
    ensure_database_exists()
    initialize_tables()