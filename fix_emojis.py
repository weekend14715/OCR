#!/usr/bin/env python3
"""
Script để thay thế emoji trong LicenseManager
"""

import re

def fix_emojis():
    emoji_replacements = {
        '🔐': '[LICENSE]',
        '🔍': '[CHECK]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '💾': '[SAVE]',
        '📁': '[FOLDER]',
        '📄': '[FILE]'
    }
    
    # Đọc file
    with open('license/license_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thay thế emoji
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Ghi lại file
    with open('license/license_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Da thay the emoji thanh cong!")

if __name__ == "__main__":
    fix_emojis()
