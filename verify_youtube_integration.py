import videogrep.modules.youtube

if __name__ == "__main__":
    # Test with the specific video the user requested
    url = "https://youtu.be/ygQ7BObIj7M"
    print(f"Testing download with URL: {url}")
    
    try:
        # Using format '18' as it was verified to work manually for this specific video
        videogrep.modules.youtube.download_video(url, output_template="test_videogrep_%(ext)s", format_code="18")
        print("Download successful!")
    except Exception as e:
        print(f"Download failed: {e}")
