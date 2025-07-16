## Flexikit - YouTube Video Downloader

Flexikit is a modern, sleek YouTube video downloader web application that allows users to download videos in various formats and resolutions. Built with Python (Flask), HTML, CSS, JavaScript, and Bootstrap 5, it provides a user-friendly interface for downloading YouTube content.

## Features

- 🎥 Download YouTube videos in multiple formats
- 🖼️ Automatic video thumbnail and info display
- 📱 Responsive design works on all devices
- ⚡ Fast downloads with progress tracking
- 🔍 Video quality/format selection
- ❓ FAQ section for common questions
- 🎨 Stylish gradient dark theme with animations

## Technologies Used

**Backend:**
- Python 3
- Flask (web framework)
- yt-dlp (YouTube downloader)
- FFmpeg (video processing)

**Frontend:**
- HTML5
- CSS3 (with custom animations)
- JavaScript (ES6)
- Bootstrap 5
- Font Awesome (icons)

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Git (optional)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flexikit.git
cd flexikit
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure FFmpeg is installed:
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/)
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

5. Run the application:
```bash
python app.py
```

6. Open your browser and visit:
```
http://localhost:5000
```

## Deployment

Flexikit can be deployed to various cloud platforms. Here are instructions for some popular options:

### Render.com (Recommended)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add environment variable if needed: `PYTHON_VERSION=3.9`

### PythonAnywhere
1. Create a free account
2. Upload your files or clone from GitHub
3. Create a new web app (Flask)
4. Configure WSGI file to point to your app
5. Reload the web app

### Vercel
1. Install Vercel CLI: `npm install -g vercel`
2. Run `vercel` in project directory
3. Configure as Python project
4. May need to adjust configuration for Flask

## Usage

1. Enter a YouTube URL in the input field
2. Click "Get Info" to fetch video details
3. Select your preferred format/quality
4. Click "Download" to start downloading
5. The video will download directly to your device

## FAQ

**Is Flexikit free to use?**  
Yes! Flexikit is completely free with no hidden charges.

**What video formats are supported?**  
Flexikit supports MP4, WebM, 3GP and many other formats at various resolutions.

**Is it legal to download YouTube videos?**  
Downloading videos is against YouTube's Terms of Service. Flexikit is intended for personal use of content you have rights to. Please respect copyright laws.

## Screenshots

![Main Screen](static/screenshots/main.png)
*Flexikit main interface*

![Video Info](static/screenshots/info.png)
*Video information display*

![Download Progress](static/screenshots/progress.png)
*Download progress tracking*

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Flexikit is for educational purposes only. The developers are not responsible for how users utilize this tool. Please respect YouTube's Terms of Service and only download content you have rights to.

---

© 2025 Flexikit | [Terms of Service](TERMS.md) | [Privacy Policy](PRIVACY.md)
