document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
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
    youtubeUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') fetchVideoInfo();
    });
    
    // Fetch video info
    async function fetchVideoInfo() {
        const url = youtubeUrl.value.trim();
        
        if (!url) return showError('Please enter a YouTube URL');
        if (!isValidYouTubeUrl(url)) return showError('Please enter a valid YouTube URL');
        
        showLoading();
        
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
            hideLoading();
        }
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
    
    showDownloadProgress();
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `url=${encodeURIComponent(url)}&format_id=${encodeURIComponent(formatId)}`
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Download failed');
        }
        
        // Get filename from content-disposition header
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'video.mp4';
        if (contentDisposition) {
            const matches = contentDisposition.match(/filename="?(.+?)"?$/);
            if (matches && matches[1]) {
                filename = matches[1];
            }
        }
        
        // Create download link
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        showSuccess('Download complete!');
    } catch (err) {
        showError(err.message);
    } finally {
        setTimeout(() => {
            downloadProgress.classList.add('d-none');
        }, 3000);
    }
}
    
    // Helper functions
    function isValidYouTubeUrl(url) {
        return /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/.test(url);
    }
    
    function displayVideoInfo(info) {
        document.getElementById('videoTitle').textContent = info.title;
        document.getElementById('videoUploader').textContent = `Uploaded by: ${info.uploader}`;
        document.getElementById('videoDuration').textContent = `Duration: ${info.duration}`;
        document.getElementById('videoViews').textContent = `Views: ${info.view_count.toLocaleString()}`;
        document.getElementById('videoThumbnail').src = info.thumbnail;
        
        const formatSelect = document.getElementById('formatSelect');
        formatSelect.innerHTML = '';
        
        info.formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.format_id;
            option.textContent = `${format.resolution || 'Audio'} (${format.ext.toUpperCase()}) - ${format.filesize}`;
            formatSelect.appendChild(option);
        });
        
        videoInfo.classList.remove('d-none');
    }
    
    function downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    function showLoading() {
        loadingSpinner.classList.remove('d-none');
        videoInfo.classList.add('d-none');
        errorMessage.classList.add('d-none');
    }
    
    function hideLoading() {
        loadingSpinner.classList.add('d-none');
    }
    
    function showDownloadProgress() {
        downloadProgress.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressText.textContent = 'Starting download...';
    }
    
    function updateProgress(percent) {
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `Downloading... ${percent}%`;
    }
    
    function showSuccess(message) {
        progressBar.style.width = '100%';
        progressBar.classList.remove('bg-danger');
        progressBar.classList.add('bg-success');
        progressText.textContent = message;
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        setTimeout(() => errorMessage.classList.add('d-none'), 5000);
    }
});
