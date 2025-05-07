# Web Scraper with Image Support

A Python-based web scraper that extracts both content and images from websites. Built with Flask and Crawl4AI.

## Features

- Web page crawling with configurable depth
- Content extraction and storage in Markdown format
- Image downloading and storage
- Web interface for scraping and viewing results
- Responsive image gallery
- Asynchronous processing for better performance

## Project Structure

```
.
├── app.py              # Flask web application
├── main.py            # Main crawling logic
├── image_scraper.py   # Image scraping module
├── requirements.txt   # Python dependencies
├── templates/         # HTML templates
│   ├── index.html    # Main page
│   ├── pages.html    # List of scraped pages
│   └── view_page.html # Page content and images view
└── scraped_pages/    # Storage directory
    └── domain__page/
        ├── domain__page.md
        └── images/
            ├── image1.jpg
            └── image2.png
```

## Image Scraping Implementation

The image scraping functionality is implemented in the `image_scraper.py` module, which provides:

1. **ImageScraper Class**:
   - Asynchronous image downloading
   - Automatic directory creation
   - Image type validation
   - Safe filename generation
   - Error handling

2. **Storage Structure**:
   - Images are stored in a subdirectory named `images` within each page's directory
   - Original image filenames are preserved when possible
   - Invalid characters in filenames are replaced with underscores

3. **Features**:
   - Supports multiple image formats (jpg, png, gif, webp)
   - Handles relative and absolute URLs
   - Skips invalid or non-image URLs
   - Lazy loading in the web interface
   - Responsive image grid layout

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter a URL to scrape and configure:
   - Maximum crawl depth
   - Tags to extract (optional)

4. View results:
   - Click "View Scraped Pages" to see all scraped content
   - Each page shows both markdown content and associated images
   - Images are displayed in a responsive grid layout

## Dependencies

Key dependencies include:
- Flask: Web framework
- Crawl4AI: Web crawling library
- BeautifulSoup4: HTML parsing
- aiohttp: Asynchronous HTTP client
- Playwright: Browser automation

See `requirements.txt` for the complete list.

## Notes

- Images are downloaded asynchronously to improve performance
- The scraper respects website structure and follows internal links only
- Image downloads are handled gracefully with error recovery
- The web interface provides a user-friendly way to browse results 