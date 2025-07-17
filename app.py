import os
import yt_dlp
import uuid
from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from waitress import serve

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ensure download folder exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

class VideoDownloader:
    @staticmethod
    def get_info(url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = []
                
                for f in info['formats']:
                    if f.get('filesize'):
                        size_mb = f['filesize'] / (1024 * 1024)
                    else:
                        size_mb = 'Unknown'
                        
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'resolution': f.get('resolution', 'audio'),
                        'filesize': f"{size_mb:.2f} MB" if isinstance(size_mb, float) else size_mb,
                    })
                
                return {
                    'title': info['title'],
                    'thumbnail': info['thumbnail'],
                    'duration': info['duration_string'],
                    'formats': formats,
                    'uploader': info['uploader'],
                }
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    @staticmethod
    def download(url, format_id):
        unique_id = str(uuid.uuid4())
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')
        
        ydl_opts = {
            'format': format_id,
            'outtmpl': download_path,
            'quiet': True,
            'retries': 3,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    raise FileNotFoundError(f"Downloaded file not found at {filename}")
                
                return filename
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)
            raise

@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/get_info', methods=['POST'])
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        # Add these options to handle restricted videos
        'age_limit': 99,  # Bypass age restriction
        'geo_bypass': True,  # Bypass geographic restrictions
        'geo_bypass_country': 'US',  # Set to your preferred country
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Rest of your code...
    except yt_dlp.utils.DownloadError as e:
        if 'Video unavailable' in str(e):
            raise Exception("This video is unavailable. It may be private, age-restricted, or blocked in your country.")
            
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    format_id = request.form.get('format_id', '').strip()
    
    if not url or not format_id:
        return jsonify({'success': False, 'error': 'URL and format are required'}), 400
    
    try:
        filepath = VideoDownloader.download(url, format_id)
        filename = secure_filename(os.path.basename(filepath))
        
        response = send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
        # Schedule file cleanup after response is sent
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
        
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    serve(app, host='0.0.0.0', port=port)
