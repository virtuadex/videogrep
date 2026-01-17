import videogrep
from videogrep import transcribe
from glob import glob
import videogrep.modules.youtube


def auto_youtube_supercut(search_query, url=None, max_videos=1, lang="en", padding=0.5, output="supercut.mp4"):
    """
    Search youtube for a query or use a direct URL, download videos with yt-dlp,
    and then makes a supercut with that query
    """

    if url:
        # If a URL is provided, we use it directly
        prefix = "yt_download"
    else:
        # Otherwise search for the query
        url = "https://www.youtube.com/results?search_query=" + search_query
        prefix = "".join([c if c.isalnum() else "_" for c in search_query])

    # Download video using the new module
    try:
        videogrep.modules.youtube.download_video(
            url,
            output_template=prefix + "%(autonumber)s.%(ext)s"
        )
    except Exception as e:
        print(f"Error downloading videos: {e}")
        return

    # grab the videos we just downloaded
    files = glob(prefix + "*.mp4")

    if not files:
        print("No videos downloaded.")
        return

    # ensure transcripts exist for all downloaded files
    for f in files:
        if not videogrep.find_transcript(f):
            print(f"Transcript not found for {f}. Transcribing with Whisper ({lang})...")
            transcribe.transcribe(f, method="whisper", language=lang)

    # run videogrep
    print(f"Creating supercut for query: {search_query} (padding: {padding}s)")
    videogrep.videogrep(files, search_query, search_type="fragment", padding=padding, output=output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a supercut of youtube videos based on a search term"
    )

    parser.add_argument("--search", "-s", dest="search", help="search term")
    parser.add_argument("--url", "-u", dest="url", help="direct youtube url (optional)")

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

    parser.add_argument(
        "--padding",
        "-p",
        dest="padding",
        type=float,
        default=0.5,
        help="padding in seconds around each clip (default: 0.5)",
    )

    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        default="youtube_supercut.mp4",
        help="output filename (default: youtube_supercut.mp4)",
    )

    args = parser.parse_args()

    if not args.search and not args.url:
        print("Error: Either --search or --url is required")
        parser.print_help()
    else:
        # If only URL is provided, use a default search term or ask for one
        query = args.search if args.search else "." # "." matches everything in regex
        auto_youtube_supercut(query, args.url, args.max_videos, args.lang, args.padding, args.output)
