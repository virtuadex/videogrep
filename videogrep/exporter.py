import os
import sys
import time
import logging
import gc
from tqdm import tqdm
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

from . import fcpxml, vtt

logger = logging.getLogger(__name__)

BATCH_SIZE = 20

def get_file_type(filename: str):
    """
    Get filetype ('audio', 'video', 'text', etc...) for filename based on the
    IANA Media Type, aka MIME type.
    """
    import mimetypes
    mimetypes.init()
    ftype = mimetypes.guess_type(filename)[0]

    if ftype != None:
        filetype = ftype.split("/")[0]
        return filetype

    return "unknown"


def get_input_type(composition):
    filenames = set([c["file"] for c in composition])
    types = []

    for f in filenames:
        type = get_file_type(f)
        types.append(type)

    if "audio" in types:
        input_type = "audio"
    else:
        input_type = "video"

    return input_type


def plan_no_action(composition, outputfile: str):
    input_type = get_input_type(composition)
    output_type = get_file_type(outputfile)

    if (
        (input_type == "audio")
        and (output_type == "video")
        and (outputfile != "supercut.mp4")
    ):
        return True
    else:
        return False


def plan_video_output(composition, outputfile: str):
    input_type = get_input_type(composition)
    output_type = get_file_type(outputfile)

    if (input_type == "video") and (output_type != "audio"):
        return True
    else:
        return False


def plan_audio_output(composition, outputfile: str):
    input_type = get_input_type(composition)
    output_type = get_file_type(outputfile)

    if (input_type == "audio") or (output_type == "audio"):
        return True
    else:
        return False

def cleanup_log_files(outputfile: str):
    """Search for and remove temp log files found in the output directory."""
    d = os.path.dirname(os.path.abspath(outputfile))
    if os.path.exists(d):
        logfiles = [f for f in os.listdir(d) if f.endswith("ogg.log")]
        for f in logfiles:
            os.remove(os.path.join(d, f))


def create_supercut(composition, outputfile: str):
    all_filenames = set([c["file"] for c in composition])

    if plan_no_action(composition, outputfile):
        logger.error("Videogrep is not able to convert audio input to video output.")
        logger.error("Try using an audio output instead, like 'supercut.mp3'.")
        sys.exit("Exiting...")
    elif plan_video_output(composition, outputfile):
        logger.info("[+] Creating clips.")
        videofileclips = dict([(f, VideoFileClip(f)) for f in all_filenames])
        cut_clips = []
        for c in tqdm(composition, desc="Creating video clips", unit="clip"):
            if c["start"] < 0:
                c["start"] = 0
            # Warning: videofileclips[c['file']].duration might be expensive or lazy
            # We assume user has files openable by moviepy
            if c["end"] > videofileclips[c["file"]].duration:
                c["end"] = videofileclips[c["file"]].duration
            cut_clips.append(videofileclips[c["file"]].subclipped(c["start"], c["end"]))

        logger.info("[+] Concatenating clips.")
        final_clip = concatenate_videoclips(cut_clips, method="compose")

        logger.info("[+] Writing ouput file.")
        final_clip.write_videofile(
            outputfile,
            codec="libx264",
            bitrate="8000k",
            audio_bitrate="192k",
            preset="medium",
            temp_audiofile=f"{outputfile}_temp-audio{time.time()}.m4a",
            remove_temp=True,
            audio_codec="aac",
        )
    elif plan_audio_output(composition, outputfile):
        logger.info("[+] Creating clips.")
        audiofileclips = dict([(f, AudioFileClip(f)) for f in all_filenames])
        cut_clips = []

        for c in tqdm(composition, desc="Creating audio clips", unit="clip"):
            if c["start"] < 0:
                c["start"] = 0
            if c["end"] > audiofileclips[c["file"]].duration:
                c["end"] = audiofileclips[c["file"]].duration
            cut_clips.append(audiofileclips[c["file"]].subclipped(c["start"], c["end"]))

        logger.info("[+] Concatenating clips.")
        final_clip = concatenate_audioclips(cut_clips)

        logger.info("[+] Writing output file.")
        if outputfile == "supercut.mp4":
            outputfile = "supercut.mp3"

        final_clip.write_audiofile(outputfile)


def create_supercut_in_batches(composition, outputfile: str):
    total_clips = len(composition)
    start_index = 0
    end_index = BATCH_SIZE
    batch_comp = []

    if plan_no_action(composition, outputfile):
        logger.error("Videogrep is not able to convert audio input to video output.")
        logger.error("Try using an audio output instead, like 'supercut.mp3'.")
        sys.exit("Exiting...")
    elif plan_video_output(composition, outputfile):
        file_ext = ".mp4"
    elif plan_audio_output(composition, outputfile):
        file_ext = ".mp3"
        if outputfile == "supercut.mp4":
            outputfile = "supercut.mp3"

    num_batches = (total_clips + BATCH_SIZE - 1) // BATCH_SIZE
    pbar = tqdm(total=num_batches, desc="Processing batches", unit="batch")

    while start_index < total_clips:
        filename = outputfile + ".tmp" + str(start_index) + file_ext
        try:
            create_supercut(composition[start_index:end_index], filename)
            batch_comp.append(filename)
            gc.collect()
            start_index += BATCH_SIZE
            end_index += BATCH_SIZE
            pbar.update(1)
        except Exception as e:
            logger.error(f"Error processing batch starting at {start_index}: {e}")
            start_index += BATCH_SIZE
            end_index += BATCH_SIZE
            pbar.update(1)
            continue
    pbar.close()

    if plan_video_output(composition, outputfile):
        clips = [VideoFileClip(filename) for filename in batch_comp]
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(
            outputfile,
            codec="libx264",
            bitrate="8000k",
            audio_bitrate="192k",
            preset="medium",
            temp_audiofile=f"{outputfile}_temp-audio{time.time()}.m4a",
            remove_temp=True,
            audio_codec="aac",
        )
    elif plan_audio_output(composition, outputfile):
        clips = [AudioFileClip(filename) for filename in batch_comp]
        audio = concatenate_audioclips(clips)
        audio.write_audiofile(outputfile)

    # remove partial video files
    for filename in batch_comp:
        os.remove(filename)

    cleanup_log_files(outputfile)


def export_individual_clips(composition, outputfile: str):
    all_filenames = set([c["file"] for c in composition])

    if plan_no_action(composition, outputfile):
        logger.error("Videogrep is not able to convert audio input to video output.")
        logger.error("Try using an audio output instead, like 'supercut.mp3'.")
        sys.exit("Exiting...")
    elif plan_video_output(composition, outputfile):
        videofileclips = dict([(f, VideoFileClip(f)) for f in all_filenames])
        cut_clips = []
        for c in composition:
            if c["start"] < 0:
                c["start"] = 0
            if c["end"] > videofileclips[c["file"]].duration:
                c["end"] = videofileclips[c["file"]].duration
            cut_clips.append(videofileclips[c["file"]].subclipped(c["start"], c["end"]))

        basename, ext = os.path.splitext(outputfile)
        logger.info("[+] Writing output files.")
        for i, clip in enumerate(tqdm(cut_clips, desc="Exporting video clips", unit="clip")):
            clipfilename = basename + "_" + str(i).zfill(5) + ext
            clip.write_videofile(
                clipfilename,
                codec="libx264",
                bitrate="8000k",
                audio_bitrate="192k",
                preset="medium",
                temp_audiofile="{clipfilename}_temp-audio.m4a",
                remove_temp=True,
                audio_codec="aac",
            )
    elif plan_audio_output(composition, outputfile):
        audiofileclips = dict([(f, AudioFileClip(f)) for f in all_filenames])
        cut_clips = []

        for c in composition:
            if c["start"] < 0:
                c["start"] = 0
            if c["end"] > audiofileclips[c["file"]].duration:
                c["end"] = audiofileclips[c["file"]].duration
            cut_clips.append(audiofileclips[c["file"]].subclipped(c["start"], c["end"]))

        if outputfile == "supercut.mp4":
            outputfile = "supercut.mp3"

        basename, ext = os.path.splitext(outputfile)
        logger.info("[+] Writing output files.")
        for i, clip in enumerate(tqdm(cut_clips, desc="Exporting video clips", unit="clip")):
            clipfilename = basename + "_" + str(i).zfill(5) + ext
            clip.write_audiofile(clipfilename)


def export_m3u(composition, outputfile: str):
    lines = []
    lines.append("#EXTM3U")
    for c in composition:
        lines.append(f"#EXTINF:")
        lines.append(f"#EXTVLCOPT:start-time={c['start']}")
        lines.append(f"#EXTVLCOPT:stop-time={c['end']}")
        lines.append(c["file"])

    with open(outputfile, "w") as outfile:
        outfile.write("\n".join(lines))


def export_mpv_edl(composition, outputfile: str):
    lines = []
    lines.append("# mpv EDL v0")
    for c in composition:
        lines.append(f"{os.path.abspath(c['file'])},{c['start']},{c['end']-c['start']}")

    with open(outputfile, "w") as outfile:
        outfile.write("\n".join(lines))


def export_xml(composition, outputfile: str):
    fcpxml.compose(composition, outputfile)
