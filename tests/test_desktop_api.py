import pytest
import json
import os
from unittest.mock import patch, MagicMock
import sys

# Import the module to test
# We might need to add desktop to sys.path
sys.path.append(os.path.join(os.getcwd(), 'desktop'))
import desktop_api

@patch('desktop_api.voxgrep.search')
@patch('desktop_api.voxgrep.find_transcript')
@patch('desktop_api.transcribe.transcribe')
@patch('desktop_api.emit')
def test_cmd_search_triggers_transcribe(mock_emit, mock_transcribe, mock_find, mock_search, tmp_path):
    # Setup: a directory with 2 videos, one with transcript, one without
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    
    vid1 = downloads / "video1.mp4"
    vid1.write_text("v1")
    vid2 = downloads / "video2.mp4"
    vid2.write_text("v2")
    
    # Mock find_transcript: vid1 found, vid2 NOT found initially
    mock_find.side_effect = [str(downloads / "video1.json"), None, str(downloads / "video2.json")]
    
    # Mock search results
    mock_search.return_value = [{"file": str(vid1), "start": 0, "end": 1, "content": "hello"}]
    
    # Run cmd_search on the downloads directory
    desktop_api.cmd_search("query", str(downloads))
    
    # Verify transcribe was called for vid2
    mock_transcribe.assert_called_once()
    args, kwargs = mock_transcribe.call_args
    assert kwargs['videofile'] == str(vid2)
    
    # Verify search was called with both files
    mock_search.assert_called_once()
    files_searched = mock_search.call_args[0][0]
    assert len(files_searched) == 2
    assert str(vid1) in files_searched
    assert str(vid2) in files_searched

@patch('desktop_api.voxgrep.create_supercut')
@patch('desktop_api.emit')
def test_cmd_export(mock_emit, mock_supercut):
    matches = [{"file": "v1.mp4", "start": 0, "end": 1, "content": "hi"}]
    desktop_api.cmd_export(json.dumps(matches), "out.mp4")
    
    mock_supercut.assert_called_once_with(matches, "out.mp4")
    mock_emit.assert_any_call("complete", {"path": "out.mp4"})
