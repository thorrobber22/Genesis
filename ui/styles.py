"""
Custom Styles - White/Black/Blue Theme
"""

import streamlit as st

def load_custom_css():
    """Load custom CSS"""
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    /* Primary buttons */
    .stButton > button {
        background-color: #0066FF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0052CC;
    }
    
    /* Chat input */
    .stChatInput > div > div > input {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1A1A1A;
        font-weight: 600;
    }
    
    /* Data tables */
    .dataframe {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #F0F7FF;
        border: 1px solid #0066FF;
        border-radius: 6px;
        color: #0052CC;
    }
    
    /* Make columns responsive */
    @media (max-width: 768px) {
        .row-widget.stHorizontal {
            flex-direction: column;
        }
    }
    </style>
    """, unsafe_allow_html=True)
