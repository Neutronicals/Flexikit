document.addEventListener('DOMContentLoaded', function() {
    const getInfoBtn = document.getElementById('getInfoBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const youtubeUrl = document.getElementById('youtubeUrl');
    const videoInfo = document.getElementById('videoInfo');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const downloadProgress = document.getElementById('downloadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    // Event listeners
    getInfoBtn.addEventListener('click', fetchVideoInfo);
    downloadBtn.addEventListener('click', downloadVideo);
    
    // Also trigger on Enter key
    youtubeUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchVideoInfo();
        }
    });
    
    // Fetch video info from backend
    async function fetchVideoInfo() {
        const url = youtubeUrl.value.trim();
        
        if (!url) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        // Validate URL (simple check)
        if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
            showError('Please enter a valid YouTube URL');
            return;
        }
        
        // Show loading spinner
        loadingSpinner.classList.remove('d-none');
        videoInfo.classList.add('d-none');
        errorMessage.classList.add('d-none');
        
        try {
            const response = await fetch('/get_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayVideoInfo(data.info);
            } else {
                showError(data.error || 'Failed to fetch video info');
            }
        } catch (err) {
            showError('Network error. Please try again.');
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    }
    
    // Display video info
    function displayVideoInfo(info) {
        document.getElementById('videoTitle').textContent = info.title;
        document.getElementById('videoUploader').textContent = `Uploaded by: ${info.uploader}`;
        document.getElementById('videoDuration').textContent = `Duration: ${info.duration}`;
        document.getElementById('videoViews').textContent = `Views: ${info.view_count.toLocaleString()}`;
        document.getElementById('videoThumbnail').src = info.thumbnail;
        
        // Populate format select
        const formatSelect = document.getElementById('formatSelect');
        formatSelect.innerHTML = '';
        
        info.formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.format_id;
            option.textContent = `${format.resolution} (${format.ext.toUpperCase()}) - ${format.filesize}`;
            formatSelect.appendChild(option);
        });
        
        // Show video info
        videoInfo.classList.remove('d-none');
    }
    
    // Download video
    async function downloadVideo() {
        const url = youtubeUrl.value.trim();
        const formatSelect = document.getElementById('formatSelect');
        const formatId = formatSelect.value;
        
        if (!url || !formatId) {
            showError('Please select a format to download');
            return;
        }
        
        // Show download progress
        downloadProgress.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressText.textContent = 'Starting download...';
        
        try {
            // First we need to initiate the download on the server
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}&format_id=${encodeURIComponent(formatId)}`
            });
            
            if (!response.ok) {
                throw new Error('Download failed');
            }
            
            // Get the filename from Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            const filename = contentDisposition 
                ? contentDisposition.split('filename=')[1].replace(/"/g, '')
                : 'video.mp4';
            
            // Create a blob from the response
            const reader = response.body.getReader();
            const contentLength = +response.headers.get('Content-Length');
            let receivedLength = 0;
            let chunks = [];
            
            while(true) {
                const {done, value} = await reader.read();
                
                if (done) break;
                
                chunks.push(value);
                receivedLength += value.length;
                
                // Update progress
                const percent = Math.round((receivedLength / contentLength) * 100);
                progressBar.style.width = `${percent}%`;
                progressText.textContent = `Downloading... ${percent}%`;
                
                // Simulate some delay to show progress (remove in production)
                await new Promise(resolve => setTimeout(resolve, 50));
            }
            
            // Combine chunks
            const blob = new Blob(chunks);
            
            // Create download link
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);
                progressText.textContent = 'Download complete!';
            }, 100);
            
        } catch (err) {
            showError(err.message || 'Download failed');
            downloadProgress.classList.add('d-none');
        }
    }
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorMessage.classList.add('d-none');
        }, 5000);
    }
});
