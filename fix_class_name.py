#!/usr/bin/env python3
"""
Fix class name issue in pipeline_manager.py
Date: 2025-06-07 19:21:05 UTC
Author: thorrobber22
"""

from pathlib import Path

def fix_class_alias():
    """Add PipelineManager alias to pipeline_manager.py"""
    
    pipeline_path = Path("scrapers/sec/pipeline_manager.py")
    
    if not pipeline_path.exists():
        print("❌ pipeline_manager.py not found!")
        return False
    
    print("Adding PipelineManager alias...")
    
    with open(pipeline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if alias already exists
    if 'PipelineManager = IPOPipelineManager' in content:
        print("✅ Alias already exists")
        return True
    
    # Add alias at the end of file
    if not content.endswith('\n'):
        content += '\n'
    
    content += '\n# Alias for compatibility\nPipelineManager = IPOPipelineManager\n'
    
    with open(pipeline_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added PipelineManager = IPOPipelineManager alias")
    return True

def verify_fix():
    """Verify the fix worked"""
    try:
        from scrapers.sec.pipeline_manager import PipelineManager, IPOPipelineManager
        print("✅ Both class names now work!")
        print(f"   - IPOPipelineManager: {IPOPipelineManager}")
        print(f"   - PipelineManager: {PipelineManager}")
        return True
    except ImportError as e:
        print(f"❌ Import still failing: {e}")
        return False

def main():
    print("FIXING CLASS NAME ISSUE")
    print("=" * 60)
    
    # Fix the class name
    if fix_class_alias():
        print("\nVerifying fix...")
        if verify_fix():
            print("\n🎉 Success! All 42 tests should now pass!")
        else:
            print("\n⚠️ Fix applied but verification failed")
    else:
        print("\n❌ Could not apply fix")

if __name__ == "__main__":
    main()