#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import signal
import threading
from pystray import Icon, Menu, MenuItem

def test_cleanup():
    """Test cleanup function."""
    print("Test cleanup function...")
    
    # Tạo icon test
    icon = Icon("test", None, "Test Icon")
    
    def cleanup():
        print("Dang cleanup...")
        try:
            icon.stop()
        except:
            pass
        try:
            import pystray
            pystray.Icon.stop_all()
        except:
            pass
        print("Cleanup hoan tat")
        os._exit(0)
    
    def signal_handler(signum, frame):
        cleanup()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Tạo menu
    menu = Menu(
        MenuItem("Test", lambda: print("Test clicked")),
        MenuItem("Exit", lambda: cleanup())
    )
    
    icon.menu = menu
    
    print("Icon da duoc tao. Nhan Ctrl+C de test cleanup...")
    
    try:
        icon.run()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    test_cleanup()
