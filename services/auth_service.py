"""
Authentication Service (Minimal)
Created: 2025-06-09 15:15:47 UTC
"""

class AuthService:
    """Basic authentication service"""
    
    def __init__(self):
        self.users = {"admin": "hedgeadmin2025"}
    
    def authenticate(self, username, password):
        """Simple authentication"""
        return self.users.get(username) == password
    
    def get_user_role(self, username):
        """Get user role"""
        return "admin" if username == "admin" else "user"
