import pymysql
from middleware.error import APIError
import logging
from config.database import DatabaseConfig
import traceback
from pymysql.cursors import DictCursor
from mysql.connector.cursor import MySQLCursorDict

logger = logging.getLogger(__name__)

class RepositoryModel:
    def __init__(self, db_pool=None):
        self.db_pool = db_pool

    def list_repositories(self, user_id):
        """List all repositories for a user."""
        connection = None
        try:
            logging.info(f"Attempting to list repositories for user_id: {user_id}")
            
            # Get database connection
            try:
                connection = DatabaseConfig.get_connection()
                logging.info("Database connection successful")
            except Exception as conn_err:
                logging.error(f"Database connection error: {str(conn_err)}")
                raise APIError(f"Database connection failed: {str(conn_err)}", 500)
            
            with connection.cursor(cursor_class=MySQLCursorDict) as cursor:
                # First verify the table structure
                cursor.execute("DESCRIBE repository")
                columns = cursor.fetchall()
                logging.info(f"Table structure: {columns}")
                
                # Execute the main query
                query = """
                    SELECT id, name, description, stars, forks, open_issues, language 
                    FROM repository 
                    WHERE user_id = %s 
                    ORDER BY id DESC
                """
                logging.info(f"Executing query for user_id: {user_id}")
                cursor.execute(query, (user_id,))
                
                # Fetch and process results
                repos = cursor.fetchall()
                logging.info(f"Query returned {len(repos)} rows")
                
                # Since we're using DictCursor, we can return the results directly
                return repos

        except pymysql.Error as e:
            error_msg = f"MySQL error: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            raise APIError(error_msg, 500)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            raise APIError(f"Error listing repositories: {str(e)}", 500)
        finally:
            if connection:
                try:
                    connection.close()
                    logging.info("Database connection closed")
                except Exception as e:
                    logging.error(f"Error closing connection: {str(e)}")

    def get_repository(self, repo_id, user_id):
        """Get a specific repository by ID."""
        try:
            with self.db_pool.connection() as conn:
                with conn.cursor(cursor_class=MySQLCursorDict) as cursor:
                    cursor.execute(
                        """
                        SELECT id, name, description, stars, forks, open_issues, language, username
                        FROM repository
                        WHERE id = %s AND user_id = %s
                        """,
                        (repo_id, user_id)
                    )
                    repo = cursor.fetchone()
                    if not repo:
                        raise APIError("Repository not found", 404)
                    return repo

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to get repository: {str(e)}", 500)

    def get_repository_stats(self, repo_id, user_id):
        """Get detailed statistics for a repository."""
        connection = None
        try:
            logging.info(f"Getting repository stats for repo_id: {repo_id}, user_id: {user_id}")
            
            # Get database connection
            connection = DatabaseConfig.get_connection()
            logging.info("Database connection established")
            
            with connection.cursor(DictCursor) as cursor:
                # Get basic repo info
                logging.info("Fetching basic repository info...")
                cursor.execute(
                    """
                    SELECT id, name, description, stars, forks, open_issues, language, username
                    FROM repository
                    WHERE id = %s AND user_id = %s
                    """,
                    (repo_id, user_id)
                )
                repo = cursor.fetchone()
                logging.info(f"Repository info: {repo}")
                
                if not repo:
                    logging.error(f"Repository not found for repo_id: {repo_id}, user_id: {user_id}")
                    raise APIError("Repository not found", 404)

                # Get detailed statistics from DeveloperModel
                logging.info("Fetching detailed statistics from DeveloperModel...")
                from models.developer import DeveloperModel
                stats = DeveloperModel.get_repository_statistics(repo_id)
                logging.info(f"Statistics retrieved: {stats}")

                # Convert any binary commit IDs to hex strings
                if stats and "recent_commits" in stats:
                    for commit in stats["recent_commits"]:
                        if isinstance(commit.get("id"), bytes):
                            commit["id"] = commit["id"].hex()

                return {
                    "repository": repo,
                    "statistics": stats
                }

        except APIError:
            logging.error("API Error occurred")
            raise
        except Exception as e:
            logging.error(f"Error getting repository statistics: {str(e)}")
            logging.error(traceback.format_exc())
            raise APIError(f"Failed to get repository statistics: {str(e)}", 500)
        finally:
            if connection:
                try:
                    connection.close()
                    logging.info("Database connection closed")
                except Exception as e:
                    logging.error(f"Error closing connection: {str(e)}")

    @staticmethod
    def add_repository(user_id, name, description, stars, forks, open_issues, language):
        try:
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO repository (user_id, name, description, stars, forks, open_issues, language) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (user_id, name, description, stars, forks, open_issues, language)
                )
                connection.commit()
                return cursor.lastrowid
        finally:
            if 'connection' in locals() and connection:
                connection.close() 