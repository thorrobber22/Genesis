"""
Simple authentication with magic links
"""
import streamlit as st
from datetime import datetime, timedelta
import secrets

def authenticate(email: str) -> bool:
    """Send magic link (for MVP, just return True)"""
    # In production, would send email with unique token
    return True

def check_auth() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)
