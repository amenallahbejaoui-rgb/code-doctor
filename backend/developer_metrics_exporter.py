import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pandas.io.sql")

import pymysql
import pandas as pd
import os

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "npwd",
    "database": "ahey"
}

# Query to aggregate developer metrics for a specific repository
QUERY = '''
SELECT 
    d.developer_id,
    d.username,
    d.repository_id,
    r.name AS repository_name,
    COUNT(DISTINCT c.id) AS total_commits,
    COALESCE(SUM(c.lines_added), 0) AS total_lines_added,
    COALESCE(SUM(c.lines_removed), 0) AS total_lines_removed,
    COALESCE(SUM(c.total_lines_changed), 0) AS total_lines_changed,
    COALESCE(SUM(c.total_files_changed), 0) AS total_files_changed,
    COUNT(DISTINCT pr.id) AS total_pull_requests,
    COUNT(DISTINCT i.issue_id) AS total_issues,
    COUNT(DISTINCT prr.id) AS total_reviews
FROM developers d
LEFT JOIN commmits c ON d.username = c.developer AND d.repository_id = c.repository_id
LEFT JOIN pull_requests pr ON d.username = pr.developer AND d.repository_id = pr.repository_id
LEFT JOIN issuesss i ON d.username = i.developer AND d.repository_id = i.repository_id
LEFT JOIN pull_request_reviews prr ON pr.id = prr.pull_request_id AND pr.repository_id = prr.repository_id
LEFT JOIN repository r ON d.repository_id = r.id
WHERE d.repository_id = %s
GROUP BY d.developer_id, d.username, d.repository_id, r.name
ORDER BY d.developer_id
'''

# Use backend/repos relative to the project root, not a hardcoded path
REPOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'repos'))

def export_repo_metrics_by_id(repo_id):
    os.makedirs(REPOS_DIR, exist_ok=True)  # Ensure 'repos/' directory exists
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM repository WHERE id = %s", (repo_id,))
            repo = cursor.fetchone()
        if not repo:
            return {'status': 'error', 'message': f'Repository with id {repo_id} not found.'}
        repo_id, repo_name = repo
        filename = os.path.join(REPOS_DIR, f'developer_metrics_by_repo{repo_id}.csv')  # Save in 'backend/repos/'
        if os.path.exists(filename):
            return {'status': 'exists', 'message': f'Metrics already exported for repo {repo_id}.', 'output_file': filename}
        # Use pymysql connection for pandas read_sql
        df = pd.read_sql(QUERY, connection, params=[repo_id])
        df.to_csv(filename, index=False)
        return {
            'status': 'success',
            'repo_id': repo_id,
            'repo_name': repo_name,
            'output_file': filename
        }
    finally:
        connection.close()

if __name__ == "__main__":
    # Replace with an actual repo_id for testing
    result = export_repo_metrics_by_id()
    print(result)
