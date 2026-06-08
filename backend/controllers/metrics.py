from flask import Blueprint, request, jsonify
from models.developer import DeveloperModel
from middleware.auth import login_required
import developer_metrics_exporter
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
import time
import traceback
from flask import current_app

metrics = Blueprint('metrics', __name__)

@metrics.route('/export_developer_metrics', methods=['POST'])
@login_required
def export_developer_metrics():
    data = request.get_json()
    repo_id = data.get('repo_id')
    if not repo_id:
        return jsonify({'status': 'error', 'message': 'repo_id is required'}), 400
    try:
        result = developer_metrics_exporter.export_repo_metrics_by_id(repo_id)
        if result.get('status') == 'success':
            msg = f"CSV created: {result.get('output_file')}"
        elif result.get('status') == 'exists':
            msg = f"CSV already exists: {result.get('output_file')}"
        else:
            msg = result.get('message', 'Unknown error')
        return jsonify({**result, 'debug': msg})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@metrics.route('/developer_analytics/<username>/<int:repo_id>', methods=['GET'])
@login_required
def developer_analytics(username, repo_id):
    metrics = DeveloperModel.get_developer_metrics(username, repo_id)
    if metrics:
        return jsonify(metrics)
    return jsonify({'error': f'Developer {username} not found in repo {repo_id}'}), 404

@metrics.route('/repo_statistics/<int:repo_id>', methods=['GET'])
@login_required
def repo_statistics(repo_id):
    try:
        stats = DeveloperModel.get_repository_statistics(repo_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrics.route('/clustering/<int:repo_id>', methods=['GET'])
@login_required
def clustering(repo_id):
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repos', f'developer_metrics_by_repo{repo_id}.csv'))
    
    # Wait for CSV file to be available (with timeout)
    max_attempts = 5
    attempt = 0
    while not os.path.exists(csv_path) and attempt < max_attempts:
        time.sleep(1)  # Wait 1 second between attempts
        attempt += 1
    
    if not os.path.exists(csv_path):
        return jsonify({'error': f'CSV file not found after waiting. Please ensure metrics are exported first.'}), 404

    try:
        df = pd.read_csv(csv_path)
        current_app.logger.info(f"CSV file loaded with {len(df)} rows")
        
        if df.empty:
            return jsonify({'error': 'CSV file is empty. No developer data found.'}), 400

        required_columns = ['username', 'total_commits', 'total_lines_added', 'total_lines_removed', 'total_pull_requests', 'total_reviews']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'error': 'Missing required columns in CSV file',
                'missing_columns': missing_columns,
                'available_columns': list(df.columns)
            }), 400

        df = df.fillna(0)

        # Normalize metrics
        def normalize_metric(x):
            x = x + 1
            x_log = np.log(x)
            x_min = x_log.min()
            x_max = x_log.max()
            if x_max == x_min:
                return np.ones_like(x)
            return (x_log - x_min) / (x_max - x_min)

        # Calculate code and review scores
        code_score = (
            0.4 * normalize_metric(df['total_commits']) +
            0.2 * normalize_metric(df['total_lines_added']) +
            0.1 * normalize_metric(df['total_lines_removed'])
        ) * 70

        review_score = (
            0.15 * normalize_metric(df['total_pull_requests']) +
            0.15 * normalize_metric(df['total_reviews'])
        ) * 30

        df['code_score'] = code_score
        df['review_score'] = review_score
        df['total_score'] = df['code_score'] + df['review_score']

        if df['total_score'].max() == 0:
            return jsonify({
                'error': 'No developer activity found',
                'details': {
                    'developers': df['username'].tolist(),
                    'raw_metrics': df[['username', 'total_commits', 'total_lines_added', 'total_lines_removed', 'total_pull_requests', 'total_reviews']].to_dict(orient='records')
                }
            }), 400

        df = df[df['total_score'] > 0].copy()
        if df.empty:
            return jsonify({
                'error': 'No developers with activity found',
                'details': {
                    'developers': df['username'].tolist(),
                    'raw_metrics': df[['username', 'total_commits', 'total_lines_added', 'total_lines_removed', 'total_pull_requests', 'total_reviews']].to_dict(orient='records')
                }
            }), 400

        # --- Improved clustering logic ---
        # Use total_score only for clustering and sort clusters by mean score
        if len(df) == 1:
            df['cluster'] = 1
        else:
            X = df[['total_score']].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            n_clusters = min(3, len(df))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            df['cluster'] = kmeans.fit_predict(X_scaled)

            # Sort clusters by mean total_score: 0=unactive, 1=normal, 2=active
            cluster_score_means = df.groupby('cluster')['total_score'].mean().sort_values()
            cluster_mapping = {old: new for new, old in enumerate(cluster_score_means.index)}
            df['cluster'] = df['cluster'].map(cluster_mapping)

        result = df[['username', 'cluster', 'code_score', 'review_score', 'total_score']].copy()
        result['code_score'] = result['code_score'].round(2)
        result['review_score'] = result['review_score'].round(2)
        result['total_score'] = result['total_score'].round(2)

        return jsonify({
            'clusters': result.to_dict(orient='records'),
            'message': 'Clustering completed successfully'
        })
    except Exception as e:
        return jsonify({
            'error': 'Error during clustering',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500