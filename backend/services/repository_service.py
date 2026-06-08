import asyncio
import httpx
from config.settings import Config
from utils.validators import validate_github_url
from middleware.error import APIError
from extract import (
    extract_owner_repo,
    fetch_and_format_repo_info,
    save_to_db_with_dynamic_table,
    fetch_all_pull_requests_async,
    fetch_pull_request_reviews_async,
    fetch_commits_async,
    fetch_developers_async,
    extract_issues_async,
    clean_pull_requests,
    clean_reviews,
    clean_commits,
    clean_issues,
    save_cleaned_pull_requests_to_db,
    save_reviews_to_db,
    save_commits_to_db,
    save_developers_to_db,
    save_issues_to_db
)

class RepositoryService:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def process_repository(self, repo_url, user_id):
        """Process a GitHub repository and extract all relevant data."""
        try:
            # Validate GitHub URL
            repo_url = validate_github_url(repo_url)
            
            # Extract owner and repo name
            owner, repo = extract_owner_repo(repo_url)
            
            # Fetch and save basic repo info
            repo_info = fetch_and_format_repo_info(repo_url)
            repo_id = save_to_db_with_dynamic_table(repo_info, user_id, owner=owner)
            
            if not repo_id:
                raise APIError("Failed to save repository information", 500)

            # Process repository data asynchronously
            async with httpx.AsyncClient() as client:
                # Fetch and process pull requests
                pull_requests = await fetch_all_pull_requests_async(client, owner, repo)
                cleaned_prs = clean_pull_requests(pull_requests)
                save_cleaned_pull_requests_to_db(repo_id, cleaned_prs)

                # Fetch and process reviews
                review_tasks = [
                    fetch_pull_request_reviews_async(client, owner, repo, pr["pr_number"])
                    for pr in cleaned_prs if pr.get("pr_number")
                ]
                all_reviews = await asyncio.gather(*review_tasks)
                for pr, reviews in zip(cleaned_prs, all_reviews):
                    cleaned_reviews = clean_reviews(reviews)
                    save_reviews_to_db(repo_id, pr["pr_number"], cleaned_reviews)

                # Fetch and process commits
                commits = await fetch_commits_async(client, owner, repo)
                cleaned_commits = clean_commits(commits)
                save_commits_to_db(repo_id, cleaned_commits)

                # Fetch and process developers
                developers = await fetch_developers_async(client, owner, repo)
                save_developers_to_db(repo_id, developers)

                # Fetch and process issues
                issues = await extract_issues_async(client, owner, repo)
                cleaned_issues = clean_issues(issues)
                save_issues_to_db(repo_id, cleaned_issues)

            return {
                "message": f"Successfully processed repository {repo_url}",
                "repo_id": repo_id,
                "stats": {
                    "pull_requests": len(cleaned_prs),
                    "commits": len(cleaned_commits),
                    "developers": len(developers),
                    "issues": len(cleaned_issues)
                }
            }

        except Exception as e:
            raise APIError(f"Failed to process repository: {str(e)}", 500) 