"""
System Monitor for Admin Panel
"""

import streamlit as st
import psutil
import time
from datetime import datetime

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def render(self):
        """Render system status"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpu_percent = psutil.cpu_percent(interval=1)
            st.metric("CPU Usage", f"{cpu_percent}%")
        
        with col2:
            memory = psutil.virtual_memory()
            st.metric("Memory Usage", f"{memory.percent}%")
        
        with col3:
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            st.metric("Uptime", f"{hours}h {minutes}m")
    
    def get_status(self):
        """Get system status"""
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }
