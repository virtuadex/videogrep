import os
import sys
import subprocess
import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .db import create_db_and_tables, get_session
from .models import Video, SearchResult
from .. import voxgrep, transcribe, search_engine
from ..config import ServerConfig, MEDIA_EXTENSIONS, DEFAULT_COMPUTE_TYPE, DEFAULT_SEARCH_TYPE
from ..utils import setup_logger, get_media_type, ensure_directory_exists

# Use ServerConfig defaults
config = ServerConfig()

# Setup logger
logger = setup_logger("voxgrep.server", level=config.log_level)

app = FastAPI(title="VoxGrep Service", version="0.2.1")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Auto-scan downloads folder on startup
    with Session(next(get_session())) as session:
        _scan_path(config.downloads_dir, session)
    logger.info(f"Database initialized and {config.downloads_dir} scanned.")

def _scan_path(path: str, session: Session) -> int:
    """Scans a path for media files and adds them to the database."""
    target_dir = ensure_directory_exists(path)
    count = 0
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in MEDIA_EXTENSIONS:
                full_path = os.path.join(root, file)
                # Check if already exists
                existing = session.exec(select(Video).where(Video.path == full_path)).first()
                if not existing:
                    try:
                        stats = os.stat(full_path)
                        transcript_path = search_engine.find_transcript(full_path)
                        video = Video(
                            path=full_path,
                            filename=file,
                            size_bytes=stats.st_size,
                            created_at=stats.st_mtime,
                            has_transcript=transcript_path is not None,
                            transcript_path=transcript_path
                        )
                        session.add(video)
                        count += 1
                    except OSError as e:
                        logger.error(f"Error accessing {full_path}: {e}")
                        
    session.commit()
    return count

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.2.1", "config": config.__dict__}

@app.get("/library", response_model=List[Video])
def get_library(session: Session = Depends(get_session)):
    """Returns a list of all videos in the library."""
    videos = session.exec(select(Video)).all()
    return videos

@app.post("/library/scan")
def scan_library(path: Optional[str] = None, session: Session = Depends(get_session)):
    """Scans a directory and adds new videos to the library."""
    target_path = path or config.downloads_dir
    added = _scan_path(target_path, session)
    return {"added": added, "path": target_path}

@app.post("/download")
def download_video(url: str, output_dir: Optional[str] = None, background_tasks: BackgroundTasks = None):
    """Placeholder for background video download logic."""
    # TODO: Implement proper background downloading with progress (yt-dlp)
    return {"status": "started", "message": "Downloader not yet implemented in service", "task_id": "TODO"}

@app.get("/search", response_model=List[SearchResult])
def search(
    query: str, 
    type: str = DEFAULT_SEARCH_TYPE, 
    threshold: float = 0.45, 
    session: Session = Depends(get_session)
):
    """Searches across all videos in the library."""
    videos = session.exec(select(Video)).all()
    files = [v.path for v in videos]
    
    if not files:
        return []

    try:
        segments = search_engine.search(files, query, type, threshold=threshold)
        results = []
        for s in segments:
            results.append(SearchResult(
                file=s["file"],
                start=s["start"],
                end=s["end"],
                content=s["content"],
                score=s.get("score")
            ))
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
def export_supercut(matches: List[SearchResult], output: str, background_tasks: BackgroundTasks):
    """Exports a supercut from the given search results."""
    composition = [m.dict() for m in matches]
    
    def run_export():
        try:
            voxgrep.voxgrep(composition, output)
            logger.info(f"Export completed: {output}")
        except Exception as e:
            logger.error(f"Background export failed: {e}")

    background_tasks.add_task(run_export)
    return {"status": "started", "path": output}

@app.post("/open_folder")
def open_folder(path: str):
    """Opens a file or directory in the system's file manager."""
    try:
        abs_path = os.path.abspath(path)
        if os.path.isfile(abs_path):
            abs_path = os.path.dirname(abs_path)
            
        if sys.platform == "darwin":
            subprocess.run(["open", abs_path])
        elif sys.platform == "win32":
            os.startfile(abs_path)
        else:
            subprocess.run(["xdg-open", abs_path])
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Open folder error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ngrams")
def get_ngrams(path: str, n: int = 1):
    """Returns n-grams for indexed videos in the given path."""
    files_to_search = []
    
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        for root, _, files in os.walk(abs_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in MEDIA_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    if search_engine.find_transcript(full_path):
                        files_to_search.append(full_path)
    else:
        if search_engine.find_transcript(abs_path):
            files_to_search = [abs_path]
            
    if not files_to_search:
        return []

    try:
        from collections import Counter
        grams = search_engine.get_ngrams(files_to_search, n)
        most_common = Counter(grams).most_common(100)
        
        results = []
        for ngram, count in most_common:
            results.append({"ngram": " ".join(ngram), "count": count})
            
        return results
    except Exception as e:
        logger.error(f"N-gram extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)
