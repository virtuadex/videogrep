import videogrep
import re
from collections import Counter
from pathlib import Path
from pytest import approx
import glob
import subprocess
import sys


def get_duration(input_video):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_video,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


def File(path):
    return str(Path(__file__).parent / Path(path))


def test_version():
    assert videogrep.__version__ == "2.3.1"


def test_srts():
    with open(File("test_inputs/metallica.srt"), encoding="utf-8") as infile:
        srt = infile.read()
    parsed = videogrep.srt.parse(srt)

    assert parsed[0]["content"].strip() == "Prometo ser o concerto desta noite no estádio de Alvalade, mas só para ouvidos duros."
    assert parsed[0]["start"] == approx(0.0)
    assert parsed[0]["end"] == approx(4.7)

    with open(File("test_inputs/metallica.srt"), encoding="utf-8") as infile:
        parsed = videogrep.srt.parse(infile)

    assert parsed[1]["content"].strip() == "E não são poucos, foram vendidos 59 mil bilhetes."
    assert parsed[1]["start"] == approx(4.86)
    assert parsed[1]["end"] == approx(7.76)


def test_cued_vtts():
    testfile = File("test_inputs/metallica.vtt")
    with open(testfile, encoding="utf-8") as infile:
        parsed = videogrep.vtt.parse(infile)

    assert parsed[0]["content"].strip() == "Prometo ser o concerto desta noite no estádio de Alvalade, mas só para ouvidos duros."
    assert parsed[0]["start"] == approx(0.0)
    assert parsed[0]["end"] == approx(4.7)


def test_find_sub():
    testvid = File("test_inputs/metallica.mp4")
    testsubfile = File("test_inputs/metallica.json")
    assert videogrep.find_transcript(testvid) == testsubfile

    testaud = File("test_inputs/metallica.mp3")
    testsubfile = File("test_inputs/metallica.json")
    assert videogrep.find_transcript(testaud) == testsubfile


def test_parse_transcript():
    testvid = File("test_inputs/metallica.mp4")
    transcript = videogrep.parse_transcript(testvid)
    assert transcript[0]["content"] == "Prometo ser o concerto desta noite no est\u00e1dio de Alvalade, mas s\u00f3 para ouvidos duros."


def test_remove_overlaps():
    segments = [{"start": 0, "end": 1}, {"start": 0.5, "end": 2}]
    cleaned = videogrep.remove_overlaps(segments)
    assert len(cleaned) == 1
    assert cleaned[-1]["end"] == 2

    segments = [{"start": 0, "end": 1}, {"start": 2, "end": 3}]
    cleaned = videogrep.remove_overlaps(segments)
    assert len(cleaned) == 2
    assert cleaned[-1]["end"] == 3


def test_pad_and_sync():
    # should remove overlap and make a single segment
    segments = [
        {"start": 0, "end": 1, "file": "1"},
        {"start": 0.5, "end": 2, "file": "1"},
    ]
    cleaned = videogrep.pad_and_sync(segments)
    assert len(cleaned) == 1
    assert cleaned[-1]["end"] == approx(2)


def test_ngrams():
    testvid = File("test_inputs/metallica.mp4")

    grams = list(videogrep.get_ngrams(testvid, 1))
    assert len(grams) == 262

    most_common = Counter(grams).most_common(10)
    assert most_common[0] == (("que",), 9)

    grams = list(videogrep.get_ngrams(testvid, 2))
    assert len(grams) == 261

    most_common = Counter(grams).most_common(10)
    assert most_common[0] == (("a", "gente"), 3)


def test_videogrep():
    out1 = File("test_outputs/supercut1.mp4")
    # Search for "Metallica" which appears many times
    videogrep.videogrep(
        File("test_inputs/metallica.mp4"),
        "Metallica",
        search_type="fragment",
        output=out1,
    )
    duration = get_duration(out1)
    assert duration > 0


def test_sentence_search_json():
    testvid = File("test_inputs/metallica.mp4")

    query = "Metallica"
    segments = videogrep.search(testvid, query, prefer=".json")
    for s in segments:
        assert query.lower() in s["content"].lower()
    assert len(segments) == 11


def test_word_search_json():
    testvid = File("test_inputs/metallica.mp4")
    segments = videogrep.search(testvid, "Metallica", search_type="fragment")
    assert len(segments) == 12

    segments = videogrep.search(testvid, "Suicidal Tendencies", search_type="fragment")
    assert len(segments) == 1
    assert segments[0]["start"] == approx(16.78)
    assert segments[0]["end"] == approx(17.96)


def test_cli():
    infile = File("test_inputs/metallica.mp4")
    outfile = File("test_outputs/supercut.mp4")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "videogrep.cli",
            "--input",
            infile,
            "--output",
            outfile,
            "--search",
            "Metallica",
            "--search-type",
            "fragment",
            "--max-clips",
            "1",
        ]
    )

    assert get_duration(outfile) > 0
