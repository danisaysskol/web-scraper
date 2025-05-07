from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
import os
from main import crawl_page
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    tags = request.form.get('tags')
    max_depth = int(request.form.get('max_depth', 1))
    output_dir = 'scraped_pages'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    async def run_crawl():
        browser_config = BrowserConfig(headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            await crawl_page(
                crawler=crawler,
                url=url,
                visited=set(),
                output_dir=output_dir,
                depth=0,
                max_depth=max_depth,
            )
    try:
        asyncio.run(run_crawl())
        return jsonify({'success': True, 'message': 'Scraping completed!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/pages')
def list_pages():
    files = [f for f in os.listdir('scraped_pages') if f.endswith('.md')]
    return render_template('pages.html', files=files)

@app.route('/pages/<filename>')
def view_page(filename):
    path = os.path.join('scraped_pages', filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get images for this page
        page_dir = os.path.splitext(path)[0]
        images_dir = os.path.join(page_dir, 'images')
        images = []
        if os.path.exists(images_dir):
            images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        
        return render_template('view_page.html', 
                             content=content, 
                             filename=filename,
                             images=images,
                             page_dir=os.path.basename(page_dir))
    return 'Page not found', 404

@app.route('/images/<page_dir>/<filename>')
def serve_image(page_dir, filename):
    images_dir = os.path.join('scraped_pages', f"{page_dir}", 'images')
    return send_from_directory(images_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
