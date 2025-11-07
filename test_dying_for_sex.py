#!/usr/bin/env python3
"""
Test specifico per Dying for Sex
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock
import tkinter as tk
from mkv_rename_assistant import MKVRenameAssistant

def create_mock_mediainfo_webdl(filename="test.mkv"):
    """Mock per WEB-DL senza encoding"""
    mock_media = Mock()
    
    general_track = Mock()
    general_track.track_type = 'General'
    general_track.file_name = filename
    
    video_track = Mock()
    video_track.track_type = 'Video'
    video_track.format = 'HEVC'
    video_track.width = 1920
    video_track.height = 1080  
    video_track.writing_library = None  # No encoding library
    video_track.encoded_library_settings = None
    video_track.format_settings = None
    video_track.bit_rate = '8000000'
    video_track.hdr_format = None
    video_track.hdr_format_profile = None
    video_track.hdr_format_compatibility = None
    video_track.color_primaries = None
    video_track.transfer_characteristics = None
    
    audio_track = Mock()
    audio_track.track_type = 'Audio'
    audio_track.format = 'AC-3'
    audio_track.format_commercial_ifany = 'Dolby Digital'
    audio_track.channel_s = '6'
    audio_track.language = 'en'
    
    mock_media.tracks = [general_track, video_track, audio_track]
    return mock_media

def test_dying_for_sex():
    """Test specifico per il file problematico"""
    print("🎯 Test Specifico: Dying for Sex")
    print("=" * 50)
    
    root = tk.Tk()
    root.withdraw()
    app = MKVRenameAssistant(root)
    
    filename = 'Dying for Sex S01E01 Una bibita dietetica conveniente.mkv'
    
    # Setup
    app.current_file.set(filename)
    app.mediainfo_data = create_mock_mediainfo_webdl(filename=filename)
    
    # Test metadata
    meta = app.extract_metadata()
    print(f"📋 Metadata estratti:")
    print(f"   Type: {meta['type']}")
    print(f"   Source: {meta['source']}")
    print(f"   Resolution: {meta['resolution']}")
    print(f"   Video Codec: {meta['video_codec']}")
    print(f"   Audio: {meta['audio']}")
    
    # Test nome generato
    scene_name = app._build_scene_name(meta)
    print(f"\n🎬 Nome generato:")
    print(f"   {scene_name}")
    
    # Verifica elementi attesi
    expected = ['Dying.for.Sex', 'S01E01', '1080p', 'WEB-DL', 'DD5.1', 'H.265']
    print(f"\n✅ Controllo elementi:")
    for element in expected:
        if element in scene_name:
            print(f"   ✅ {element}")
        else:
            print(f"   ❌ {element} (mancante)")

if __name__ == "__main__":
    test_dying_for_sex()