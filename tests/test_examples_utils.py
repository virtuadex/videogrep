from examples.utils import calculate_silences, merge_clips

def test_calculate_silences():
    timestamps = [
        {"start": 0, "end": 1, "content": "hello", "words": [{"word": "hello", "start": 0, "end": 1}]},
        {"start": 2, "end": 3, "content": "world", "words": [{"word": "world", "start": 2, "end": 3}]}
    ]
    # Gap is from 1 to 2 = 1.0s
    silences = calculate_silences(timestamps, "test.mp4", min_duration=0.5)
    assert len(silences) == 1
    assert silences[0]["start"] == 1
    assert silences[0]["end"] == 2
    
    # Gap is 1.0s, so min_duration=1.5 should return nothing
    silences = calculate_silences(timestamps, "test.mp4", min_duration=1.5)
    assert len(silences) == 0

def test_merge_clips():
    items = [
        {"start": 0, "end": 1},
        {"start": 1.2, "end": 2}, # gap 0.2
        {"start": 5, "end": 6}    # gap 3.0
    ]
    # Merge if gap < 1.0
    merged = merge_clips(items, "test.mp4", min_silence_duration=1.0)
    assert len(merged) == 2
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 2
    assert merged[1]["start"] == 5
    assert merged[1]["end"] == 6
