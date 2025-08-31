#!/usr/bin/env python3
"""
Fix Flet API references for newer version compatibility.

Updates ft.icons -> ft.Icons and ft.colors -> ft.Colors
"""

import os
import re

def fix_file(filepath):
    """Fix Flet API references in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix icons: ft.icons. -> ft.Icons.
        content = re.sub(r'ft\.icons\.', 'ft.Icons.', content)
        
        # Fix colors: ft.colors. -> ft.Colors.
        content = re.sub(r'ft\.colors\.', 'ft.Colors.', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {filepath}")
            return True
        else:
            print(f"- No changes: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the project."""
    print("🔧 Fixing Flet API references...")
    print("=" * 40)
    
    fixed_count = 0
    total_count = 0
    
    # Find all Python files in src directory
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_count += 1
                if fix_file(filepath):
                    fixed_count += 1
    
    # Also fix demo_mode.py
    if os.path.exists('demo_mode.py'):
        total_count += 1
        if fix_file('demo_mode.py'):
            fixed_count += 1
    
    print("=" * 40)
    print(f"✅ Fixed {fixed_count} out of {total_count} files")
    print("🚀 Ready to run demo!")

if __name__ == "__main__":
    main()
