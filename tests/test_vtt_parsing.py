from voxgrep import vtt

def test_parse_cued_vtt_with_word_timestamps():
    vtt_content = """WEBVTT
Kind: captions
Language: en

00:00:00.160 --> 00:00:02.110 align:start position:0%
 
It's <00:00:00.323><c>the </c><00:00:00.486><c>last </c><00:00:00.649><c>one </c><00:00:00.812><c>of </c>

00:00:02.110 --> 00:00:04.000 align:start position:0%
<00:00:02.500><c>all, </c>
"""
    parsed = vtt.parse(vtt_content)
    
    # First segment
    assert len(parsed) >= 1
    assert parsed[0]["start"] == 0.16
    assert parsed[0]["end"] == 2.11
    
    # Check words in first segment
    words = parsed[0]["words"]
    assert words[0]["word"] == "It's"
    assert words[0]["start"] == 0.16
    assert words[0]["end"] == 0.323
    
    assert words[1]["word"] == "the"
    assert words[1]["start"] == 0.323
    assert words[1]["end"] == 0.486

def test_parse_uncued_vtt():
    vtt_content = """WEBVTT

00:00:01.000 --> 00:00:02.000
Hello World
"""
    parsed = vtt.parse(vtt_content)
    assert len(parsed) == 1
    assert parsed[0]["content"] == "Hello World"
    assert parsed[0]["start"] == 1.0
    assert parsed[0]["end"] == 2.0
