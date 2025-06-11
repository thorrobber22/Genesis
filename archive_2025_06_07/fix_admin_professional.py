#!/usr/bin/env python3
"""
Fix the metadata error in professional admin
Date: 2025-06-06 22:21:31 UTC
Author: thorrobber22
"""

from pathlib import Path

# Read the admin file
admin_file = Path("admin_professional.py")
with open(admin_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the metadata scope issue
# Find the problematic section
old_section = '''                # Show filing types breakdown
                if metadata and 'filing_types' in metadata:
                    st.markdown("#### Filing Types")
                    filing_df = pd.DataFrame(
                        [(k, v) for k, v in metadata['filing_types'].items()],
                        columns=['Type', 'Count']
                    )
                    st.bar_chart(filing_df.set_index('Type'))'''

new_section = '''                # Show filing types breakdown
                if metadata_file.exists() and 'filing_types' in metadata:
                    st.markdown("#### Filing Types")
                    filing_df = pd.DataFrame(
                        [(k, v) for k, v in metadata['filing_types'].items()],
                        columns=['Type', 'Count']
                    )
                    st.bar_chart(filing_df.set_index('Type'))'''

# Replace the section
content = content.replace(old_section, new_section)

# Also initialize metadata at the beginning of the section
# Find where metadata is loaded
metadata_load = '''                # Load metadata
                metadata_file = ticker_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)'''

new_metadata_load = '''                # Load metadata
                metadata_file = ticker_dir / "metadata.json"
                metadata = {}
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)'''

content = content.replace(metadata_load, new_metadata_load)

# Save the fixed file
with open(admin_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed metadata error in admin_professional.py")
print("\nRun: streamlit run admin_professional.py")