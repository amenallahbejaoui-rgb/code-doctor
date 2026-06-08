from flask import Blueprint, request, jsonify, current_app, send_file
from middleware.auth import login_required
from services.repository_service import RepositoryService
from models.repository import RepositoryModel
from middleware.error import APIError
import asyncio
from extract import process_github_repository_async
import logging
import traceback
import os
import pandas as pd

repo = Blueprint('repo', __name__)

@repo.route('/process', methods=['POST'])
@login_required
def process_repository():
    """Process a GitHub repository and extract all relevant data."""
    try:
        data = request.get_json()
        if not data or 'repo_url' not in data:
            raise APIError("Repository URL is required", 400)

        repo_url = data['repo_url']
        user_id = request.user_id  # Set by login_required decorator

        # Run the async process in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_github_repository_async(repo_url, user_id))
        loop.close()
        
        return jsonify({
            'status': 'success',
            'data': result
        })

    except APIError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), e.status_code
    except Exception as e:
        current_app.logger.error(f"Error processing repository: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500

@repo.route('/list', methods=['GET'])
@login_required
def list_repos():
    """List all repositories for the authenticated user."""
    try:
        user_id = request.user_id
        current_app.logger.info(f"Listing repositories for user_id: {user_id}")
        
        # Create model instance without pool
        repo_model = RepositoryModel()
        repos = repo_model.list_repositories(user_id)
        current_app.logger.info(f"Successfully retrieved {len(repos)} repositories")
        return jsonify(repos)
    except APIError as e:
        current_app.logger.error(f"API Error in list_repos: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), e.status_code
    except Exception as e:
        current_app.logger.error(f"Unexpected error in list_repos: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500

@repo.route('/<int:repo_id>', methods=['GET'])
@login_required
def get_repo(repo_id):
    """Get detailed information about a specific repository."""
    try:
        current_app.logger.info(f"Getting repository details for repo_id: {repo_id}")
        user_id = request.user_id
        current_app.logger.info(f"User ID from request: {user_id}")
        
        repo_model = RepositoryModel()
        current_app.logger.info("RepositoryModel instance created")
        
        current_app.logger.info("Calling get_repository_stats...")
        repo_data = repo_model.get_repository_stats(repo_id, user_id)
        current_app.logger.info(f"Repository data retrieved: {repo_data}")
        
        return jsonify({
            'status': 'success',
            'data': repo_data
        })
    except APIError as e:
        current_app.logger.error(f"API Error in get_repo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), e.status_code
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_repo: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500

@repo.route('/csv/<int:repo_id>', methods=['GET'])
@login_required
def get_repo_csv(repo_id):
    """Get the CSV file for a specific repository."""
    try:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repos', f'developer_metrics_by_repo{repo_id}.csv'))
        if not os.path.exists(csv_path):
            return jsonify({'error': f'CSV file not found for repository {repo_id}'}), 404

        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Convert to dictionary format
        data = df.to_dict(orient='records')
        
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        current_app.logger.error(f"Error serving CSV file: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred while serving the CSV file'
        }), 500 