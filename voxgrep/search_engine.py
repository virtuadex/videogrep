import os
import re
import json
import random
from pathlib import Path
from typing import Optional, List, Union, Iterator
from tqdm import tqdm

import numpy as np
try:
    from sentence_transformers import SentenceTransformer, util
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

from . import vtt, srt, sphinx
from .config import (
    SUBTITLE_EXTENSIONS,
    DEFAULT_SEMANTIC_MODEL,
    DEFAULT_SEMANTIC_THRESHOLD,
    get_cache_dir
)
from .utils import setup_logger, ensure_list
from .exceptions import (
    TranscriptNotFoundError,
    SemanticSearchNotAvailableError,
    InvalidSearchTypeError
)

logger = setup_logger(__name__)

# Legacy constant for backwards compatibility
SUB_EXTS = SUBTITLE_EXTENSIONS

class SemanticModel:
    """Singleton class for managing the semantic search model."""
    _instance = None

    @classmethod
    def get_instance(cls, model_name: Optional[str] = None):
        """Get or create the semantic model instance."""
        if cls._instance is None:
            if not SEMANTIC_AVAILABLE:
                raise SemanticSearchNotAvailableError(
                    "sentence-transformers is not installed. "
                    "Install with 'pip install sentence-transformers'"
                )
            model_name = model_name or DEFAULT_SEMANTIC_MODEL
            logger.info(f"Loading semantic model: {model_name}")
            cls._instance = SentenceTransformer(model_name)
        return cls._instance


def find_transcript(videoname: str, prefer: Optional[str] = None) -> Optional[str]:
    """
    Find a transcript file for a given video file.
    
    Searches for subtitle/transcript files with the same base name as the video,
    trying various extensions and fuzzy matching strategies.
    
    Args:
        videoname: Path to the video file
        prefer: Preferred subtitle extension to try first (e.g., '.srt')
    
    Returns:
        Path to the transcript file if found, None otherwise
    """
    video_path = Path(videoname)
    if not video_path.parent.exists():
        return None
        
    _sub_exts = list(SUBTITLE_EXTENSIONS)
    if prefer is not None:
        _sub_exts = [prefer] + _sub_exts

    parent = video_path.parent
    name_stem = video_path.stem
    
    # Strategy 1: Exact match (video.mp4 -> video.srt)
    for ext in _sub_exts:
        candidate = video_path.with_suffix(ext)
        if candidate.exists():
            return candidate.as_posix()

    # Pre-list files once for efficiency
    try:
        all_files = list(parent.iterdir())
    except OSError:
        return None

    # Strategy 2: Fuzzy match for filenames with language codes (video.en.srt)
    for ext in _sub_exts:
        for f in all_files:
            if f.is_file() and f.name.startswith(name_stem) and f.suffix == ext:
                return f.as_posix()
            
    # Strategy 3: Legacy regex-based fallback for complex multi-part extensions
    for ext in _sub_exts:
        pattern = re.escape(name_stem) + r".*?\.?" + ext.replace(".", "")
        for f in all_files:
            if f.is_file() and re.search(pattern, f.name):
                return f.as_posix()

    return None


def parse_transcript(
    videoname: str, prefer: Optional[str] = None
) -> Optional[List[dict]]:
    """
    Parse a transcript file for a given video.
    
    Args:
        videoname: Path to the video file
        prefer: Preferred subtitle format to try first
    
    Returns:
        List of transcript segments with 'content', 'start', 'end' keys,
        and optionally 'words' for word-level timestamps
    """
    subfile = find_transcript(videoname, prefer)

    if subfile is None:
        logger.error(f"No subtitle file found for {videoname}")
        return None

    transcript = None

    try:
        with open(subfile, "r", encoding="utf8") as infile:
            if subfile.endswith(".srt"):
                transcript = srt.parse(infile)
            elif subfile.endswith(".vtt"):
                transcript = vtt.parse(infile)
            elif subfile.endswith(".json"):
                transcript = json.load(infile)
            elif subfile.endswith(".transcript"):
                transcript = sphinx.parse(infile)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, IndexError) as e:
        logger.error(f"Error parsing transcript file {subfile}: {e}")
        return None

    return transcript


def get_embeddings_path(videoname: str) -> str:
    """Get the path where embeddings for a video are cached."""
    return os.path.splitext(videoname)[0] + ".embeddings.npy"


def get_embeddings(videoname: str, transcript: List[dict], force: bool = False) -> np.ndarray:
    """
    Get or generate semantic embeddings for a transcript.
    
    Args:
        videoname: Path to the video file
        transcript: Parsed transcript data
        force: If True, regenerate embeddings even if cached
    
    Returns:
        NumPy array of embeddings
    """
    emb_path = get_embeddings_path(videoname)
    if os.path.exists(emb_path) and not force:
        logger.debug(f"Loading cached embeddings from {emb_path}")
        return np.load(emb_path)
    
    model = SemanticModel.get_instance()
    sentences = [line["content"] for line in transcript]
    logger.info(f"Generating embeddings for {videoname}...")
    embeddings = model.encode(sentences, show_progress_bar=False)
    np.save(emb_path, embeddings)
    return embeddings


def get_ngrams(files: Union[str, List[str]], n: int = 1) -> Iterator[tuple]:
    """
    Extract n-grams from transcript files.
    
    Args:
        files: Single file path or list of file paths
        n: Size of n-grams (1 for unigrams, 2 for bigrams, etc.)
    
    Returns:
        Iterator of n-gram tuples
    """
    files = ensure_list(files)
    words = []

    for file in files:
        transcript = parse_transcript(file)
        if transcript is None:
            continue
        for line in transcript:
            if "words" in line:
                words += [w["word"] for w in line["words"]]
            else:
                words += re.split(r"[.?!,:\"]+\s*|\s+", line["content"])

    ngrams = zip(*[words[i:] for i in range(n)])
    return ngrams


def search(
    files: Union[str, List[str]],
    query: Union[str, List[str]],
    search_type: str = "sentence",
    prefer: Optional[str] = None,
    threshold: float = DEFAULT_SEMANTIC_THRESHOLD,
    force_reindex: bool = False,
) -> List[dict]:
    """
    Search through video/audio files for a specific query.
    
    Args:
        files: Single file path or list of file paths
        query: Search query or list of queries
        search_type: Type of search ('sentence', 'fragment', 'mash', 'semantic')
        prefer: Preferred subtitle extension
        threshold: Similarity threshold for semantic search
        force_reindex: If True, force regeneration of embeddings for semantic search
        
    Returns:
        List of matching segments
    """
    files = ensure_list(files)
    query = ensure_list(query)
    all_segments = []

    if search_type == "mash":
        # For mash, we need to collect ALL words from ALL files first
        all_words = []
        for file in tqdm(files, desc="Indexing words for mash", unit="file", disable=len(files) < 2):
            transcript = parse_transcript(file, prefer=prefer)
            if transcript and len(transcript) > 0 and "words" in transcript[0]:
                for line in transcript:
                    for w in line["words"]:
                        w["file"] = file # Ensure we know which file the word came from
                        all_words.append(w)
        
        if not all_words:
            logger.error("Could not find word-level timestamps in any of the provided files.")
            return []

        for _query in query:
            queries = _query.split(" ")
            for q in queries:
                matches = [w for w in all_words if re.sub(r"[.?!,:\"]+", "", w["word"].lower()) == q.lower()]
                if len(matches) == 0:
                    logger.error(f"Could not find '{q}' in any transcript.")
                    continue 
                
                word = random.choice(matches)
                all_segments.append(
                    {
                        "file": word["file"],
                        "start": word["start"],
                        "end": word["end"],
                        "content": word["word"],
                    }
                )
        return all_segments

    if search_type == "semantic":
        if not SEMANTIC_AVAILABLE:
            raise SemanticSearchNotAvailableError(
                "Semantic search requires sentence-transformers. "
                "Install with 'pip install sentence-transformers'"
            )
        
        model = SemanticModel.get_instance()
        query_embeddings = model.encode(query, show_progress_bar=False)

        for file in tqdm(files, desc="Semantic search", unit="file", disable=len(files) < 2):
            transcript = parse_transcript(file, prefer=prefer)
            if not transcript:
                continue
            
            embeddings = get_embeddings(file, transcript, force=force_reindex)
            # util.cos_sim returns a matrix of shape [len(queries), len(sentences)]
            cos_scores = util.cos_sim(query_embeddings, embeddings)

            for i, _query in enumerate(query):
                scores = cos_scores[i]
                for j, score in enumerate(scores):
                    if score >= threshold:
                        all_segments.append({
                            "file": file,
                            "start": transcript[j]["start"],
                            "end": transcript[j]["end"],
                            "content": transcript[j]["content"],
                            "score": float(score)
                        })
        
        # Sort by score descending
        all_segments = sorted(all_segments, key=lambda k: k["score"], reverse=True)
        return all_segments

    # Standard regex/fragment search
    for file in tqdm(files, desc="Searching files", unit="file", disable=len(files) < 2):
        segments = []
        transcript = parse_transcript(file, prefer=prefer)
        if transcript is None:
            continue

        if search_type == "sentence":
            for line in transcript:
                for _query in query:
                    if re.search(_query, line["content"], re.IGNORECASE):
                        segments.append(
                            {
                                "file": file,
                                "start": line["start"],
                                "end": line["end"],
                                "content": line["content"],
                            }
                        )

        elif search_type == "fragment":
            if len(transcript) == 0 or "words" not in transcript[0]:
                logger.error(f"Could not find word-level timestamps for {file}")
                continue

            words = []
            for line in transcript:
                words += line["words"]

            for _query in query:
                queries = _query.split(" ")
                queries = [q.strip() for q in queries if q.strip() != ""]
                fragments = zip(*[words[i:] for i in range(len(queries))])
                for fragment in fragments:
                    found = all(
                        re.search(q, w["word"], re.IGNORECASE) for q, w in zip(queries, fragment)
                    )
                    if found:
                        phrase = " ".join([w["word"] for w in fragment])
                        segments.append(
                            {
                                "file": file,
                                "start": fragment[0]["start"],
                                "end": fragment[-1]["end"],
                                "content": phrase,
                            }
                        )
        else:
            raise InvalidSearchTypeError(f"Unsupported search type: {search_type}")

        segments = sorted(segments, key=lambda k: k["start"])
        all_segments += segments

    return all_segments
