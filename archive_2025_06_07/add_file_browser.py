#!/usr/bin/env python3
"""
Add file browser to admin
Date: 2025-06-06 22:52:22 UTC
Author: thorrobber22
"""

from pathlib import Path

# Read current admin
with open("admin_progress.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert the file browser tab
tabs_line = 'tab1, tab2, tab3 = st.tabs(["🔄 Process IPOs", "📊 Active IPOs", "🔧 Manual Download"])'
new_tabs_line = 'tab1, tab2, tab3, tab4 = st.tabs(["🔄 Process IPOs", "📊 Active IPOs", "🔧 Manual Download", "📁 File Browser"])'

content = content.replace(tabs_line, new_tabs_line)

# Add file browser tab content before the footer
footer_marker = '# Footer'
file_browser_code = '''
with tab4:
    st.subheader("📁 Downloaded Files Browser")
    
    sec_dir = Path("data/sec_documents")
    
    if sec_dir.exists():
        # Get all company directories
        companies = sorted([d for d in sec_dir.iterdir() if d.is_dir()])
        
        if companies:
            # Company selector
            col1, col2 = st.columns([2, 3])
            
            with col1:
                selected_company = st.selectbox(
                    "Select Company",
                    [""] + [d.name for d in companies],
                    format_func=lambda x: f"{x} ({len(list((sec_dir / x).glob('*.*')))} files)" if x else "Choose a company"
                )
            
            if selected_company:
                company_dir = sec_dir / selected_company
                
                # Load metadata
                metadata_file = company_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    with col2:
                        st.info(f"Last scan: {metadata.get('last_scan', 'Unknown')[:19]} • "
                               f"Total files: {metadata.get('total_files', 0)} • "
                               f"Version: {metadata.get('scan_version', 'Unknown')}")
                
                # File type filter
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    file_types = set()
                    for f in company_dir.glob("*.*"):
                        if f.suffix:
                            file_types.add(f.suffix.lower())
                    
                    selected_type = st.selectbox(
                        "File Type",
                        ["All"] + sorted(list(file_types))
                    )
                
                with col2:
                    sort_by = st.selectbox(
                        "Sort By",
                        ["Name", "Size", "Date Modified"]
                    )
                
                # Get files
                if selected_type == "All":
                    files = list(company_dir.glob("*.*"))
                else:
                    files = list(company_dir.glob(f"*{selected_type}"))
                
                # Remove metadata.json from list
                files = [f for f in files if f.name != "metadata.json"]
                
                # Sort files
                if sort_by == "Size":
                    files.sort(key=lambda x: x.stat().st_size, reverse=True)
                elif sort_by == "Date Modified":
                    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                else:
                    files.sort(key=lambda x: x.name)
                
                # Display files
                st.markdown(f"#### Files ({len(files)} total)")
                
                # Create a scrollable container
                with st.container():
                    for file in files:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            # Extract filing type from filename
                            parts = file.stem.split('_')
                            filing_type = parts[0] if parts else "Unknown"
                            st.text(f"📄 {file.name}")
                        
                        with col2:
                            # File size
                            size_kb = file.stat().st_size / 1024
                            if size_kb > 1024:
                                st.caption(f"{size_kb/1024:.1f} MB")
                            else:
                                st.caption(f"{size_kb:.0f} KB")
                        
                        with col3:
                            # File type
                            st.caption(file.suffix.upper()[1:] or "FILE")
                        
                        with col4:
                            # Modified date
                            modified = datetime.fromtimestamp(file.stat().st_mtime)
                            st.caption(modified.strftime("%m/%d"))
                
                # Summary statistics
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_size = sum(f.stat().st_size for f in files) / 1024 / 1024
                    st.metric("Total Size", f"{total_size:.1f} MB")
                
                with col2:
                    file_types_count = {}
                    for f in files:
                        ext = f.suffix.lower()
                        file_types_count[ext] = file_types_count.get(ext, 0) + 1
                    st.metric("File Types", len(file_types_count))
                
                with col3:
                    # Most common filing type
                    filing_types = {}
                    for f in files:
                        parts = f.stem.split('_')
                        if parts:
                            filing_type = parts[0]
                            filing_types[filing_type] = filing_types.get(filing_type, 0) + 1
                    if filing_types:
                        most_common = max(filing_types.items(), key=lambda x: x[1])
                        st.metric("Most Common", f"{most_common[0]} ({most_common[1]})")
                
                with col4:
                    # Average file size
                    if files:
                        avg_size = sum(f.stat().st_size for f in files) / len(files) / 1024
                        st.metric("Avg Size", f"{avg_size:.0f} KB")
                
        else:
            st.info("No companies downloaded yet. Process some IPOs to see files here.")
    else:
        st.warning("SEC documents directory not found. Process some IPOs first.")

# Footer'''

content = content.replace(footer_marker, file_browser_code + '\n\n' + footer_marker)

# Save updated admin
with open("admin_final_browser.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Created admin_final_browser.py with file browser")