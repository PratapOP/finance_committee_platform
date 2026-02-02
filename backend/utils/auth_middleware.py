"""
Authentication Decorators and Middleware for Finance Committee Platform
"""

from functools import wraps
import time
from flask import request, jsonify, session
from flask_login import login_required, current_user
from models import FCMember

def require_role(*roles):
    """
    Decorator to require specific user roles
    Usage: @require_role('admin', 'finance')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            
            if current_user.role not in roles:
                return jsonify({
                    "error": "Access denied. Required roles: " + ", ".join(roles),
                    "required_roles": roles,
                    "current_role": current_user.role
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to require admin access
    Usage: @admin_required
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({
                "error": "Admin access required",
                "current_role": current_user.role
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def api_key_required(f):
    """
    Decorator to require valid API key
    Usage: @api_key_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header or query parameter
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        # In production, validate against database or config
        valid_api_keys = ['finance-committee-2024']  # Move to config
        
        if not api_key or api_key not in valid_api_keys:
            return jsonify({
                "error": "Valid API key required"
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON request body
    Usage: @validate_json(['name', 'email'], ['phone'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "JSON content type required"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is required"}), 400
            
            # Validate required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or str(data[field]).strip() == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        "error": f"Missing required fields: " + ", ".join(missing_fields),
                        "missing_fields": missing_fields
                    }), 400
            
            # Validate optional fields if provided
            if optional_fields and data:
                invalid_fields = []
                for field in optional_fields:
                    if field in data and data[field] is not None and str(data[field]).strip() == '':
                        invalid_fields.append(field)
                
                if invalid_fields:
                    return jsonify({
                        "error": f"Fields cannot be empty: " + ", ".join(invalid_fields),
                        "invalid_fields": invalid_fields
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window_seconds=3600):
    """
    Decorator to implement rate limiting (basic in-memory implementation)
    Usage: @rate_limit(10, 60)  # 10 requests per minute
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (IP address or user ID)
            client_id = request.remote_addr
            if current_user.is_authenticated:
                client_id = f"user_{current_user.id}"
            
            # Simple in-memory rate limiting (in production, use Redis/Memcached)
            if not hasattr(rate_limit, '_requests'):
                rate_limit._requests = {}
            
            now = int(time.time())
            window_start = now - window_seconds
            
            if client_id not in rate_limit._requests:
                rate_limit._requests[client_id] = []
            
            # Remove old requests outside the window
            rate_limit._requests[client_id] = [
                req_time for req_time in rate_limit._requests[client_id] 
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(rate_limit._requests[client_id]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "limit": max_requests,
                    "window": window_seconds,
                    "retry_after": window_seconds - (now - rate_limit._requests[client_id][0])
                }), 429
            
            # Add current request
            rate_limit._requests[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_api_access(f):
    """
    Decorator to log API access
    Usage: @log_api_access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        from datetime import datetime
        
        # Log request details
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'endpoint': request.endpoint,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'user_id': current_user.id if current_user.is_authenticated else None,
            'content_length': request.content_length
        }
        
        logging.info(f"API Access: {log_data}")
        
        return f(*args, **kwargs)
    return decorated_function

def cors_enabled(allowed_origins=None):
    """
    Decorator to enable CORS
    Usage: @cors_enabled(['http://localhost:3000'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response = jsonify({'status': 'ok'})
            else:
                response = f(*args, **kwargs)
            
            # Set CORS headers
            if allowed_origins:
                origin = request.headers.get('Origin')
                if origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            return response
        return decorated_function
    return decorator

# Session management utilities
def set_session_data(key, value):
    """Set session data"""
    session[key] = value
    session.permanent = True

def get_session_data(key, default=None):
    """Get session data"""
    return session.get(key, default)

def clear_session_data(key=None):
    """Clear session data"""
    if key:
        session.pop(key, None)
    else:
        session.clear()

# User context utilities
def get_user_context():
    """Get current user context"""
    if current_user.is_authenticated:
        return {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'role': current_user.role
        }
    return None

def is_admin():
    """Check if current user is admin"""
    return current_user.is_authenticated and current_user.role == 'admin'

def is_finance_member():
    """Check if current user is finance member"""
    return current_user.is_authenticated and current_user.role == 'finance'

def has_permission(permission):
    """Check if current user has specific permission"""
    permissions = {
        'admin': ['admin'],
        'finance': ['admin', 'finance'],
        'read': ['admin', 'finance'],
        'write': ['admin', 'finance'],
        'delete': ['admin']
    }
    
    user_permissions = permissions.get(permission, [])
    return current_user.is_authenticated and current_user.role in user_permissions