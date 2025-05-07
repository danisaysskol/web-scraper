import asyncio
import os
import re
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from image_scraper import ImageScraper

# OPTIONAL: If you want to store JSON with additional info,
# you can import json and store a dictionary. 
# import json

async def crawl_page(
    crawler,
    url,
    visited,
    output_dir,
    depth=0,
    max_depth=2,
    progress_callback=None
):
    """
    Recursively crawls the given URL up to `max_depth` levels deep, 
    storing each page's content locally in Markdown and downloading images.
    """
    if depth > max_depth:
        return

    # Mark this URL as visited
    visited.add(url)
    print(f"[Depth {depth}] Crawling: {url}")

    # Update progress
    if progress_callback:
        progress_callback(len(visited), len(visited) + 1, f"Crawling: {url}")

    # Run the crawl
    run_config = CrawlerRunConfig()
    result = await crawler.arun(url=url, config=run_config)

    # If crawl wasn't successful, just log and return
    if not result.success:
        print(f"Failed to crawl {url} - {result.error_message}")
        if progress_callback:
            progress_callback(len(visited), len(visited), f"Failed to crawl: {url}")
        return

    # ---------------------------------------------------
    # 1. Store the page content in Markdown files
    # ---------------------------------------------------
    parsed = urlparse(url)
    netloc = parsed.netloc.replace(":", "_")
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    path = re.sub(r"[^a-zA-Z0-9_\-]", "_", path)

    filename = f"{netloc}__{path}.md"
    file_path = os.path.join(output_dir, filename)
    page_dir = os.path.splitext(file_path)[0]

    # Save markdown content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result.markdown)

    print(f"  Saved: {file_path}")

    # Update progress
    if progress_callback:
        progress_callback(len(visited), len(visited) + 1, f"Processing images: {url}")

    # ---------------------------------------------------
    # 2. Download images from the page
    # ---------------------------------------------------
    async with ImageScraper(output_dir) as image_scraper:
        downloaded_images = await image_scraper.scrape_images(
            result.html,
            url,
            page_dir
        )
        if downloaded_images:
            print(f"  Downloaded {len(downloaded_images)} images")

    # ---------------------------------------------------
    # 3. Recursively follow internal links
    # ---------------------------------------------------
    if "internal" in result.links:
        total_links = len(result.links["internal"])
        for i, link_info in enumerate(result.links["internal"], 1):
            href = link_info["href"]
            next_url = urljoin(url, href)

            if next_url not in visited:
                if progress_callback:
                    progress_callback(len(visited), len(visited) + total_links, 
                                    f"Following link {i}/{total_links}: {next_url}")
                await crawl_page(
                    crawler,
                    next_url,
                    visited,
                    output_dir,
                    depth=depth + 1,
                    max_depth=max_depth,
                    progress_callback=progress_callback
                )

    # Update final progress
    if progress_callback:
        progress_callback(len(visited), len(visited), f"Completed: {url}")



