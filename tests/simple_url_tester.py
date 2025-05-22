#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple URL tester.

A simpler version of the thumbnail tester using only standard libraries.
"""

import os
import sys
import logging
import urllib.request
import urllib.parse
import json
import re
import uuid
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("simple_url_tester")

# Add parent directory to path for imports if running as script
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import from project structure if available
try:
    from utils.media_utils import is_valid_url
except ImportError:
    # Define a simple version if not available
    def is_valid_url(url):
        """Basic URL validation."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            if len(url) < 5:  # Minimum possible URL "h://x"
                return False
                
            return True
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False

class SimpleURLTester:
    """Test URL processing with minimal dependencies."""
    
    def __init__(self, output_dir=None):
        """Initialize the tester.
        
        Args:
            output_dir: Directory to save test results
        """
        # Use tests/data/url_tests as the default output directory instead of temp
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "url_tests")
        self.output_dir = output_dir or default_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
        
        # User agent to mimic browser
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        # Initialize results
        self.results = {
            'url': None,
            'domain': None,
            'timestamp': datetime.now().isoformat(),
            'tests': []
        }
    
    def add_test_result(self, test_name, success, message=None, data=None):
        """Add a test result.
        
        Args:
            test_name: Name of the test
            success: Whether the test succeeded
            message: Optional message
            data: Optional data about the test
        """
        self.results['tests'].append({
            'name': test_name,
            'success': success,
            'message': message,
            'data': data
        })
        
        if success:
            logger.info(f"✅ {test_name}: {message}")
        else:
            logger.warning(f"❌ {test_name}: {message}")
    
    def process_url(self, url):
        """Process URL and try different tests.
        
        Args:
            url: URL to process
            
        Returns:
            dict: Results of tests
        """
        if not is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return None
        
        # Add http:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.results['url'] = url
        parsed_url = urllib.parse.urlparse(url)
        self.results['domain'] = parsed_url.netloc
        
        logger.info(f"Processing URL: {url}")
        logger.info(f"Domain: {self.results['domain']}")
        
        # Test basic connectivity
        self.test_connectivity(url)
        
        # Test URL format and components
        self.test_url_components(url)
        
        # Test for redirects
        self.test_redirects(url)
        
        # Test URL in Telegram format
        self.test_telegram_format(url)
        
        # Test for video platform
        self.test_video_platform(url)
        
        # Save results to JSON file
        result_path = os.path.join(self.output_dir, f"result_{uuid.uuid4().hex}.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {result_path}")
        
        return self.results
    
    def test_connectivity(self, url):
        """Test basic connectivity to the URL.
        
        Args:
            url: URL to test
        """
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': self.user_agent}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content_type = response.getheader('Content-Type')
                
                self.add_test_result(
                    "connectivity",
                    success=status_code == 200,
                    message=f"Status code: {status_code}, Content-Type: {content_type}",
                    data={
                        'status_code': status_code,
                        'content_type': content_type,
                        'headers': dict(response.getheaders())
                    }
                )
        except Exception as e:
            self.add_test_result(
                "connectivity",
                success=False,
                message=f"Connection error: {str(e)}"
            )
    
    def test_url_components(self, url):
        """Test URL format and components.
        
        Args:
            url: URL to test
        """
        try:
            parsed = urllib.parse.urlparse(url)
            components = {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
            
            # Parse query parameters
            query_params = {}
            if parsed.query:
                for param in parsed.query.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
                        
            components['query_params'] = query_params
            
            self.add_test_result(
                "url_components",
                success=True,
                message=f"URL structure: {parsed.scheme}://{parsed.netloc}{parsed.path}",
                data=components
            )
        except Exception as e:
            self.add_test_result(
                "url_components",
                success=False,
                message=f"Failed to parse URL components: {str(e)}"
            )
    
    def test_redirects(self, url):
        """Test if URL redirects.
        
        Args:
            url: URL to test
        """
        try:
            class RedirectHandler(urllib.request.HTTPRedirectHandler):
                def __init__(self):
                    self.redirections = []
                
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    self.redirections.append((code, newurl))
                    return super().redirect_request(req, fp, code, msg, headers, newurl)
            
            redirect_handler = RedirectHandler()
            opener = urllib.request.build_opener(redirect_handler)
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': self.user_agent}
            )
            
            with opener.open(req, timeout=10) as response:
                final_url = response.geturl()
                redirects = redirect_handler.redirections
                
                if redirects:
                    redirect_chain = " -> ".join([f"{code}: {url}" for code, url in redirects])
                    self.add_test_result(
                        "redirects",
                        success=True,
                        message=f"URL redirects: {len(redirects)} redirects, final URL: {final_url}",
                        data={
                            'redirect_count': len(redirects),
                            'redirects': redirects,
                            'final_url': final_url
                        }
                    )
                else:
                    self.add_test_result(
                        "redirects",
                        success=True,
                        message="URL does not redirect"
                    )
        except Exception as e:
            self.add_test_result(
                "redirects",
                success=False,
                message=f"Failed to test redirects: {str(e)}"
            )
    
    def test_telegram_format(self, url):
        """Test how the URL might be processed in Telegram.
        
        Args:
            url: URL to test
        """
        # Simulate different ways Telegram might process the URL
        variations = [
            ('original', url),
            ('with_t.me_prefix', f"https://t.me/share/url?url={urllib.parse.quote(url)}"),
            ('as_text', f"Check out this link: {url}"),
            ('in_markdown', f"[Link]({url})"),
            ('in_html', f'<a href="{url}">Link</a>')
        ]
        
        results = []
        for name, variant in variations:
            results.append({
                'type': name,
                'url': variant
            })
        
        self.add_test_result(
            "telegram_format",
            success=True,
            message=f"Generated {len(variations)} Telegram URL variations",
            data=results
        )
    
    def test_video_platform(self, url):
        """Test if the URL is from a known video platform.
        
        Args:
            url: URL to test
        """
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path
        
        platforms = {
            'youtube': {
                'domains': ['youtube.com', 'youtu.be', 'www.youtube.com'],
                'patterns': [
                    r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
                    r'youtu\.be/([a-zA-Z0-9_-]+)',
                    r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
                ]
            },
            'vimeo': {
                'domains': ['vimeo.com', 'player.vimeo.com'],
                'patterns': [
                    r'vimeo\.com/(\d+)',
                    r'vimeo\.com/channels/[^/]+/(\d+)',
                    r'player\.vimeo\.com/video/(\d+)'
                ]
            },
            'dailymotion': {
                'domains': ['dailymotion.com', 'dai.ly'],
                'patterns': [
                    r'dailymotion\.com/video/([a-zA-Z0-9]+)',
                    r'dai\.ly/([a-zA-Z0-9]+)'
                ]
            },
            'facebook': {
                'domains': ['facebook.com', 'fb.com', 'fb.watch'],
                'patterns': [
                    r'facebook\.com/watch/?\?v=(\d+)',
                    r'fb\.watch/([^/]+)'
                ]
            },
            'instagram': {
                'domains': ['instagram.com', 'instagr.am'],
                'patterns': [
                    r'instagram\.com/p/([^/]+)',
                    r'instagram\.com/tv/([^/]+)',
                    r'instagram\.com/reel/([^/]+)'
                ]
            },
            'twitter': {
                'domains': ['twitter.com', 'x.com'],
                'patterns': [
                    r'twitter\.com/[^/]+/status/(\d+)',
                    r'x\.com/[^/]+/status/(\d+)'
                ]
            },
            'pornhub': {
                'domains': ['pornhub.com', 'www.pornhub.com'],
                'patterns': [
                    r'pornhub\.com/view_video.php\?viewkey=([a-zA-Z0-9]+)',
                    r'pornhub\.com/embed/([a-zA-Z0-9]+)'
                ]
            }
        }
        
        detected_platform = None
        detected_id = None
        
        for platform, info in platforms.items():
            # Check domain
            if any(d in domain for d in info['domains']):
                # Check patterns
                for pattern in info['patterns']:
                    match = re.search(pattern, url)
                    if match:
                        detected_platform = platform
                        detected_id = match.group(1)
                        break
                        
            if detected_platform:
                break
        
        if detected_platform:
            self.add_test_result(
                "video_platform",
                success=True,
                message=f"Detected {detected_platform} video with ID: {detected_id}",
                data={
                    'platform': detected_platform,
                    'id': detected_id
                }
            )
        else:
            self.add_test_result(
                "video_platform",
                success=False,
                message="Not a recognized video platform"
            )
    
    def print_summary(self):
        """Print summary of results."""
        success_count = sum(1 for test in self.results['tests'] if test['success'])
        total_count = len(self.results['tests'])
        
        print("\n" + "="*60)
        print(f"URL Test Results for: {self.results['url']}")
        print("="*60)
        print(f"\nDomain: {self.results['domain']}")
        print(f"Tests passed: {success_count}/{total_count}")
        
        print("\nTest Results:")
        print("-"*60)
        for test in self.results['tests']:
            status = "✅ Success" if test['success'] else "❌ Failed"
            print(f"  {test['name']}: {status}")
            print(f"    {test['message']}")
            
        print("="*60 + "\n")


def main():
    """Main function to run the URL tester."""
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL to test: ").strip()
    
    # Create tester
    tester = SimpleURLTester()
    
    # Process URL
    results = tester.process_url(url)
    
    if results:
        # Print summary
        tester.print_summary()
        
        # Display absolute path to the results directory
        abs_output_dir = os.path.abspath(tester.output_dir)
        print(f"Results directory: {abs_output_dir}")
        
        # Open file explorer if platform supports it
        if sys.platform == "darwin":  # macOS
            os.system(f"open {abs_output_dir}")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer {abs_output_dir}")
        elif sys.platform == "linux" and os.path.exists("/usr/bin/xdg-open"):  # Linux with xdg-open
            os.system(f"xdg-open {abs_output_dir}")
    else:
        print(f"Failed to process URL: {url}")


if __name__ == "__main__":
    main() 