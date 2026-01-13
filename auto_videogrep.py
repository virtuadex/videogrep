import argparse
import os
import subprocess
import sys
from pathlib import Path

def run_whisper(video_path, model="medium"):
    """
    Runs OpenAI Whisper on the video file to generate an SRT file.
    """
    print(f"[+] Transcribing '{video_path}' using Whisper (model: {model})...")
    print("[+] This may take a while depending on your GPU and video length.")
    
    # Whisper command to output SRT directly to the same directory
    output_dir = os.path.dirname(os.path.abspath(video_path))
    
    try:
        subprocess.run(
            [
                "whisper",
                video_path,
                "--model", model,
                "--output_format", "srt",
                "--output_dir", output_dir,
                "--verbose", "False"
            ],
            check=True
        )
        print("[+] Transcription complete.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error running Whisper: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("[-] 'whisper' command not found. Please ensure openai-whisper is installed.")
        print("[-] Try running: pip install openai-whisper")
        sys.exit(1)

def run_videogrep(video_path, query, search_type="sentence", output_file="supercut.mp4"):
    """
    Runs videogrep using the generated SRT file.
    """
    print(f"[+] Running videogrep for query: '{query}'...")
    
    try:
        cmd = [
            "videogrep",
            "--input", video_path,
            "--search", query,
            "--search-type", search_type,
            "--output", output_file
        ]
        
        print(f"[+] Executing: {' '.join(cmd)}")
        
        subprocess.run(cmd, check=True)
        print(f"[+] Supercut created: {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"[-] Error running videogrep: {e}")

def main():
    parser = argparse.ArgumentParser(description="Auto-transcribe with Whisper and run Videogrep.")
    parser.add_argument("video", help="Path to the video file.")
    parser.add_argument("query", help="Search query (regex supported).")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny, base, small, medium, large). Default: medium.")
    parser.add_argument("--search-type", default="sentence", choices=["sentence", "fragment"], help="Videogrep search type. Default: sentence.")
    parser.add_argument("--output", help="Output filename. If not provided, defaults to virtuacuts_[video_name].mp4")
    parser.add_argument("--force-transcribe", action="store_true", help="Force re-transcription even if SRT exists.")

    args = parser.parse_args()
    
    video_path = args.video
    if not os.path.exists(video_path):
        print(f"[-] Video file not found: {video_path}")
        sys.exit(1)

    # Determine default output filename based on video name
    if not args.output:
        base_video_name = os.path.basename(video_path)
        video_name_no_ext = os.path.splitext(base_video_name)[0]
        output_file = f"virtuacuts_{video_name_no_ext}.mp4"
    else:
        output_file = args.output

    # Check for existing SRT
    base_name = os.path.splitext(video_path)[0]
    srt_path = base_name + ".srt"
    
    if os.path.exists(srt_path) and not args.force_transcribe:
        print(f"[+] Found existing subtitle file: {srt_path}")
        print("[+] Skipping transcription (use --force-transcribe to override).")
    else:
        run_whisper(video_path, args.model)
        
    # Run videogrep
    run_videogrep(video_path, args.query, args.search_type, output_file)

if __name__ == "__main__":
    main()
