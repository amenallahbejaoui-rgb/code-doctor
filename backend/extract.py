import requests
import re
import pymysql
import asyncio
import httpx
import time
from http.client import RemoteDisconnected
from datetime import datetime

github_token = SECRET
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "npwd",
    "database": "ahey"
}

def extract_owner_repo(repo_url):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError("Invalid GitHub URL format. Please enter a valid repository URL.")

def fetch_and_format_repo_info(repo_url):
    owner, repo = extract_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        return {
            "Name": repo_data.get("name", "N/A"),
            "Description": repo_data.get("description", "No description available"),
            "Stars": repo_data.get("stargazers_count", 0),
            "Forks": repo_data.get("forks_count", 0),
            "Open Issues": repo_data.get("open_issues_count", 0),
            "Language": repo_data.get("language", "Unknown")
        }
    else:
        raise Exception(f"GitHub API Error {response.status_code}: {response.text}")

def save_to_db_with_dynamic_table(repo_info, user_id, owner=None):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS repository (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                description TEXT,
                stars INT,
                forks INT,
                open_issues INT,
                language VARCHAR(50),
                user_id INT,
                username VARCHAR(255)  -- New column for repo owner
            );
            """
            cursor.execute(create_table_sql)
            insert_data_sql = """
            INSERT INTO repository (name, description, stars, forks, open_issues, language, user_id, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_data_sql, (
                repo_info["Name"],
                repo_info["Description"],
                repo_info["Stars"],
                repo_info["Forks"],
                repo_info["Open Issues"],
                repo_info["Language"],
                user_id,
                owner  # Store the owner (username)
            ))
            connection.commit()
            repo_id = cursor.lastrowid
            print(f"Repository information saved successfully with ID: {repo_id}")
            return repo_id
    except Exception as e:
        print(f"Error while saving to database: {e}")
        return None
    finally:
        if connection:
            connection.close()


# --- ASYNC GITHUB FETCH HELPERS ---
async def async_fetch(client, url):
    for _ in range(3):
        try:
            resp = await client.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            await asyncio.sleep(1)
        except Exception:
            await asyncio.sleep(1)
    return None

async def fetch_all_pull_requests_async(client, owner, repo, max_pages=10, limit=200):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    all_pull_requests = []
    count = 0
    for page in range(1, max_pages + 1):
        if count >= limit:
            break
        url = f"{base_url}?state=all&per_page=100&page={page}"
        prs = await async_fetch(client, url)
        if not prs:
            break
        for pr in prs:
            if count >= limit:
                break
            all_pull_requests.append({
                "pr_number": pr.get("number"),
                "developer_id": pr.get("user", {}).get("id"),
                "developer": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "pr_closed": pr.get("closed_at"),
                "pr_merged": pr.get("merged_at"),
                "pr_status": pr.get("state"),
                "pr_updated_at": pr.get("updated_at"),
                "pr_title": pr.get("title")
            })
            count += 1
    return all_pull_requests

async def fetch_pull_request_reviews_async(client, owner, repo, pr_number, max_pages=5, limit=200):
    reviews = []
    count = 0
    for page in range(1, max_pages + 1):
        if count >= limit:
            break
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews?page={page}&per_page=100"
        review_data = await async_fetch(client, url)
        if not review_data:
            break
        for review in review_data:
            if count >= limit:
                break
            reviews.append({
                "review_id": review.get("id"),
                "developer": review.get("user", {}).get("login") if review.get("user") else None,
                "reviewer": review.get("user", {}).get("login") if review.get("user") else None,
                "state": review.get("state"),
                "submitted_at": review.get("submitted_at"),
                "review_body": review.get("body")
            })
            count += 1
    return reviews

async def fetch_commit_details_and_pr(client, owner, repo, sha, semaphore):
    async with semaphore:
        commit_details_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/pulls"
        commit_details, pr_data = await asyncio.gather(
            async_fetch(client, commit_details_url),
            async_fetch(client, pr_url)
        )
        pr_number = pr_data[0].get("number") if pr_data and len(pr_data) > 0 else None
        stats = commit_details.get("stats", {}) if commit_details else {}
        author = commit_details.get("author") if commit_details else None
        author_info = commit_details.get("commit", {}).get("author", {}) if commit_details else {}
        developer = author.get("login") if author else "Unknown"
        return {
            "commit_id": sha,
            "developer": developer,
            "commit_date": author_info.get("date"),
            "message": commit_details.get("commit", {}).get("message", "") if commit_details else "",
            "lines_added": stats.get("additions", 0),
            "lines_removed": stats.get("deletions", 0),
            "total_lines_changed": stats.get("total", 0),
            "total_files_changed": len(commit_details.get("files", [])) if commit_details else 0,
            "pr_number": pr_number
        }

async def fetch_commits_async(client, owner, repo, limit=200, concurrency=15):
    commits = []
    count = 0
    page = 1
    semaphore = asyncio.Semaphore(concurrency)
    while count < limit:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}"
        commit_list = await async_fetch(client, url)
        if not commit_list:
            break
        batch = []
        for commit in commit_list:
            if count >= limit:
                break
            sha = commit.get("sha")
            batch.append(fetch_commit_details_and_pr(client, owner, repo, sha, semaphore))
            count += 1
        # Run all detail+PR fetches for this batch in parallel
        batch_results = await asyncio.gather(*batch)
        commits.extend(batch_results)
        page += 1
    return commits

async def fetch_developers_async(client, owner, repo, limit=200):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    developers = []
    page = 1
    count = 0
    while count < limit:
        
        resp = await async_fetch(client, f"{url}?per_page=100&page={page}")
        if not resp:
            break
        for dev in resp:
            if count >= limit:
                break
            developers.append({
                "developer_id": dev["id"],
                "username": dev["login"]
            })
            count += 1
        page += 1
    return developers

async def extract_issues_async(client, owner, repo, limit=200):
    issues = []
    count = 0
    page = 1
    while count < limit:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}"
        issue_list = await async_fetch(client, url)
        if not issue_list:
            break
        for issue in issue_list:
            if count >= limit:
                break
            # Use pull_request field to link to PRs
            pr_number = None
            if "pull_request" in issue:
                pr_number = issue.get("number")
            issues.append({
                "issue_id": issue["id"],
                "developer": issue["user"]["login"] if issue.get("user") else "Unknown",
                "issue_title": issue.get("title", "Unknown"),
                "issue_description": issue.get("body", ""),
                "issue_status": issue.get("state", "Unknown"),
                "issue_created_at": issue.get("created_at"),
                "issue_updated_at": issue.get("updated_at"),
                "issue_closed": issue.get("closed_at"),
                "closed_by": issue.get("closed_by", {}).get("login") if issue.get("closed_by") else None,
                "pr_number": pr_number
            })
            count += 1
        page += 1
    return issues


def clean_pull_requests(pr_list):
    cleaned_prs = []
    seen_pr_numbers = set()  # Ensure no duplicate PRs
    for pr in pr_list:
        if pr.get("pr_number") in seen_pr_numbers:
            continue
        seen_pr_numbers.add(pr.get("pr_number"))

        if "developer" in pr and isinstance(pr["developer"], str):
            pr["developer"] = pr["developer"].strip()

        if "pr_title" in pr and isinstance(pr["pr_title"], str):
            pr["pr_title"] = re.sub(r'[^\w\s]', '', pr["pr_title"])  # Remove special characters
            pr["pr_title"] = re.sub(r'[\U00010000-\U0010ffff]', '', pr["pr_title"])  # Remove emojis

        if "created_at" in pr and pr["created_at"]:
            pr["created_at"] = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%S%z").date().strftime("%Y-%m-%d")

        if "pr_updated_at" in pr and pr["pr_updated_at"]:
            pr["pr_updated_at"] = datetime.strptime(pr["pr_updated_at"], "%Y-%m-%dT%H:%M:%S%z").date().strftime("%Y-%m-%d")

        # Handle merged_at field properly
        if "pr_merged" in pr and pr["pr_merged"]:
            pr["pr_merged"] = datetime.strptime(pr["pr_merged"], "%Y-%m-%dT%H:%M:%S%z").date().strftime("%Y-%m-%d")
        else:
            pr["pr_merged"] = None  # Store None if no data is available

        if "pr_closed" in pr and pr["pr_closed"]:
            pr["pr_closed"] = datetime.strptime(pr["pr_closed"], "%Y-%m-%dT%H:%M:%S%z").date().strftime("%Y-%m-%d")
        else:
            pr["pr_closed"] = None  # Store None if no data is available

        pr["pr_status"] = pr.get("pr_status", "Unknown")

        cleaned_prs.append(pr)
    return cleaned_prs


def save_cleaned_pull_requests_to_db(repo_id, cleaned_pull_requests):
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        with connection.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS pull_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                repository_id INT,
                pr_number INT,
                developer VARCHAR(255),
                created_at DATE,
                pr_closed DATE,
                pr_merged DATE,
                pr_status VARCHAR(50),
                pr_updated_at DATE,
                pr_title TEXT,
                FOREIGN KEY (repository_id) REFERENCES repository(id) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_sql)

            insert_pull_request_sql = """
            INSERT INTO pull_requests (
                repository_id, pr_number, developer, created_at,
                pr_closed, pr_merged, pr_status, pr_updated_at, pr_title
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for pr in cleaned_pull_requests:
                cursor.execute(insert_pull_request_sql, (
                    repo_id,
                    pr["pr_number"],
                    pr["developer"],
                    pr["created_at"],
                    pr["pr_closed"],
                    pr["pr_merged"],
                    pr["pr_status"],
                    pr["pr_updated_at"],
                    pr["pr_title"]
                ))
            connection.commit()

        print(f"Cleaned pull requests successfully stored for repository ID: {repo_id}")

    except Exception as e:
        print(f"Error while saving cleaned pull requests to database: {e}")
    finally:
        if connection:
            connection.close()




def fetch_pull_request_reviews(repo_url, pr_number, retries=3, max_pages=100, limit=200):
    owner, repo = extract_owner_repo(repo_url)
    reviews = []
    page = 1  # Starting page number
    count = 0  # Initialize count

    while page <= max_pages:
        if count >= limit:  # Check if limit is reached
            break
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews?page={page}&per_page=200"
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    review_data = response.json()
                    if not review_data:
                        return reviews  # Exit if no reviews on current page

                    for review in review_data:
                        if count >= limit:  # Check if limit is reached
                            break
                        # Add null check for review object
                        if not review:
                            continue
                        try:
                            reviews.append({
                                "review_id": review.get("id"),
                                "developer": review.get("user", {}).get("login") if review.get("user") else None,
                                "reviewer": review.get("user", {}).get("login") if review.get("user") else None,
                                "state": review.get("state"),
                                "submitted_at": review.get("submitted_at"),
                                "review_body": review.get("body")
                            })
                            count += 1
                        except Exception as e:
                            print(f"Error processing review: {str(e)}")
                            continue
                    page += 1  # Move to the next page on success
                    break  # Exit the retry loop after a successful request
                else:
                    return reviews
            except (requests.exceptions.RequestException, RemoteDisconnected) as e:
                time.sleep(2)
        else:
            break

    return reviews



def clean_reviews(review_list):
    cleaned_reviews = []
    seen_review_ids = set()

    for review in review_list:
        review_id = review.get("review_id")
        if review_id in seen_review_ids:
            continue
        seen_review_ids.add(review_id)

        if "developer" in review and isinstance(review["developer"], str):
            review["developer"] = review["developer"].strip()

        if "reviewer" in review and isinstance(review["reviewer"], str):
            review["reviewer"] = review["reviewer"].strip()

        if "review_body" in review and isinstance(review["review_body"], str):
            review["review_body"] = re.sub(r'[^\w\s]', '', review["review_body"])
            review["review_body"] = re.sub(r'[\U00010000-\U0010ffff]', '', review["review_body"])

        if "submitted_at" in review and review["submitted_at"]:
            try:
                dt = datetime.strptime(review["submitted_at"], "%Y-%m-%dT%H:%M:%SZ")
                review["submitted_at"] = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                review["submitted_at"] = review["submitted_at"]

        review["state"] = review.get("state", "UNKNOWN").upper()

        cleaned_reviews.append(review)

    return cleaned_reviews


def save_reviews_to_db(repo_id, pr_number, cleaned_reviews):
    try:
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )

        with connection.cursor() as cursor:
            # 🔎 Step 1: Get the internal pull_request_id from the DB
            cursor.execute(
                "SELECT id FROM pull_requests WHERE repository_id=%s AND pr_number=%s",
                (repo_id, pr_number)
            )
            result = cursor.fetchone()
            if not result:
                print(f"❌ Pull request #{pr_number} not found in DB. Skipping reviews.")
                return
            pull_request_id = result[0]

            # ✅ Step 2: Create reviews table if not exists
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS pull_request_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pull_request_id INT,
                repository_id INT,
                reviewer VARCHAR(255),
                review_state VARCHAR(50),
                review_body TEXT,
                submitted_at DATETIME,
                FOREIGN KEY (pull_request_id) REFERENCES pull_requests(id) ON DELETE CASCADE,
                FOREIGN KEY (repository_id) REFERENCES repository(id) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_sql)

            # ✅ Step 3: Insert each review using DB pull_request_id
            insert_review_sql = """
            INSERT INTO pull_request_reviews (
                pull_request_id, repository_id, reviewer, review_state, review_body, submitted_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            for review in cleaned_reviews:
                cursor.execute(insert_review_sql, (
                    pull_request_id,  # ✅ Actual DB ID
                    repo_id,
                    review["reviewer"],
                    review["state"],
                    review["review_body"],
                    review["submitted_at"]
                ))
            connection.commit()

        print(f"✅ Stored {len(cleaned_reviews)} reviews for pull request #{pr_number} in repository ID: {repo_id}")

    except Exception as e:
        print(f"❌ Error while saving reviews to database: {e}")

    finally:
        if connection:
            connection.close()






def fetch_commits(repo_url, limit=200):
    owner, repo = extract_owner_repo(repo_url)
    commits = []
    count = 0
    page = 1

    try:
        while count < limit:
            url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                commit_list = response.json()
                if not commit_list:  # No more commits to fetch
                    break
                
                for commit in commit_list:
                    if count >= limit:
                        break
                        
                    try:
                        sha = commit.get("sha")
                        commit_details_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                        
                        # Add retry mechanism with delay
                        for attempt in range(3):
                            try:
                                commit_response = requests.get(commit_details_url, headers=headers, timeout=10)
                                if commit_response.status_code == 200:
                                    commit_details = commit_response.json()
                                    break
                                time.sleep(2)
                            except (requests.exceptions.RequestException, RemoteDisconnected) as e:
                                if attempt == 2:  # Last attempt
                                    print(f"Error processing commit {sha}: {str(e)}")
                                    continue
                                time.sleep(2)
                                continue
                        
                        # Try to get PR information for this commit
                        pr_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/pulls"
                        pr_response = requests.get(pr_url, headers=headers, timeout=10)
                        pr_number = None
                        if pr_response.status_code == 200:
                            pr_data = pr_response.json()
                            if pr_data and len(pr_data) > 0:
                                pr_number = pr_data[0].get("number")
                        
                        author_info = commit.get("commit", {}).get("author", {})
                        stats = commit_details.get("stats", {})
                        author = commit.get("author")
                        developer = author.get("login") if author else "Unknown"
                        
                        commits.append({
                            "commit_id": sha,
                            "developer": developer,
                            "commit_date": author_info.get("date"),
                            "message": commit.get("commit", {}).get("message", ""),
                            "lines_added": stats.get("additions", 0),
                            "lines_removed": stats.get("deletions", 0),
                            "total_lines_changed": stats.get("total", 0),
                            "total_files_changed": len(commit_details.get("files", [])),
                            "pr_number": pr_number  # Add PR number if found
                        })
                        count += 1
                        print(f"Processed commit {count}/{limit}")
                        
                    except Exception as e:
                        print(f"Error processing commit {sha}: {str(e)}")
                        continue
                
                page += 1  # Move to next page
                time.sleep(1)  # Add delay between pages to avoid rate limiting
                
            else:
                raise Exception(f"GitHub API Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"Error fetching commits: {str(e)}")
        
    return commits

def clean_commits(commit_list):
    cleaned_commits = []
    seen_commit_ids = set()

    for commit in commit_list:
        commit_id = commit.get("commit_id")
        if commit_id in seen_commit_ids:
            continue
        seen_commit_ids.add(commit_id)

        if "developer" in commit and isinstance(commit["developer"], str):
            commit["developer"] = commit["developer"].strip()

        if "message" in commit and isinstance(commit["message"], str):
            commit["message"] = re.sub(r'[\U00010000-\U0010ffff]', '', commit["message"])

        if "commit_date" in commit and commit["commit_date"]:
            try:
                dt = datetime.strptime(commit["commit_date"], "%Y-%m-%dT%H:%M:%SZ")
                commit["commit_date"] = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                commit["commit_date"] = commit["commit_date"]

        cleaned_commits.append(commit)

    return cleaned_commits

def save_commits_to_db(repo_id, cleaned_commits):
    try:
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS commmits (
                id BINARY(20) PRIMARY KEY,
                repository_id INT,
                pull_request_id INT,
                developer VARCHAR(255),
                commit_date DATETIME,
                message TEXT,
                lines_added INT,
                lines_removed INT,
                total_lines_changed INT,
                total_files_changed INT,
                FOREIGN KEY (repository_id) REFERENCES repository(id) ON DELETE CASCADE,
                FOREIGN KEY (pull_request_id) REFERENCES pull_requests(id) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_sql)

            get_pr_id_sql = """
            SELECT id FROM pull_requests 
            WHERE repository_id = %s AND pr_number = %s
            """
            
            insert_commit_sql = """
            INSERT INTO commmits (
                id, repository_id, pull_request_id, developer, commit_date, message,
                lines_added, lines_removed, total_lines_changed, total_files_changed
            ) VALUES (UNHEX(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                developer=VALUES(developer),
                commit_date=VALUES(commit_date),
                message=VALUES(message),
                lines_added=VALUES(lines_added),
                lines_removed=VALUES(lines_removed),
                total_lines_changed=VALUES(total_lines_changed),
                total_files_changed=VALUES(total_files_changed)
            """
            
            for commit in cleaned_commits:
                sha = commit["commit_id"]
                pr_number = None
                message = commit.get("message", "")
                pr_match = re.search(r'#(\d+)', message)
                pull_request_id = None
                
                if pr_match:
                    pr_number = int(pr_match.group(1))
                    cursor.execute(get_pr_id_sql, (repo_id, pr_number))
                    result = cursor.fetchone()
                    pull_request_id = result[0] if result else None

                cursor.execute(insert_commit_sql, (
                    sha,
                    repo_id,
                    pull_request_id,
                    commit["developer"],
                    commit["commit_date"],
                    commit["message"],
                    commit["lines_added"],
                    commit["lines_removed"],
                    commit["total_lines_changed"],
                    commit["total_files_changed"]
                ))
            connection.commit()

        print(f"✅ Stored {len(cleaned_commits)} commits for repository ID: {repo_id}")

    except Exception as e:
        print(f"❌ Error while saving commits to database: {e}")

    finally:
        if connection:
            connection.close()







def fetch_developers(repo_url, limit=200):
    owner, repo = extract_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    developers = []
    page = 1
    count = 0  # Initialize count for limiting
    
    try:
        while count < limit:  # Continue until we reach the limit
            response = requests.get(f"{url}?per_page=100&page={page}", headers=headers)
            if response.status_code == 200:
                page_data = response.json()
                if not page_data:
                    break
                    
                for dev in page_data:
                    if count >= limit:  # Check if we've reached the limit
                        break
                    developers.append({
                        "developer_id": dev["id"],
                        "username": dev["login"]
                    })
                    count += 1  # Increment count for each developer added
                page += 1
                time.sleep(0.5)  # Rate limit protection
            else:
                print(f"Failed to fetch developers: {response.status_code}")
                break
    except Exception as e:
        print(f"Error fetching developers: {str(e)}")
        
    print(f"Fetched {count} developers (limit: {limit})")
    return developers

def save_developers_to_db(repo_id, developers):
    try:
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS developers (
                    developer_id INT PRIMARY KEY,  
                    repository_id INT,
                    username VARCHAR(255),
                    FOREIGN KEY (repository_id) REFERENCES repository(id) ON DELETE CASCADE
                )
            """)
            
            insert_sql = """
              INSERT INTO developers (developer_id, repository_id, username)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE username = VALUES(username)
            """
            
            for dev in developers:
                cursor.execute(insert_sql, (
                    dev["developer_id"],  # Use GitHub user ID as primary key
                    repo_id,
                    dev["username"]
                ))
                
            connection.commit()
            print(f"✅ Stored {len(developers)} contributors for repository ID: {repo_id}")
            
    except Exception as e:
        print(f"❌ Error saving contributors: {str(e)}")
    finally:
        if connection:
            connection.close()



def extract_issues(repo_url, limit=200):
    owner, repo = extract_owner_repo(repo_url)
    issues = []
    count = 0
    page = 1

    try:
        while count < limit:
            url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100&page={page}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                issue_list = response.json()
                if not issue_list:
                    break

                for issue in issue_list:
                    if count >= limit:
                        break
                    issues.append({
                        "issue_id": issue["id"],
                        "developer": issue["user"]["login"] if issue.get("user") else "Unknown",
                        "issue_title": issue.get("title", "Unknown"),
                        "issue_description": issue.get("body", ""),
                        "issue_status": issue.get("state", "Unknown"),
                        "issue_created_at": issue.get("created_at"),
                        "issue_updated_at": issue.get("updated_at"),
                        "issue_closed": issue.get("closed_at"),
                        "closed_by": issue.get("closed_by", {}).get("login") if issue.get("closed_by") else None
                    })
                    count += 1
                page += 1
                time.sleep(0.5)
            else:
                break

    except Exception as e:
        print(f"Error fetching issues: {str(e)}")
        
    return issues  
   
def clean_issues(issue_list):
    cleaned_issues = []
    seen_issue_ids = set()

    for issue in issue_list:
        issue_id = issue.get("issue_id")
        if not issue_id or issue_id in seen_issue_ids:
            continue
        seen_issue_ids.add(issue_id)

        # Clean developer field
        if "developer" in issue and isinstance(issue["developer"], str):
            issue["developer"] = issue["developer"].strip()

        # Clean text fields
        for field in ["issue_title", "issue_description"]:
            if field in issue and isinstance(issue[field], str):
                issue[field] = re.sub(r'[^\w\s\-_.,!?]', '', issue[field])
                issue[field] = re.sub(r'[\U00010000-\U0010ffff]', '', issue[field]).strip()

        # Format dates
        for date_field in ["issue_created_at", "issue_updated_at", "issue_closed"]:
            if issue.get(date_field):
                try:
                    dt = datetime.strptime(issue[date_field], "%Y-%m-%dT%H:%M:%SZ")
                    issue[date_field] = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass  # Keep original value if parsing fails

        # Clean closed_by field
        if "closed_by" in issue and isinstance(issue["closed_by"], str):
            issue["closed_by"] = issue["closed_by"].strip()

        cleaned_issues.append(issue)

    return cleaned_issues            
            
def save_issues_to_db(repo_id, cleaned_issues):
    try:
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS issuesss (
                    issue_id BIGINT PRIMARY KEY,
                    repository_id INT,
                    pull_request_id INT,
                    developer VARCHAR(255),
                    issue_title TEXT,
                    issue_description TEXT,
                    issue_status VARCHAR(50),
                    created_at DATETIME,
                    updated_at DATETIME,
                    closed_at DATETIME,
                    closed_by VARCHAR(255),
                    FOREIGN KEY (repository_id) REFERENCES repository(id) ON DELETE CASCADE,
                    FOREIGN KEY (pull_request_id) REFERENCES pull_requests(id) ON DELETE SET NULL
                )
            """)
            
            get_pr_id_sql = """
                SELECT id FROM pull_requests 
                WHERE repository_id = %s AND pr_number = %s
            """
            
            insert_sql = """
                INSERT INTO issuesss (
                    issue_id, repository_id, pull_request_id, developer,
                    issue_title, issue_description, issue_status,
                    created_at, updated_at, closed_at, closed_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    developer=VALUES(developer),
                    issue_title=VALUES(issue_title),
                    issue_description=VALUES(issue_description),
                    issue_status=VALUES(issue_status),
                    created_at=VALUES(created_at),
                    updated_at=VALUES(updated_at),
                    closed_at=VALUES(closed_at),
                    closed_by=VALUES(closed_by)
            """
            
            for issue in cleaned_issues:
                pull_request_id = None
                pr_number = issue.get("pr_number")
                if pr_number:
                    cursor.execute(get_pr_id_sql, (repo_id, pr_number))
                    result = cursor.fetchone()
                    if result:
                        pull_request_id = result[0]
                cursor.execute(insert_sql, (
                    issue["issue_id"],
                    repo_id,
                    pull_request_id,
                    issue.get("developer", ""),
                    issue.get("issue_title", ""),
                    issue.get("issue_description", ""),
                    issue.get("issue_status", "Unknown"),
                    issue.get("issue_created_at"),
                    issue.get("issue_updated_at"),
                    issue.get("issue_closed"),
                    issue.get("closed_by", "")
                ))
            connection.commit()
        print(f"✅ Stored {len(cleaned_issues)} issues for repository ID: {repo_id}")
    except Exception as e:
        print(f"❌ Error saving issues: {str(e)}")
    finally:
        if connection:
            connection.close()

# --- MAIN ASYNC ORCHESTRATOR ---
async def process_github_repository_async(repo_url, user_id):
    repo_id = None
    connection = None
    try:
        print(f"Processing repository: {repo_url}")
        repo_info = fetch_and_format_repo_info(repo_url)
        owner, _ = extract_owner_repo(repo_url)  # Get owner
        repo_id = save_to_db_with_dynamic_table(repo_info, user_id, owner=owner)
        if not repo_id:
            raise Exception("Could not save repository to DB.")
        if connection:
            connection.close()
            connection = None
        print(f"Repository ID: {repo_id}")
        owner, repo = extract_owner_repo(repo_url)
        async with httpx.AsyncClient() as client:
            print("Fetching pull requests...")
            pull_requests = await fetch_all_pull_requests_async(client, owner, repo)
            cleaned_pull_requests = clean_pull_requests(pull_requests)
            save_cleaned_pull_requests_to_db(repo_id, cleaned_pull_requests)
            print(f"Stored {len(cleaned_pull_requests)} pull requests.")
            print("Fetching reviews...")
            review_tasks = [fetch_pull_request_reviews_async(client, owner, repo, pr["pr_number"]) for pr in cleaned_pull_requests if pr.get("pr_number")]
            all_reviews = await asyncio.gather(*review_tasks)
            processed_reviews_count = 0
            for pr, reviews in zip(cleaned_pull_requests, all_reviews):
                pr_number = pr.get("pr_number")
                cleaned_reviews = clean_reviews(reviews)
                save_reviews_to_db(repo_id, pr_number, cleaned_reviews)
                processed_reviews_count += len(cleaned_reviews)
            print(f"Stored {processed_reviews_count} reviews.")
            print("Fetching commits...")
            commits = await fetch_commits_async(client, owner, repo)
            cleaned_commits = clean_commits(commits)
            save_commits_to_db(repo_id, cleaned_commits)
            print(f"Stored {len(cleaned_commits)} commits.")
            print("Fetching developers...")
            developers = await fetch_developers_async(client, owner, repo)
            save_developers_to_db(repo_id, developers)
            print(f"Stored {len(developers)} developers.")
            print("Fetching issues...")
            issues = await extract_issues_async(client, owner, repo)
            cleaned_issues = clean_issues(issues)
            save_issues_to_db(repo_id, cleaned_issues)
            print(f"Stored {len(cleaned_issues)} issues.")
        return {
            "message": f"Successfully processed repository {repo_url}",
            "repo_id": repo_id
        }
    except Exception as e:
        print(f"Error processing repository {repo_url}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to process repository {repo_url}. Error: {str(e)}")
    finally:
        if connection and connection.open:
            connection.close()
            print("Database connection closed in finally block.")


import sys
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <github_repo_url>")
    else:
        repo_url = sys.argv[1]
        asyncio.run(process_github_repository_async(repo_url))