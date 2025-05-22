import os
import requests
from flask import session, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user
import logging

logger = logging.getLogger(__name__)

class ReplitAuth:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.client_id = os.environ.get('REPL_ID')
        self.client_secret = os.environ.get('REPL_TOKEN') 
        self.redirect_uri = self.get_redirect_uri()
        
    def get_redirect_uri(self):
        # Get the domain from environment variables
        replit_domain = os.environ.get('REPLIT_DOMAINS', '').split(',')[0] if os.environ.get('REPLIT_DOMAINS') else 'localhost:5000'
        if 'localhost' in replit_domain:
            return f"http://{replit_domain}/auth/callback"
        else:
            return f"https://{replit_domain}/auth/callback"
    
    def get_auth_url(self):
        """Generate the Replit OAuth authorization URL"""
        auth_url = "https://replit.com/oauth/authorize"
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'user:read'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_url}?{query_string}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        token_url = "https://replit.com/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Get user information from Replit API"""
        api_url = "https://replit.com/graphql"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        query = {
            'query': '''
                query {
                    currentUser {
                        id
                        username
                        displayName
                        firstName
                        lastName
                        image
                        bio
                    }
                }
            '''
        }
        
        try:
            response = requests.post(api_url, json=query, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return None
                
            return data.get('data', {}).get('currentUser')
        except requests.RequestException as e:
            logger.error(f"Error fetching user info: {e}")
            return None

def setup_replit_auth_routes(app, db, User, replit_auth):
    """Setup Replit Auth routes"""
    
    @app.route('/auth/replit')
    def replit_login():
        """Redirect to Replit OAuth"""
        auth_url = replit_auth.get_auth_url()
        return redirect(auth_url)
    
    @app.route('/auth/callback')
    def replit_callback():
        """Handle Replit OAuth callback"""
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.error(f"OAuth error: {error}")
            return redirect(url_for('index') + '?error=auth_failed')
        
        if not code:
            logger.error("No authorization code received")
            return redirect(url_for('index') + '?error=no_code')
        
        # Exchange code for token
        token_data = replit_auth.exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            logger.error("Failed to get access token")
            return redirect(url_for('index') + '?error=token_failed')
        
        # Get user info
        user_info = replit_auth.get_user_info(token_data['access_token'])
        if not user_info:
            logger.error("Failed to get user info")
            return redirect(url_for('index') + '?error=user_info_failed')
        
        # Create or update user
        try:
            user = User.query.filter_by(id=str(user_info['id'])).first()
            
            if not user:
                # Create new user
                user = User(
                    id=str(user_info['id']),
                    username=user_info.get('username', ''),
                    email=None,  # Replit doesn't provide email in basic scope
                    first_name=user_info.get('firstName'),
                    last_name=user_info.get('lastName'),
                    profile_image_url=user_info.get('image')
                )
                db.session.add(user)
            else:
                # Update existing user
                user.username = user_info.get('username', user.username)
                user.first_name = user_info.get('firstName')
                user.last_name = user_info.get('lastName')
                user.profile_image_url = user_info.get('image')
                user.updated_at = db.func.current_timestamp()
            
            db.session.commit()
            
            # Log in the user
            login_user(user)
            
            return redirect(url_for('index') + '?login=success')
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            db.session.rollback()
            return redirect(url_for('index') + '?error=user_create_failed')
    
    @app.route('/auth/logout')
    def auth_logout():
        """Logout user"""
        logout_user()
        session.clear()
        return redirect(url_for('index'))