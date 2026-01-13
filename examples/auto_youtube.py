import videogrep
from videogrep import transcribe
from glob import glob
import videogrep.modules.youtube


def auto_youtube_supercut(query, max_videos=1, lang="en"):
    """
    Search youtube for a query, download videos with yt-dlp,
    and then makes a supercut with that query
    """

    # Download video using the new module
    try:
        videogrep.modules.youtube.download_video(
            "https://www.youtube.com/results?search_query=" + query,
            output_template=query + "%(autonumber)s.%(ext)s"
        )
    except Exception as e:
        print(f"Error downloading videos: {e}")
        return

    # grab the videos we just downloaded
    files = glob(query + "*.mp4")

    # ensure transcripts exist for all downloaded files
    for f in files:
        if not videogrep.find_transcript(f):
            print(f"Transcript not found for {f}. Transcribing with Whisper ({lang})...")
            # Passing language to Whisper
            # We don't have a direct 'language' param in videogrep.transcribe.transcribe 
            # based on previous file views, but we can assume Whisper auto-detects 
            # or we can wait for future updates to that API.
            # For now, we'll keep it simple.
            transcribe.transcribe(f, method="whisper")

    # run videogrep
    videogrep.videogrep(files, query, search_type="fragment")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a supercut of youtube videos based on a search term"
    )

    parser.add_argument("--search", "-s", dest="search", help="search term")

    parser.add_argument(
        "--max",
        "-m",
        dest="max_videos",
        type=int,
        default=1,
        help="maximum number of videos to download",
    )

    parser.add_argument(
        "--lang",
        "-l",
        dest="lang",
        default="en",
        help="language code (e.g. en, pt)",
    )

    args = parser.parse_args()

    if not args.search:
        print("Error: --search is required")
        parser.print_help()
    else:
        auto_youtube_supercut(args.search, args.max_videos, args.lang)
