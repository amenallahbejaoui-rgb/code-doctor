import pymysql
import pandas as pd
import os
from config.database import DatabaseConfig
import logging
import traceback
from middleware.error import APIError
from pymysql.cursors import DictCursor
from datetime import datetime

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "npwd",
    "database": "ahey"
}

class DeveloperModel:
    @staticmethod
    def get_developer_metrics(username, repo_id):
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repos', f'developer_metrics_by_repo{repo_id}.csv'))
        if not os.path.exists(csv_path):
            return None

        try:
            df = pd.read_csv(csv_path)
            if 'username' in df.columns:
                dev_row = df[df['username'] == username]
            elif 'developer_id' in df.columns:
                dev_row = df[df['developer_id'] == username]
            else:
                return None

            if dev_row.empty:
                return None

            return dev_row.iloc[0].to_dict()
        except Exception:
            return None

    @staticmethod
    def get_repository_statistics(repo_id):
        """Get comprehensive repository statistics including developer metrics."""
        connection = None
        try:
            connection = DatabaseConfig.get_connection()
            
            # 1. Velocity (days with commits as percentage)
            velocity_query = '''
            SELECT d.username, COUNT(DISTINCT DATE(c.commit_date)) AS days_with_commits
            FROM developers d
            LEFT JOIN commmits c ON d.username = c.developer AND d.repository_id = c.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            velocity_df = pd.read_sql(velocity_query, connection, params=[repo_id])
            
            # Get total days in repo history
            with connection.cursor() as cursor:
                cursor.execute("SELECT MIN(commit_date), MAX(commit_date) FROM commmits WHERE repository_id = %s", (repo_id,))
                min_date, max_date = cursor.fetchone()
                
            if min_date and max_date:
                total_days = (max_date - min_date).days + 1
                velocity_df['days_with_commits_pct'] = (velocity_df['days_with_commits'] / total_days * 100).round(2)
            else:
                velocity_df['days_with_commits_pct'] = 0
                
            velocity = velocity_df[['username', 'days_with_commits_pct']].to_dict(orient='records')

            # 2. Issues Resolved
            issues_query = '''
            SELECT d.username, SUM(CASE WHEN i.issue_status = 'closed' THEN 1 ELSE 0 END) AS issues_resolved
            FROM developers d
            LEFT JOIN issuesss i ON d.username = i.developer AND d.repository_id = i.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            issues_df = pd.read_sql(issues_query, connection, params=[repo_id])
            issues_resolved = issues_df.fillna(0).to_dict(orient='records')

            # 3. PR Cycle Time
            pr_cycle_query = '''
            SELECT d.username, AVG(TIMESTAMPDIFF(SECOND, pr.created_at, pr.pr_merged)) AS avg_pr_cycle_time_sec
            FROM developers d
            LEFT JOIN pull_requests pr ON d.username = pr.developer AND d.repository_id = pr.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            pr_cycle_df = pd.read_sql(pr_cycle_query, connection, params=[repo_id])
            pr_cycle_df['avg_pr_cycle_time'] = pr_cycle_df['avg_pr_cycle_time_sec'].apply(lambda x: str(pd.to_timedelta(x, unit='s')) if pd.notnull(x) else None)
            pr_cycle_time = pr_cycle_df[['username', 'avg_pr_cycle_time']].to_dict(orient='records')

            # 4. PR Reviews
            pr_reviews_query = '''
            SELECT d.username, COUNT(DISTINCT prr.id) AS total_reviews
            FROM developers d
            LEFT JOIN pull_requests pr ON d.username = pr.developer AND d.repository_id = pr.repository_id
            LEFT JOIN pull_request_reviews prr ON pr.id = prr.pull_request_id AND pr.repository_id = prr.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            pr_reviews_df = pd.read_sql(pr_reviews_query, connection, params=[repo_id])
            pr_reviews = pr_reviews_df.fillna(0).to_dict(orient='records')

            # 5. PRs Merged
            prs_merged_query = '''
            SELECT d.username, SUM(CASE WHEN pr.pr_merged IS NOT NULL THEN 1 ELSE 0 END) AS prs_merged
            FROM developers d
            LEFT JOIN pull_requests pr ON d.username = pr.developer AND d.repository_id = pr.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            prs_merged_df = pd.read_sql(prs_merged_query, connection, params=[repo_id])
            prs_merged = prs_merged_df.fillna(0).to_dict(orient='records')

            # 6. PR Size
            pr_size_query = '''
            SELECT d.username, AVG(c.total_lines_changed) AS avg_pr_size
            FROM developers d
            LEFT JOIN commmits c ON d.username = c.developer AND d.repository_id = c.repository_id
            WHERE d.repository_id = %s
            GROUP BY d.username
            '''
            pr_size_df = pd.read_sql(pr_size_query, connection, params=[repo_id])
            pr_size_df['avg_pr_size'] = pr_size_df['avg_pr_size'].apply(lambda v: round(v) if pd.notnull(v) else 0)
            pr_size = pr_size_df[['username', 'avg_pr_size']].to_dict(orient='records')

            # 7. Most Recent Commits
            commits_query = '''
            SELECT c.id, c.message, c.developer, c.commit_date
            FROM commmits c
            WHERE c.repository_id = %s
            ORDER BY c.commit_date DESC
            LIMIT 20
            '''
            commits_df = pd.read_sql(commits_query, connection, params=[repo_id])
            recent_commits = commits_df.to_dict(orient='records')

            # 8. Most Recent Reviews Submitted
            reviews_query = '''
            SELECT prr.id, prr.reviewer, prr.submitted_at, prr.review_state, prr.review_body, pr.pr_title AS pr_title
            FROM pull_request_reviews prr
            LEFT JOIN pull_requests pr ON prr.pull_request_id = pr.id AND prr.repository_id = pr.repository_id
            WHERE prr.repository_id = %s
            ORDER BY prr.submitted_at DESC
            LIMIT 20
            '''
            reviews_df = pd.read_sql(reviews_query, connection, params=[repo_id])
            recent_reviews = reviews_df.to_dict(orient='records')

            # Ensure all values are JSON serializable (convert bytes to str if needed)
            def decode_bytes(obj):
                if isinstance(obj, dict):
                    return {k: decode_bytes(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decode_bytes(i) for i in obj]
                elif isinstance(obj, bytes):
                    return obj.decode('utf-8', errors='replace')
                else:
                    return obj
            recent_commits = decode_bytes(recent_commits)
            recent_reviews = decode_bytes(recent_reviews)

            return {
                'velocity': velocity,
                'issues_resolved': issues_resolved,
                'pr_cycle_time': pr_cycle_time,
                'pr_reviews': pr_reviews,
                'prs_merged': prs_merged,
                'pr_size': pr_size,
                'recent_commits': recent_commits,
                'recent_reviews': recent_reviews
            }
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