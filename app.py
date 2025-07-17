import os
import yt_dlp
import uuid
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import threading
import shutil

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ensure download folder exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def cleanup_downloads():
    """Clean up old download files"""
    try:
        for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    except Exception as e:
        print(f"Cleanup error: {e}")

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
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
                'note': f.get('format_note', ''),
            })
        
        return {
            'title': info['title'],
            'thumbnail': info['thumbnail'],
            'duration': info['duration_string'],
            'formats': formats,
            'uploader': info['uploader'],
            'view_count': info['view_count'],
        }

def download_video(url, format_id):
    """Download video with proper error handling"""
    unique_id = str(uuid.uuid4())
    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': download_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'retries': 3,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Verify file exists and has content
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Downloaded file not found at {filename}")
            if os.path.getsize(filename) == 0:
                raise ValueError("Downloaded file is empty")
                
            return filename
    except Exception as e:
        # Clean up if download failed
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)
        raise e

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']
    
    try:
        filepath = download_video(url, format_id)
        filename = secure_filename(os.path.basename(filepath))
        
        # Schedule cleanup after sending the file
        @after_this_request
        def cleanup(response):
            try:
                # Start cleanup in a separate thread
                thread = threading.Thread(target=cleanup_downloads)
                thread.start()
            except Exception as e:
                app.logger.error(f"Cleanup error: {e}")
            return response
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to download video. Please try another format.'
        }), 400

# ... (keep all other routes the same)
