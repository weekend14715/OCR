#!/usr/bin/env python3
"""
Script để thay thế tất cả emoji trong ocr_tool.py
"""

import re

# Mapping emoji to text
emoji_replacements = {
    '🚀': '[START]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '🔑': '[KEY]',
    'ℹ️': '[INFO]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    '📖': '[GUIDE]',
    '👋': '[EXIT]',
    '🎨': '[COLOR]',
    '📐': '[SIZE]',
    '📊': '[STATS]',
    '✨': '[SHARP]',
    '⚫⚪': '[THRESHOLD]',
    '🧹': '[CLEAN]',
    '🎯': '[TARGET]'
}

def fix_unicode_in_file():
    """Fix Unicode emojis in ocr_tool.py"""
    
    # Read file
    with open('ocr_tool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace emojis
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Write back
    with open('ocr_tool.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Da thay the tat ca emoji trong ocr_tool.py")

if __name__ == "__main__":
    fix_unicode_in_file()
