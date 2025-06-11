#!/usr/bin/env python3
"""
Apply Apple-style cream theme to Hedge Intelligence
"""

from pathlib import Path

def update_main_app_theme():
    """Update hedge_intelligence.py with cream theme"""
    print("🎨 Applying Apple cream theme...")
    
    app_path = Path("hedge_intelligence.py")
    
    if not app_path.exists():
        print("❌ hedge_intelligence.py not found!")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the apply_dark_theme function
    new_theme_function = '''def apply_cream_theme():
    """Apply Apple-style cream theme"""
    st.markdown("""
    <style>
    /* Hedge Intelligence - Premium Apple Theme */
    
    /* Remove Streamlit defaults */
    .stApp {
        background-color: #FAFAF8;
    }
    
    /* Main content area */
    .main {
        background-color: #FAFAF8;
        color: #1A1A1A;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1A1A1A !important;
        font-weight: 600;
    }
    
    /* Text */
    p, span, div {
        color: #1A1A1A;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F5F5F3;
    }
    
    /* Buttons - Dark with blue hover */
    .stButton > button {
        background-color: #2D2D2D;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #007AFF;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
    }
    
    /* Cards and containers */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
    }
    
    /* Links */
    a {
        color: #1A1A1A;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    a:hover {
        color: #007AFF;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Remove blue progress bars */
    .stProgress > div > div > div {
        background-color: #34C759;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E7;
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F5F5F3;
        color: #1A1A1A;
        border-radius: 8px;
    }
    
    /* Data editor/tables */
    .glideDataEditor {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    
    /* Remove all remaining blue */
    .css-1cpxqw2, .css-1v0mbdj > img {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)'''
    
    # Replace apply_dark_theme with apply_cream_theme
    if 'def apply_dark_theme' in content:
        # Find the function and replace it
        import re
        pattern = r'def apply_dark_theme\(\):.*?(?=\ndef|\nif|\nclass|\Z)'
        content = re.sub(pattern, new_theme_function, content, flags=re.DOTALL)
        
        # Also replace the function call
        content = content.replace('apply_dark_theme()', 'apply_cream_theme()')
    else:
        # Add the function before main
        content = new_theme_function + '\n\n' + content
        
        # Add the call after page config
        if 'st.set_page_config' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'st.set_page_config' in line:
                    # Insert after the closing parenthesis
                    j = i
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    lines.insert(j + 1, '    apply_cream_theme()')
                    break
            content = '\n'.join(lines)
    
    # Save updated file
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Cream theme applied!")
    
    # Also update any component files that might have blue
    update_component_styles()

def update_component_styles():
    """Remove blue from component files"""
    print("\n🔍 Checking components for blue styling...")
    
    components = [
        "components/dashboard.py",
        "components/document_explorer.py",
        "components/chat.py"
    ]
    
    for comp_path in components:
        path = Path(comp_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace any blue references
            original = content
            content = content.replace("info", "secondary")
            content = content.replace("primary", "secondary")
            content = content.replace("#007bff", "#2D2D2D")
            content = content.replace("blue", "#2D2D2D")
            
            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Updated {comp_path}")
            else:
                print(f"  ✓ {comp_path} - no blue found")

def main():
    print("🎨 APPLYING APPLE CREAM THEME")
    print("="*70)
    
    update_main_app_theme()
    
    print("\n✅ Theme update complete!")
    print("Restart the app to see the new cream theme.")

if __name__ == "__main__":
    main()