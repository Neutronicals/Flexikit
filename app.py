import os
import yt_dlp
import uuid
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Ensure download folder exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def get_video_info(url):
    """Fetch video info from YouTube"""
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
    """Download video in selected format"""
    unique_id = str(uuid.uuid4())
    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': download_path,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
    return filename

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/get_info', methods=['POST'])
def get_info():
    """API endpoint to get video info"""
    url = request.form['url']
    try:
        info = get_video_info(url)
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    """API endpoint to download video"""
    url = request.form['url']
    format_id = request.form['format_id']
    
    try:
        filepath = download_video(url, format_id)
        filename = secure_filename(os.path.basename(filepath))
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
