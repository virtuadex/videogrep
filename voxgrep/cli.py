import argparse
import logging
from tqdm import tqdm
from collections import Counter

from . import sphinx, voxgrep, vocab, __version__
from .search_engine import get_ngrams
from .config import (
    DEFAULT_WHISPER_MODEL,
    DEFAULT_DEVICE,
    DEFAULT_COMPUTE_TYPE,
    DEFAULT_SEARCH_TYPE
)
from .utils import setup_logger

# Initialize logger with simple format for CLI
logger = setup_logger("voxgrep.cli", level="INFO")


def main():
    """
    Run the command line version of VoxGrep
    """

    parser = argparse.ArgumentParser(
        description='Generate a "supercut" of one or more video files by searching through subtitle tracks.'
    )
    
    # Input/Output
    io_group = parser.add_argument_group("Input/Output Options")
    io_group.add_argument(
        "--input", "-i",
        dest="inputfile",
        nargs="*",
        required=True,
        help="video file or files",
    )
    io_group.add_argument(
        "--output", "-o",
        dest="outputfile",
        default="supercut.mp4",
        help="name of output file",
    )
    io_group.add_argument(
        "--export-clips", "-ec",
        dest="export_clips",
        action="store_true",
        help="Export individual clips instead of concatenating",
    )
    io_group.add_argument(
        "--export-vtt", "-ev",
        dest="write_vtt",
        action="store_true",
        help="Write a WebVTT file next to the output",
    )

    # Search
    search_group = parser.add_argument_group("Search Options")
    search_group.add_argument(
        "--search", "-s",
        dest="search",
        action="append",
        help="Search term (use multiple times for multiple queries)",
    )
    search_group.add_argument(
        "--search-type", "-st",
        dest="searchtype",
        default=DEFAULT_SEARCH_TYPE,
        choices=["sentence", "fragment", "mash", "semantic"],
        help=f"Type of search. Default: {DEFAULT_SEARCH_TYPE}",
    )
    search_group.add_argument(
        "--max-clips", "-m",
        dest="maxclips",
        type=int,
        default=0,
        help="Maximum number of clips to use",
    )
    search_group.add_argument(
        "--randomize", "-r",
        action="store_true",
        help="Randomize the clip order",
    )

    # Audio/Video processing
    proc_group = parser.add_argument_group("Processing Options")
    proc_group.add_argument(
        "--padding", "-p",
        dest="padding",
        type=float,
        help="Padding in seconds at start and end of each clip",
    )
    proc_group.add_argument(
        "--resyncsubs", "-rs",
        dest="sync",
        default=0,
        type=float,
        help="Subtitle re-sync delay +/- in seconds",
    )

    # Transcription
    trans_group = parser.add_argument_group("Transcription Options")
    trans_group.add_argument(
        "--transcribe", "-tr",
        dest="transcribe",
        action="store_true",
        help="Transcribe the video using Whisper",
    )
    trans_group.add_argument(
        "--model", "-mo",
        dest="model",
        help=f"Whisper model name. Default: {DEFAULT_WHISPER_MODEL}",
    )
    trans_group.add_argument(
        "--device", "-dev",
        dest="device",
        default=DEFAULT_DEVICE,
        help=f"Device to use for transcription (cpu, cuda, mlx). Default: {DEFAULT_DEVICE}",
    )
    trans_group.add_argument(
        "--compute-type", "-ct",
        dest="compute_type",
        default=DEFAULT_COMPUTE_TYPE,
        help=f"Compute type for transcription. Default: {DEFAULT_COMPUTE_TYPE}",
    )
    trans_group.add_argument(
        "--language", "-l",
        dest="language",
        help="Language of the video (Whisper only)",
    )
    trans_group.add_argument(
        "--initial-prompt", "-ip",
        dest="prompt",
        help="Initial prompt to guide transcription (Whisper only)",
    )
    trans_group.add_argument(
        "--sphinx-transcribe", "-str",
        dest="sphinxtranscribe",
        action="store_true",
        help="Transcribe using pocketsphinx (must be installed)",
    )

    # Advanced
    adv_group = parser.add_argument_group("Advanced Options")
    adv_group.add_argument(
        "--ngrams", "-n",
        dest="ngrams",
        type=int,
        default=0,
        help="Return n-grams for the input videos",
    )
    adv_group.add_argument(
        "--preview", "-pr",
        action="store_true",
        help="Preview results in mpv (must be installed)",
    )
    adv_group.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Show results without creating a supercut",
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"VoxGrep {__version__}",
    )

    args = parser.parse_args()

    # Handle n-grams mode
    if args.ngrams > 0:
        grams = get_ngrams(args.inputfile, args.ngrams)
        most_common = Counter(grams).most_common(100)
        for ngram, count in most_common:
            print(" ".join(ngram), count)
        return True

    # Handle transcription
    if args.sphinxtranscribe:
        for f in tqdm(args.inputfile, desc="Transcribing files (Sphinx)", unit="file", disable=len(args.inputfile) < 2):
            sphinx.transcribe(f)
        if not args.search:
            return True

    if args.transcribe:
        from . import transcribe
        for f in tqdm(args.inputfile, desc="Transcribing files (Whisper)", unit="file", disable=len(args.inputfile) < 2):
            transcribe.transcribe(
                f, 
                model_name=args.model, 
                prompt=args.prompt, 
                language=args.language, 
                device=args.device, 
                compute_type=args.compute_type
            )
        if not args.search:
            return True

    # Validate search
    if args.search is None:
        parser.error("argument --search/-s is required unless only transcribing")

    # Execute voxgrep
    voxgrep.voxgrep(
        files=args.inputfile,
        query=args.search,
        search_type=args.searchtype,
        output=args.outputfile,
        maxclips=args.maxclips,
        padding=args.padding,
        demo=args.demo,
        random_order=args.randomize,
        resync=args.sync,
        export_clips=args.export_clips,
        write_vtt=args.write_vtt,
        preview=args.preview,
    )


if __name__ == "__main__":
    main()
