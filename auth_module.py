from functools import wraps
from typing import Optional, Dict, Any, Callable
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import Flask, request, jsonify, Response

class CloudRunWebhookAuth:
    def __init__(self, project_number: str, service_id: str, region: str):
        self.project_number = project_number
        self.service_id = service_id
        self.region = region
        self.audience = f"https://{service_id}-{project_number}-{region}.run.app"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                audience=self.audience
            )
            if not payload.get('email', '').endswith('.run.app'):
                raise ValueError('Token is not from Cloud Run')
            return payload
        except (ValueError, jwt.InvalidTokenError) as e:
            raise ValueError(f'Token verification failed: {str(e)}')

    def require_auth(self, f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Response:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid authorization header'}), 401
            try:
                token = auth_header.split(' ')[1]
                payload = self.verify_token(token)
                request.auth_payload = payload
                return f(*args, **kwargs)
            except ValueError as e:
                return jsonify({'error': str(e)}), 401
        return decorated_function