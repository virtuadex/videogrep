import logging
import yt_dlp
from tqdm import tqdm

logger = logging.getLogger(__name__)

def download_video(
    url: str, 
    output_template: str = "%(title)s.%(ext)s", 
    format_code: str = None,
    progress_hooks: list = None,
    restrict_filenames: bool = True
) -> str:
    """
    Download a video (and subtitles) from a URL using yt-dlp.
    
    Args:
        url (str): The URL of the video to download.
        output_template (str): The output filename template. 
                               Default is "%(title)s.%(ext)s".
        format_code (str): The format code to use (optional). 
                           Defaults to robust logic.
        progress_hooks (list): Optional list of callback functions for progress updates.
        restrict_filenames (bool): Restrict filenames to ASCII characters (default: True).
                               
    Returns:
        str: The filename of the downloaded video.
    """
    # Configure yt-dlp options
    ydl_opts = {
        'format': format_code if format_code else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'pt'], # prioritize english and portuguese
        'ignoreerrors': True,  # Don't fail if subtitles can't be downloaded
        'quiet': True,
        'noprogress': True,
        'no_warnings': True,
        'restrictfilenames': False,
    }
    
    pbar = None
    
    def tqdm_hook(d):
        nonlocal pbar
        if d['status'] == 'downloading':
            if pbar is None:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                pbar = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading")
            
            downloaded = d.get('downloaded_bytes', 0)
            if pbar:
                pbar.update(downloaded - pbar.n)
        
        elif d['status'] == 'finished':
            if pbar:
                pbar.close()
                pbar = None

    if progress_hooks:
        ydl_opts['progress_hooks'] = progress_hooks
    else:
        ydl_opts['progress_hooks'] = [tqdm_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info first to get the filename
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            logger.info(f"Successfully downloaded: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise
        finally:
            if pbar:
                pbar.close()
