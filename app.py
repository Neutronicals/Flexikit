import os
import yt_dlp
import uuid
from flask import Flask, render_template, request, Response, jsonify, stream_with_context
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from waitress import serve
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['DOWNLOAD_FOLDER'] = 'static/downloads/'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

class VideoDownloader:
    @staticmethod
    def get_info(url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'age_limit': 99,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
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
                    'title': info.get('title', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration_string', ''),
                    'formats': formats,
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                }
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    @staticmethod
    def get_format_ext(url, format_id):
        # Helper to extract extension for the selected format
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'age_limit': 99,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                for f in info['formats']:
                    if f['format_id'] == format_id:
                        return f['ext']
        except Exception as e:
            logger.error(f"Error getting video format ext: {str(e)}")
        return 'mp4'  # fallback

def generate_ytdlp_stream(url, format_id):
    # Get extension for the right mimetype/filename
    ext = VideoDownloader.get_format_ext(url, format_id)
    filename = f"video.{ext}"
    # Start yt-dlp process to stream to stdout
    ytdlp_cmd = [
        "yt-dlp", "-f", format_id, "-o", "-", url
    ]
    process = subprocess.Popen(ytdlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        while True:
            chunk = process.stdout.read(8192)
            if not chunk:
                break
            yield chunk
    finally:
        process.stdout.close()
        process.stderr.close()
        process.terminate()

@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/get_info', methods=['POST'])
def get_video_info():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400
    try:
        info = VideoDownloader.get_info(url)
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    format_id = request.form.get('format_id', '').strip()
    if not url or not format_id:
        return jsonify({'success': False, 'error': 'URL and format are required'}), 400

    # Get extension for mimetype/filename
    ext = VideoDownloader.get_format_ext(url, format_id)
    filename = secure_filename(f"video.{ext}")
    mimetype = f"video/{ext}" if ext != "unknown" else "application/octet-stream"

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': mimetype
    }

    return Response(
        stream_with_context(generate_ytdlp_stream(url, format_id)),
        headers=headers
    )

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    serve(app, host='0.0.0.0', port=port)
