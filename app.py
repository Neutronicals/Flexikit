from flask import Flask, render_template, request, send_file, jsonify, after_this_request
import os
import yt_dlp
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'

# Ensure download folder exists
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

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
    unique_id = str(uuid.uuid4())
    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f'{unique_id}.%(ext)s')
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': download_path,
        'quiet': True,
        'progress_hooks': [lambda d: print(d['status'])],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
    return filename

@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/get_info', methods=['POST'])
def get_info():
    url = request.form['url']
    try:
        info = get_video_info(url)
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_id = request.form['format_id']
    
    try:
        filepath = download_video(url, format_id)
        
        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
            except Exception as e:
                app.logger.error(f"Error removing file {filepath}: {e}")
            return response
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
