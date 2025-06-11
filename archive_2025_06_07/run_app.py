import streamlit.cli as stcli
import sys
import os

if __name__ == '__main__':
    # Set up the path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the app
    sys.argv = ["streamlit", "run", "frontend/app.py", "--server.port=8501"]
    sys.exit(stcli.main())
