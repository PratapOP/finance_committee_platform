from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from utils.auth_middleware import admin_required, log_api_access
import os
from datetime import datetime

settings_bp = Blueprint("settings", __name__)

# In-memory settings storage (in production, use database or config files)
app_settings = {
    "allow_registration": True,
    "default_role": "finance",
    "session_timeout": 60,
    "maintenance_mode": False,
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes
    "require_email_verification": False,
    "allow_password_reset": True,
    "api_rate_limit": 100,
    "api_rate_window": 3600  # 1 hour
}

@settings_bp.route("/", methods=["GET"])
@login_required
@admin_required
@log_api_access
def get_settings():
    """Get all system settings"""
    try:
        return jsonify({
            "settings": app_settings,
            "last_updated": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get settings: {str(e)}"}), 500

@settings_bp.route("/", methods=["PUT"])
@login_required
@admin_required
@log_api_access
def update_settings():
    """Update system settings"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Update allowed settings
        allowed_settings = [
            "allow_registration",
            "default_role", 
            "session_timeout",
            "maintenance_mode",
            "max_login_attempts",
            "lockout_duration",
            "require_email_verification",
            "allow_password_reset",
            "api_rate_limit",
            "api_rate_window"
        ]
        
        updated_settings = {}
        for key, value in data.items():
            if key in allowed_settings:
                # Validate specific settings
                if key == "default_role" and value not in ["admin", "finance"]:
                    return jsonify({"error": "Default role must be 'admin' or 'finance'"}), 400
                
                if key in ["session_timeout", "max_login_attempts", "lockout_duration", "api_rate_limit", "api_rate_window"]:
                    try:
                        value = int(value)
                        if value < 0:
                            return jsonify({"error": f"{key} must be a positive integer"}), 400
                    except (ValueError, TypeError):
                        return jsonify({"error": f"{key} must be a valid integer"}), 400
                
                if key in ["allow_registration", "maintenance_mode", "require_email_verification", "allow_password_reset"]:
                    if not isinstance(value, bool):
                        return jsonify({"error": f"{key} must be a boolean"}), 400
                
                app_settings[key] = value
                updated_settings[key] = value
        
        return jsonify({
            "message": "Settings updated successfully",
            "updated_settings": updated_settings,
            "all_settings": app_settings,
            "updated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 500

@settings_bp.route("/backup", methods=["GET"])
@login_required
@admin_required
@log_api_access
def backup_settings():
    """Get settings backup as JSON"""
    try:
        backup_data = {
            "settings": app_settings,
            "backup_info": {
                "created_at": datetime.utcnow().isoformat(),
                "created_by": current_user.name,
                "version": "1.0"
            }
        }
        
        return jsonify(backup_data)
    except Exception as e:
        return jsonify({"error": f"Failed to create backup: {str(e)}"}), 500

@settings_bp.route("/restore", methods=["POST"])
@login_required
@admin_required
@log_api_access
def restore_settings():
    """Restore settings from backup"""
    try:
        data = request.json
        
        if not data or "settings" not in data:
            return jsonify({"error": "Backup data is required"}), 400
        
        # Validate backup structure
        backup_settings = data["settings"]
        if not isinstance(backup_settings, dict):
            return jsonify({"error": "Invalid backup format"}), 400
        
        # Restore only valid settings
        valid_keys = set(app_settings.keys())
        for key, value in backup_settings.items():
            if key in valid_keys:
                app_settings[key] = value
        
        return jsonify({
            "message": "Settings restored successfully",
            "restored_settings": len([k for k in backup_settings.keys() if k in valid_keys]),
            "current_settings": app_settings,
            "restored_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to restore settings: {str(e)}"}), 500

@settings_bp.route("/reset", methods=["POST"])
@login_required
@admin_required
@log_api_access
def reset_settings():
    """Reset settings to default values"""
    try:
        # Default settings
        default_settings = {
            "allow_registration": True,
            "default_role": "finance",
            "session_timeout": 60,
            "maintenance_mode": False,
            "max_login_attempts": 5,
            "lockout_duration": 900,
            "require_email_verification": False,
            "allow_password_reset": True,
            "api_rate_limit": 100,
            "api_rate_window": 3600
        }
        
        app_settings.update(default_settings)
        
        return jsonify({
            "message": "Settings reset to defaults successfully",
            "default_settings": default_settings,
            "reset_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to reset settings: {str(e)}"}), 500

@settings_bp.route("/system-info", methods=["GET"])
@login_required
@admin_required
@log_api_access
def get_system_info():
    """Get system information and statistics"""
    try:
        from models import FCMember, Sponsor, Event, Sponsorship
        
        # Get database statistics
        user_count = FCMember.query.count()
        active_user_count = FCMember.query.filter_by(is_active=True).count()
        admin_count = FCMember.query.filter_by(role='admin', is_active=True).count()
        
        sponsor_count = Sponsor.query.count()
        event_count = Event.query.count()
        sponsorship_count = Sponsorship.query.count()
        
        # Get system info
        system_info = {
            "database": {
                "total_users": user_count,
                "active_users": active_user_count,
                "admin_users": admin_count,
                "total_sponsors": sponsor_count,
                "total_events": event_count,
                "total_sponsorships": sponsorship_count
            },
            "application": {
                "version": "1.0.0",
                "environment": os.getenv("FLASK_ENV", "development"),
                "debug_mode": os.getenv("FLASK_DEBUG", "False") == "True"
            },
            "security": {
                "password_min_length": 8,
                "session_timeout_minutes": app_settings.get("session_timeout", 60),
                "max_login_attempts": app_settings.get("max_login_attempts", 5),
                "lockout_duration_minutes": app_settings.get("lockout_duration", 900) // 60
            },
            "current_settings": app_settings,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({"error": f"Failed to get system info: {str(e)}"}), 500