import mysql.connector
from mysql.connector import Error
from middleware.error import APIError
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    HOST = "localhost"
    USER = "root"
    PASSWORD = "."
    DATABASE = "."
    PORT = .

    @classmethod
    def get_connection(cls):
        """Get a database connection"""
        try:
            return mysql.connector.connect(
                host=cls.HOST,
                user=cls.USER,
                password=cls.PASSWORD,
                database=cls.DATABASE,
                port=cls.PORT
            )
        except Error as e:
            raise APIError(f"Database connection failed: {str(e)}", 500)

    @classmethod
    def create_database(cls):
        """Create database if it doesn't exist"""
        try:
            conn = mysql.connector.connect(
                host=cls.HOST,
                user=cls.USER,
                password=cls.PASSWORD,
                port=cls.PORT
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {cls.DATABASE}")
            cursor.close()
            conn.close()
            logger.info(f"Database {cls.DATABASE} created or already exists")
        except Error as e:
            logger.error(f"Error creating database: {str(e)}")
            raise APIError("Database creation failed", 500)

    @classmethod
    def get_connection_pool(cls):
        """Get a connection pool"""
        try:
            return mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                host=cls.HOST,
                user=cls.USER,
                password=cls.PASSWORD,
                database=cls.DATABASE,
                port=cls.PORT
            )
        except Error as e:
            logger.error(f"Error creating connection pool: {str(e)}")
            raise APIError("Database connection failed", 500) 