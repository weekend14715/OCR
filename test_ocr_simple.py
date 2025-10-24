#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PIL import Image, ImageDraw

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ocr_functionality():
    """Test chức năng OCR cơ bản"""
    print("=== TEST OCR FUNCTIONALITY ===")
    
    try:
        # Import OCR class
        from ocr_tool import ScreenSelector
        
        # Tạo một ảnh test đơn giản với text
        img = Image.new('RGB', (300, 100), 'white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Hello World", fill='black')
        
        print("OK - Tao anh test thanh cong")
        
        # Test OCR
        selector = ScreenSelector()
        result = selector.ocr(img)
        
        if result:
            print(f"OK - OCR thanh cong: '{result}'")
        else:
            print("ERROR - OCR khong tra ve ket qua")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_functionality()
