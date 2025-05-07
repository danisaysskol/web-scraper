from flask import Flask, render_template, request, jsonify, send_from_directory, session
import asyncio
import os
import shutil
import json
import csv
from main import crawl_page
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session

# Global variable to store scraping progress
scraping_progress = {
    'current': 0,
    'total': 0,
    'status': '',
    'is_running': False,
    'should_stop': False
}

@app.route('/')
def index():
    return render_template('index.html', progress=scraping_progress)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    tags = request.form.get('tags')
    max_depth = int(request.form.get('max_depth', 1))
    output_dir = 'scraped_pages'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Reset progress
    global scraping_progress
    scraping_progress = {
        'current': 0,
        'total': 0,
        'status': 'Starting scraping process...',
        'is_running': True,
        'should_stop': False
    }

    async def run_crawl():
        browser_config = BrowserConfig(headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            try:
                await crawl_page(
                    crawler=crawler,
                    url=url,
                    visited=set(),
                    output_dir=output_dir,
                    depth=0,
                    max_depth=max_depth,
                    progress_callback=update_progress
                )
            except Exception as e:
                scraping_progress['status'] = f'Error: {str(e)}'
            finally:
                scraping_progress['is_running'] = False
                # Save data in JSON and CSV formats
                save_data_in_formats(output_dir)

    def update_progress(current, total, status):
        global scraping_progress
        if scraping_progress['should_stop']:
            raise Exception('Scraping stopped by user')
        scraping_progress['current'] = current
        scraping_progress['total'] = total
        scraping_progress['status'] = status

    def save_data_in_formats(output_dir):
        # Create JSON file
        json_data = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                json_data.append({
                    'filename': filename,
                    'content': content,
                    'url': url
                })
        
        # Save JSON
        with open(os.path.join(output_dir, 'scraped_data.json'), 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        with open(os.path.join(output_dir, 'scraped_data.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Filename', 'Content', 'URL'])
            for item in json_data:
                writer.writerow([item['filename'], item['content'], item['url']])

    try:
        asyncio.run(run_crawl())
        return jsonify({'success': True, 'message': 'Scraping completed!'})
    except Exception as e:
        scraping_progress['is_running'] = False
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop-scraping', methods=['POST'])
def stop_scraping():
    global scraping_progress
    scraping_progress['should_stop'] = True
    return jsonify({'success': True, 'message': 'Stopping scraping process...'})

@app.route('/progress')
def get_progress():
    return jsonify(scraping_progress)

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

@app.route('/delete-page', methods=['POST'])
def delete_page():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': 'No filename provided'})

    try:
        # Get the full path of the file and its directory
        file_path = os.path.join('scraped_pages', filename)
        dir_path = os.path.splitext(file_path)[0]

        # Delete the markdown file
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the associated directory (which contains images)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

        return jsonify({'success': True, 'message': 'Page deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete-all-pages', methods=['POST'])
def delete_all_pages():
    try:
        # Get all markdown files
        files = [f for f in os.listdir('scraped_pages') if f.endswith('.md')]
        
        # Delete each file and its associated directory
        for filename in files:
            file_path = os.path.join('scraped_pages', filename)
            dir_path = os.path.splitext(file_path)[0]
            
            # Delete the markdown file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete the associated directory (which contains images)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        
        return jsonify({'success': True, 'message': 'All pages deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
