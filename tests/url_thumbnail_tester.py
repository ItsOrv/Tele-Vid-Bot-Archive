#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""URL thumbnail extraction tester.

This script tests various methods to extract thumbnails or previews from URLs.
It supports different types of URLs (video links, webpages, etc.) and tries
multiple methods to get a preview image from each URL.
"""

import os
import sys
import logging
import argparse
import uuid
import json
import traceback
import time
from urllib.parse import urlparse
import tempfile
import requests
from bs4 import BeautifulSoup
import cv2
import re

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("url_thumbnail_tester")

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
            # Add http:// if not present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Accept almost any URL format with minimal validation
            if len(url) < 5:  # Minimum possible URL "h://x"
                return False
                
            return True
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False

class URLThumbnailTester:
    """Test various methods to extract thumbnails from URLs."""
    
    def __init__(self, output_dir=None):
        """Initialize the tester.
        
        Args:
            output_dir: Directory to save thumbnails
        """
        # Use tests/data/thumbnails as the default output directory instead of temp
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "thumbnails")
        self.output_dir = output_dir or default_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
        
        # User agent to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize results
        self.results = {
            'url': None,
            'domain': None,
            'methods_tested': [],
            'successful_methods': [],
            'generated_thumbnails': []
        }
    
    def process_url(self, url):
        """Process URL and try different thumbnail extraction methods.
        
        Args:
            url: URL to process
            
        Returns:
            dict: Results of thumbnail extraction attempts
        """
        if not is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return None
        
        # Add http:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.results['url'] = url
        parsed_url = urlparse(url)
        self.results['domain'] = parsed_url.netloc
        
        logger.info(f"Processing URL: {url}")
        logger.info(f"Domain: {self.results['domain']}")
        
        # Try different methods based on domain
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            logger.info("Detected YouTube URL")
            self.try_youtube_thumbnail(url)
        elif 'vimeo.com' in parsed_url.netloc:
            logger.info("Detected Vimeo URL")
            self.try_vimeo_thumbnail(url)
        elif 'dailymotion.com' in parsed_url.netloc:
            logger.info("Detected Dailymotion URL")
            self.try_dailymotion_thumbnail(url)
        
        # Try general methods for any URL
        self.try_opengraph_thumbnail(url)
        self.try_twitter_card_thumbnail(url)
        self.try_schema_org_thumbnail(url)
        self.try_largest_image(url)
        self.try_screenshot_webpage(url)
        
        return self.results
    
    def save_image(self, image_data, method_name):
        """Save image data to file.
        
        Args:
            image_data: Raw image data or URL to image
            method_name: Name of method that generated the thumbnail
            
        Returns:
            str: Path to saved image or None if failed
        """
        try:
            filename = f"{uuid.uuid4().hex}_{method_name}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            if isinstance(image_data, str) and (image_data.startswith('http://') or image_data.startswith('https://')):
                # If image_data is a URL, download it
                logger.info(f"Downloading image from {image_data}")
                response = requests.get(image_data, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            else:
                # Assume it's binary data
                with open(filepath, 'wb') as f:
                    f.write(image_data)
            
            logger.info(f"Saved thumbnail to {filepath}")
            
            # Add to results
            self.results['generated_thumbnails'].append({
                'method': method_name,
                'path': filepath
            })
            
            if method_name not in self.results['successful_methods']:
                self.results['successful_methods'].append(method_name)
            
            return filepath
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def try_youtube_thumbnail(self, url):
        """Try to get thumbnail from YouTube URL.
        
        Args:
            url: YouTube URL
        """
        self.results['methods_tested'].append('youtube_api')
        try:
            # Extract video ID
            video_id = None
            
            # Pattern for youtu.be URLs
            if 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            
            # Pattern for youtube.com URLs
            elif 'youtube.com/watch' in url:
                query = urlparse(url).query
                params = dict(param.split('=') for param in query.split('&') if '=' in param)
                video_id = params.get('v')
            
            # Pattern for youtube.com/embed URLs
            elif 'youtube.com/embed/' in url:
                video_id = url.split('youtube.com/embed/')[1].split('?')[0]
                
            if video_id:
                # Try multiple thumbnail formats
                thumbnail_urls = [
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # HD
                    f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",      # SD
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",      # HQ
                    f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",      # MQ
                    f"https://img.youtube.com/vi/{video_id}/default.jpg"         # Default
                ]
                
                for i, thumbnail_url in enumerate(thumbnail_urls):
                    try:
                        response = requests.head(thumbnail_url, timeout=5)
                        if response.status_code == 200:
                            quality = ['HD', 'SD', 'HQ', 'MQ', 'Default'][i]
                            logger.info(f"Found YouTube thumbnail ({quality}): {thumbnail_url}")
                            self.save_image(thumbnail_url, f'youtube_{quality.lower()}')
                            break
                    except Exception as e:
                        logger.warning(f"Failed to get YouTube {['HD', 'SD', 'HQ', 'MQ', 'Default'][i]} thumbnail: {str(e)}")
            else:
                logger.warning("Could not extract YouTube video ID from URL")
        except Exception as e:
            logger.error(f"Error in YouTube thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_vimeo_thumbnail(self, url):
        """Try to get thumbnail from Vimeo URL.
        
        Args:
            url: Vimeo URL
        """
        self.results['methods_tested'].append('vimeo_api')
        try:
            # Extract video ID
            video_id = None
            if 'vimeo.com/' in url:
                path_parts = urlparse(url).path.split('/')
                for part in path_parts:
                    if part.isdigit():
                        video_id = part
                        break
            
            if video_id:
                # Use Vimeo oEmbed API
                oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
                response = requests.get(oembed_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'thumbnail_url' in data:
                        thumbnail_url = data['thumbnail_url']
                        logger.info(f"Found Vimeo thumbnail: {thumbnail_url}")
                        self.save_image(thumbnail_url, 'vimeo_api')
                    else:
                        logger.warning("No thumbnail_url in Vimeo API response")
                else:
                    logger.warning(f"Vimeo API returned status code {response.status_code}")
            else:
                logger.warning("Could not extract Vimeo video ID from URL")
        except Exception as e:
            logger.error(f"Error in Vimeo thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_dailymotion_thumbnail(self, url):
        """Try to get thumbnail from Dailymotion URL.
        
        Args:
            url: Dailymotion URL
        """
        self.results['methods_tested'].append('dailymotion_api')
        try:
            # Extract video ID
            video_id = None
            if 'dailymotion.com/video/' in url:
                video_id = url.split('dailymotion.com/video/')[1].split('?')[0]
            
            if video_id:
                # Use Dailymotion oEmbed API
                oembed_url = f"https://www.dailymotion.com/services/oembed?url=https://www.dailymotion.com/video/{video_id}&format=json"
                response = requests.get(oembed_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'thumbnail_url' in data:
                        thumbnail_url = data['thumbnail_url']
                        logger.info(f"Found Dailymotion thumbnail: {thumbnail_url}")
                        self.save_image(thumbnail_url, 'dailymotion_api')
                    else:
                        logger.warning("No thumbnail_url in Dailymotion API response")
                else:
                    logger.warning(f"Dailymotion API returned status code {response.status_code}")
            else:
                logger.warning("Could not extract Dailymotion video ID from URL")
        except Exception as e:
            logger.error(f"Error in Dailymotion thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_opengraph_thumbnail(self, url):
        """Try to extract OpenGraph thumbnail.
        
        Args:
            url: URL to process
        """
        self.results['methods_tested'].append('opengraph')
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for og:image meta tag
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
                # Make sure URL is absolute
                if not image_url.startswith(('http://', 'https://')):
                    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                    if image_url.startswith('/'):
                        image_url = f"{base_url}{image_url}"
                    else:
                        image_url = f"{base_url}/{image_url}"
                
                logger.info(f"Found OpenGraph image: {image_url}")
                self.save_image(image_url, 'opengraph')
            else:
                logger.warning("No OpenGraph image found")
        except Exception as e:
            logger.error(f"Error in OpenGraph thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_twitter_card_thumbnail(self, url):
        """Try to extract Twitter Card thumbnail.
        
        Args:
            url: URL to process
        """
        self.results['methods_tested'].append('twitter_card')
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for twitter:image meta tag
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'}) or \
                           soup.find('meta', attrs={'property': 'twitter:image'})
            
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image['content']
                # Make sure URL is absolute
                if not image_url.startswith(('http://', 'https://')):
                    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                    if image_url.startswith('/'):
                        image_url = f"{base_url}{image_url}"
                    else:
                        image_url = f"{base_url}/{image_url}"
                
                logger.info(f"Found Twitter Card image: {image_url}")
                self.save_image(image_url, 'twitter_card')
            else:
                logger.warning("No Twitter Card image found")
        except Exception as e:
            logger.error(f"Error in Twitter Card thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_schema_org_thumbnail(self, url):
        """Try to extract Schema.org thumbnail.
        
        Args:
            url: URL to process
        """
        self.results['methods_tested'].append('schema_org')
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for JSON-LD schema
            schema_tags = soup.find_all('script', attrs={'type': 'application/ld+json'})
            for tag in schema_tags:
                try:
                    data = json.loads(tag.string)
                    # Look for image in schema
                    image_url = None
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'image' in item:
                                image_url = item['image']
                                if isinstance(image_url, dict) and 'url' in image_url:
                                    image_url = image_url['url']
                                break
                    elif isinstance(data, dict):
                        if 'image' in data:
                            image_url = data['image']
                            if isinstance(image_url, dict) and 'url' in image_url:
                                image_url = image_url['url']
                    
                    if image_url:
                        # Make sure URL is absolute
                        if not isinstance(image_url, str):
                            continue
                            
                        if not image_url.startswith(('http://', 'https://')):
                            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                            if image_url.startswith('/'):
                                image_url = f"{base_url}{image_url}"
                            else:
                                image_url = f"{base_url}/{image_url}"
                        
                        logger.info(f"Found Schema.org image: {image_url}")
                        self.save_image(image_url, 'schema_org')
                        break
                except Exception as e:
                    logger.warning(f"Error parsing JSON-LD: {str(e)}")
            else:
                logger.warning("No Schema.org image found")
        except Exception as e:
            logger.error(f"Error in Schema.org thumbnail extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_largest_image(self, url):
        """Try to find the largest image on the page.
        
        Args:
            url: URL to process
        """
        self.results['methods_tested'].append('largest_image')
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            
            if not images:
                logger.warning("No images found on the page")
                return
            
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            largest_area = 0
            largest_image_url = None
            
            # Find image with width and height attributes
            for img in images:
                width = img.get('width')
                height = img.get('height')
                
                if width and height:
                    try:
                        width = int(width)
                        height = int(height)
                        area = width * height
                        
                        if area > largest_area and width >= 100 and height >= 100:
                            largest_area = area
                            src = img.get('src')
                            if src:
                                # Make sure URL is absolute
                                if not src.startswith(('http://', 'https://')):
                                    if src.startswith('/'):
                                        src = f"{base_url}{src}"
                                    else:
                                        src = f"{base_url}/{src}"
                                largest_image_url = src
                    except ValueError:
                        pass
            
            # If no images with dimensions found, look for data-* attributes
            if not largest_image_url:
                for img in images:
                    for attr in img.attrs:
                        if attr.startswith('data-') and ('width' in attr or 'height' in attr):
                            src = img.get('src') or img.get('data-src')
                            if src:
                                # Make sure URL is absolute
                                if not src.startswith(('http://', 'https://')):
                                    if src.startswith('/'):
                                        src = f"{base_url}{src}"
                                    else:
                                        src = f"{base_url}/{src}"
                                largest_image_url = src
                                break
            
            # If still no image, just take the first one with a src
            if not largest_image_url:
                for img in images:
                    src = img.get('src')
                    if src and not src.endswith(('.gif', '.svg')):
                        # Make sure URL is absolute
                        if not src.startswith(('http://', 'https://')):
                            if src.startswith('/'):
                                src = f"{base_url}{src}"
                            else:
                                src = f"{base_url}/{src}"
                        largest_image_url = src
                        break
            
            if largest_image_url:
                logger.info(f"Found largest image: {largest_image_url}")
                self.save_image(largest_image_url, 'largest_image')
            else:
                logger.warning("No suitable images found")
        except Exception as e:
            logger.error(f"Error in largest image extraction: {str(e)}")
            logger.error(traceback.format_exc())
    
    def try_screenshot_webpage(self, url):
        """Try to take a screenshot of the webpage (if running with GUI).
        
        Args:
            url: URL to process
        """
        self.results['methods_tested'].append('screenshot')
        logger.info("Screenshot method is only supported with additional dependencies (selenium)")
        logger.info("This method requires a GUI environment and is not implemented in this test")
    
    def print_summary(self):
        """Print summary of results."""
        print("\n" + "="*60)
        print(f"URL Thumbnail Test Results for: {self.results['url']}")
        print("="*60)
        print(f"\nDomain: {self.results['domain']}")
        print(f"Methods tested: {len(self.results['methods_tested'])}")
        print(f"Successful methods: {len(self.results['successful_methods'])}")
        print(f"Thumbnails generated: {len(self.results['generated_thumbnails'])}")
        
        if self.results['successful_methods']:
            print("\nSuccessful methods:")
            for method in self.results['successful_methods']:
                print(f"  - {method}")
                
            print("\nGenerated thumbnails:")
            for thumbnail in self.results['generated_thumbnails']:
                print(f"  - {thumbnail['method']}: {thumbnail['path']}")
        else:
            print("\nNo successful methods found.")
            
        print("\nDetailed Method Results:")
        print("-"*60)
        for method in self.results['methods_tested']:
            status = "✅ Success" if method in self.results['successful_methods'] else "❌ Failed"
            print(f"  {method}: {status}")
            
        print("="*60 + "\n")


def main():
    """Main function to run the URL thumbnail tester."""
    parser = argparse.ArgumentParser(
        description="Test various methods to extract thumbnails from URLs."
    )
    parser.add_argument("url", nargs="?", help="URL to test (if not provided, will prompt for input)")
    parser.add_argument("-o", "--output-dir", help="Directory to save thumbnails")
    args = parser.parse_args()
    
    # Get URL from command line or prompt
    url = args.url
    if not url:
        url = input("Enter URL to test: ").strip()
    
    # Create thumbnail tester
    tester = URLThumbnailTester(output_dir=args.output_dir)
    
    # Process URL
    results = tester.process_url(url)
    
    if results:
        # Print summary
        tester.print_summary()
        
        # Always display the path to the thumbnails directory
        abs_output_dir = os.path.abspath(tester.output_dir)
        print(f"Thumbnails directory: {abs_output_dir}")
        
        # Open file explorer if results were generated and platform supports it
        if tester.results['generated_thumbnails']:
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