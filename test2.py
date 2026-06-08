import pymysql
import pandas as pd

db_config = {
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

def main():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM repository")
            repos = cursor.fetchall()
        for repo_id, repo_name in repos:
            df = pd.read_sql(QUERY, connection, params=[repo_id])
            filename = f'developer_metrics_by_repo{repo_id}.csv'
            df.to_csv(filename, index=False)
            print(f'Developer metrics exported to {filename}')
    finally:
        connection.close()

if __name__ == "__main__":
    main()
