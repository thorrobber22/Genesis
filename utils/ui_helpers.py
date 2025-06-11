"""
UI Helper Functions
Date: 2025-06-07 14:19:15 UTC
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import humanize

def format_date(date_str: str, format: str = "YYYY-MM-DD") -> str:
    """Format date string based on user preference"""
    try:
        dt = datetime.fromisoformat(date_str) if isinstance(date_str, str) else date_str
        
        if format == "MM/DD/YYYY":
            return dt.strftime('%m/%d/%Y')
        elif format == "DD/MM/YYYY":
            return dt.strftime('%d/%m/%Y')
        else:  # Default YYYY-MM-DD
            return dt.strftime('%Y-%m-%d')
    except:
        return str(date_str)

def format_time_ago(timestamp: float) -> str:
    """Format timestamp as human-readable time ago"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return humanize.naturaltime(datetime.now() - dt)
    except:
        return "Unknown"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def show_loading_message(message: str = "Loading..."):
    """Show a loading message with spinner"""
    with st.spinner(message):
        return True

def show_error_message(error: str, details: Optional[str] = None):
    """Show error message with optional details"""
    st.error(error)
    if details:
        with st.expander("Error details"):
            st.code(details)

def show_success_message(message: str, balloons: bool = False):
    """Show success message with optional balloons"""
    st.success(message)
    if balloons:
        st.balloons()

def confirm_action(action: str, key: str) -> bool:
    """Show confirmation dialog for an action"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.warning(f"Are you sure you want to {action}?")
    
    with col2:
        if st.button("Confirm", key=f"confirm_{key}", type="primary"):
            return True
    
    return False

def create_metric_card(title: str, value: Any, delta: Optional[Any] = None, help_text: Optional[str] = None):
    """Create a metric card with optional delta and help text"""
    if help_text:
        st.metric(label=title, value=value, delta=delta, help=help_text)
    else:
        st.metric(label=title, value=value, delta=delta)

def create_progress_bar(current: int, total: int, label: str = "Progress"):
    """Create a progress bar"""
    if total > 0:
        progress = current / total
        st.progress(progress, text=f"{label}: {current}/{total} ({progress:.0%})")
    else:
        st.progress(0.0, text=f"{label}: 0/0")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def highlight_text(text: str, search_term: str) -> str:
    """Highlight search term in text"""
    if not search_term:
        return text
    
    import re
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group()}**", text)

def create_download_button(data: bytes, filename: str, label: str = "Download", mime: str = "application/octet-stream"):
    """Create a styled download button"""
    st.download_button(
        label=f"📥 {label}",
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True
    )

def create_sidebar_nav_item(icon: str, label: str, active: bool = False):
    """Create a sidebar navigation item"""
    if active:
        st.markdown(f"""
        <div style="background-color: #007AFF; color: white; padding: 10px; border-radius: 5px; margin: 5px 0;">
            {icon} {label}
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button(f"{icon} {label}", use_container_width=True):
            return True
    return False

def format_lock_up_status(expiry_date: str) -> Dict[str, str]:
    """Format lock-up expiry status"""
    try:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
        today = datetime.now()
        days_until = (expiry - today).days
        
        if days_until < 0:
            return {
                'status': 'Expired',
                'days': 'Expired',
                'color': 'red'
            }
        elif days_until <= 7:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'orange'
            }
        elif days_until <= 30:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'yellow'
            }
        else:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'green'
            }
    except:
        return {
            'status': 'Unknown',
            'days': 'N/A',
            'color': 'gray'
        }

def create_empty_state(message: str, action_label: Optional[str] = None, action_callback: Optional[callable] = None):
    """Create an empty state message with optional action"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info(message)
        
        if action_label and action_callback:
            if st.button(action_label, use_container_width=True):
                action_callback()

def format_confidence_score(score: float) -> str:
    """Format AI confidence score with color"""
    percentage = score * 100
    
    if score >= 0.9:
        return f"🟢 {percentage:.0f}% confidence"
    elif score >= 0.7:
        return f"🟡 {percentage:.0f}% confidence"
    else:
        return f"🔴 {percentage:.0f}% confidence"

def create_data_table(data: List[Dict], selectable: bool = True, key: str = "table"):
    """Create a formatted data table"""
    import pandas as pd
    
    if not data:
        st.info("No data available")
        return None
    
    df = pd.DataFrame(data)
    
    if selectable:
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=key
        )
        
        if event.selection.rows:
            return df.iloc[event.selection.rows[0]]
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    return None
