import os
import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

class ImageScraper:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def download_image(self, img_url, page_url, page_dir):
        """Download an image and save it to the specified directory."""
        try:
            # Create absolute URL if needed
            img_url = urljoin(page_url, img_url)
            
            # Skip data URLs
            if img_url.startswith('data:'):
                return None

            # Get image filename from URL
            parsed = urlparse(img_url)
            filename = os.path.basename(parsed.path)
            
            # Skip if no filename
            if not filename:
                return None

            # Add extension if missing
            if '.' not in filename:
                filename += '.jpg'

            # Create safe filename
            filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
            
            # Create images directory for this page
            images_dir = os.path.join(page_dir, 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            # Full path for the image
            filepath = os.path.join(images_dir, filename)
            
            # Download and save image
            async with self.session.get(img_url) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        with open(filepath, 'wb') as f:
                            f.write(await response.read())
                        return filename
            return None
        except Exception as e:
            print(f"Error downloading image {img_url}: {str(e)}")
            return None

    async def scrape_images(self, html_content, page_url, page_dir):
        """Extract and download images from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        
        downloaded_images = []
        for img in img_tags:
            src = img.get('src')
            if src:
                filename = await self.download_image(src, page_url, page_dir)
                if filename:
                    downloaded_images.append(filename)
        
        return downloaded_images 