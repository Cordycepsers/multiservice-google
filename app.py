# webhook_auth.py
from functools import wraps
from typing import Optional, Dict, Any, Callable
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import Flask, request, jsonify, Response

class CloudRunWebhookAuth:
    def __init__(self, project_number: str, service_id: str, region: str):
        """
        Initialize Cloud Run webhook authentication.
        
        Args:
            project_number: GCP project number
            service_id: Cloud Run service ID
            region: Cloud Run service region
        """
        self.project_number = project_number
        self.service_id = service_id
        self.region = region
        self.audience = f"https://{service_id}-{project_number}-{region}.run.app"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify the Cloud Run authentication token.
        
        Args:
            token: JWT token from the request header
            
        Returns:
            Dict containing the token payload if valid
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Verify the token using Google Auth Library
            payload = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                audience=self.audience
            )

            # Verify the token is from Cloud Run
            if not payload.get('email', '').endswith('.run.app'):
                raise ValueError('Token is not from Cloud Run')

            return payload

        except (ValueError, jwt.InvalidTokenError) as e:
            raise ValueError(f'Token verification failed: {str(e)}')

    def require_auth(self, f: Callable) -> Callable:
        """
        Decorator for Flask routes that require authentication.
        
        Args:
            f: Flask route function to wrap
            
        Returns:
            Wrapped function with authentication check
        """
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Response:
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'Missing or invalid authorization header'
                }), 401

            try:
                token = auth_header.split(' ')[1]
                payload = self.verify_token(token)
                # Add verified payload to request context
                request.auth_payload = payload
                return f(*args, **kwargs)
            
            except ValueError as e:
                return jsonify({
                    'error': str(e)
                }), 401
            
        return decorated_function


# Example usage with Flask
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize authentication
auth = CloudRunWebhookAuth(
    project_number=os.getenv('PROJECT_NUMBER'),
    service_id=os.getenv('SERVICE_ID'),
    region=os.getenv('REGION')
)

@app.route('/webhook', methods=['POST'])
@auth.require_auth
def webhook_handler() -> Response:
    """Handle incoming webhook requests"""
    try:
        payload = request.json
        
        # Access the verified auth payload if needed
        auth_payload = request.auth_payload
        
        # Process webhook data
        process_webhook_data(payload)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        app.logger.error(f'Webhook processing error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

def process_webhook_data(payload: Dict[str, Any]) -> None:
    """
    Process webhook payload.
    
    Args:
        payload: Webhook data to process
    """
    # Implement your webhook processing logic here
    app.logger.info(f'Processing webhook payload: {payload}')

if __name__ == '__main__':
    # Configuration
    app.config.update(
        DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
        SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key')
    )
    
    # Run the application
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
