#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test script for URL validation functionality."""

import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger("url_test")

# Import the function to test
from utils.media_utils import is_valid_url

def test_url_validation():
    """Test the URL validation functionality with various URLs."""
    
    test_cases = [
        # Format: (url, expected_result, description)
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True, "Standard YouTube URL"),
        ("youtu.be/dQw4w9WgXcQ", True, "YouTube short URL"),
        ("https://vimeo.com/123456789", True, "Vimeo URL"),
        ("https://www.dailymotion.com/video/x7zkw0p", True, "Dailymotion URL"),
        ("https://www.pornhub.com/view_video.php?viewkey=68012db864390", True, "PornHub URL"),
        ("https://www.facebook.com/watch?v=123456789", True, "Facebook Watch URL"),
        ("https://twitter.com/username/status/123456789", True, "Twitter video URL"),
        ("https://www.instagram.com/p/ABC123/", True, "Instagram URL"),
        ("https://www.example.com/video", True, "Any domain URL"),
        ("invalid-url", True, "Non-standard URL format - now allowed"),
        ("http://localhost:8080", True, "Local URL - now allowed"),
        ("test", True, "Short text - now allowed as URL"),
        ("a.b", False, "Too short URL - still invalid"),
    ]
    
    passed = 0
    failed = 0
    
    print("\n============ URL VALIDATION TEST RESULTS ============")
    print(f"{'URL':<50} | {'EXPECTED':<10} | {'RESULT':<10} | {'STATUS':<10}")
    print("-" * 85)
    
    for url, expected, description in test_cases:
        result = is_valid_url(url)
        status = "PASS" if result == expected else "FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        # Truncate URL if too long
        display_url = url[:47] + "..." if len(url) > 50 else url.ljust(50)
        print(f"{display_url} | {str(expected):<10} | {str(result):<10} | {status:<10}")
    
    print("-" * 85)
    print(f"Total: {len(test_cases)}, Passed: {passed}, Failed: {failed}")
    print("=" * 85)
    
    return passed, failed

if __name__ == "__main__":
    print("Starting URL validation tests...")
    passed, failed = test_url_validation()
    
    if failed == 0:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} tests failed!")
        sys.exit(1) 