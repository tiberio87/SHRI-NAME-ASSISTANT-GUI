#!/usr/bin/env python3
"""
Test per miglioramenti serie TV e DLMux/WEBMux recognition
"""

import sys
import os

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, MagicMock
import tkinter as tk
from mkv_rename_assistant import MKVRenameAssistant

def create_mock_mediainfo(writing_library="", codec="H.264", resolution=(1920, 1080), filename="test.mkv"):
    """Crea un mock MediaInfo object"""
    mock_media = Mock()
    
    # General track - usa il filename completo
    general_track = Mock()
    general_track.track_type = 'General'
    general_track.file_name = filename  # Nome completo del file
    
    # Video track
    video_track = Mock()
    video_track.track_type = 'Video'
    video_track.format = codec
    video_track.width = resolution[0]
    video_track.height = resolution[1]
    video_track.writing_library = writing_library
    video_track.encoded_library_settings = None
    video_track.format_settings = None
    video_track.bit_rate = '8000000'  # 8 Mbps
    # Assicurati che non ci sia HDR
    video_track.hdr_format = None
    video_track.hdr_format_profile = None
    video_track.hdr_format_compatibility = None
    video_track.color_primaries = None
    video_track.transfer_characteristics = None
    
    # Audio track  
    audio_track = Mock()
    audio_track.track_type = 'Audio'
    audio_track.format = 'E-AC-3'
    audio_track.format_commercial_ifany = 'Dolby Digital Plus'
    audio_track.channel_s = '6'
    audio_track.language = 'en'
    
    mock_media.tracks = [general_track, video_track, audio_track]
    return mock_media

def test_dlmux_webmux_detection():
    """Test detection DLMux/WEBMux come WEB-DL"""
    print("🧪 Test DLMux/WEBMux Detection...")
    
    root = tk.Tk()
    root.withdraw()  # Nascondi finestra per i test
    app = MKVRenameAssistant(root)
    
    test_cases = [
        {
            'filename': 'The Midnight Club S01E01 Il capitolo finale DLMux 1080p E-AC3+AC3 ITA ENG SUBS.mkv',
            'writing_library': '',  # No encoding - dovrebbe essere WEB-DL
            'expected_type': 'WEBDL',
            'expected_source': 'WEB'
        },
        {
            'filename': 'Show Name S02E05 WEBMux 720p AC3 ITA.mkv', 
            'writing_library': '',
            'expected_type': 'WEBDL',
            'expected_source': 'WEB'
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n  Test {i+1}: {case['filename']}")
        
        # Setup mock
        app.current_file.set(case['filename'])
        
        # Mock MediaInfo with correct filename
        mock_media = create_mock_mediainfo(
            writing_library=case['writing_library'],
            filename=case['filename']
        )
        app.mediainfo_data = mock_media
        
        # Extract metadata
        meta = app.extract_metadata()
        
        # Debug info solo per primo test
        if i == 0:
            print(f"    DEBUG - Meta keys: {list(meta.keys())}")
            print(f"    DEBUG - Basename: '{meta.get('basename', 'NOT SET')}'")
            print(f"    DEBUG - Current file: '{app.current_file.get()}'")
            print(f"    DEBUG - General track filename: '{mock_media.tracks[0].file_name}'")
        
        # Verifica
        if meta['type'] == case['expected_type'] and meta['source'] == case['expected_source']:
            print(f"    ✅ PASS - Type: {meta['type']}, Source: {meta['source']}")
        else:
            print(f"    ❌ FAIL - Expected: {case['expected_type']}/{case['expected_source']}, Got: {meta['type']}/{meta['source']}")

def test_webrip_detection():
    """Test detection WEBRip quando c'è x264/x265 writing library"""
    print("\n🧪 Test WEBRip Detection (x264/x265)...")
    
    root = tk.Tk()
    root.withdraw()  # Nascondi finestra per i test
    app = MKVRenameAssistant(root)
    
    test_cases = [
        {
            'filename': 'The Midnight Club S01E01 DLMux 1080p E-AC3.mkv',
            'writing_library': 'x264 core 164',  # Con encoding - dovrebbe essere WEBRip
            'expected_type': 'WEBRIP',
            'expected_source': 'WEB'
        },
        {
            'filename': 'Show Name WEBMux 2160p HEVC.mkv',
            'writing_library': 'x265 3.5',
            'expected_type': 'WEBRIP', 
            'expected_source': 'WEB'
        },
        {
            'filename': 'Movie DLMux 1080p.mkv',
            'writing_library': 'HandBrake 1.4.0',
            'expected_type': 'WEBRIP',
            'expected_source': 'WEB'
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n  Test {i+1}: {case['filename']}")
        
        # Setup mock
        app.current_file.set(case['filename'])
        app.mediainfo_data = create_mock_mediainfo(
            writing_library=case['writing_library'],
            filename=case['filename']
        )
        
        # Extract metadata
        meta = app.extract_metadata()
        
        # Verifica
        if meta['type'] == case['expected_type'] and meta['source'] == case['expected_source']:
            print(f"    ✅ PASS - Type: {meta['type']}, Source: {meta['source']}")
        else:
            print(f"    ❌ FAIL - Expected: {case['expected_type']}/{case['expected_source']}, Got: {meta['type']}/{meta['source']}")

def test_series_name_generation():
    """Test generazione nomi serie TV con S01E01"""
    print("\n🧪 Test Serie TV Name Generation...")
    
    root = tk.Tk()
    root.withdraw()  # Nascondi finestra per i test
    app = MKVRenameAssistant(root)
    
    test_cases = [
        {
            'filename': 'The Midnight Club S01E01 Il capitolo finale DLMux 1080p E-AC3+AC3 ITA ENG SUBS.mkv',
            'writing_library': 'x264 core 164',
            'expected_contains': ['The.Midnight.Club', 'S01E01', '1080p', 'WEBRip', 'x264']
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n  Test {i+1}: {case['filename']}")
        
        # Setup mock
        app.current_file.set(case['filename'])
        app.mediainfo_data = create_mock_mediainfo(
            writing_library=case['writing_library'],
            filename=case['filename']
        )
        
        # Extract metadata e genera nome
        meta = app.extract_metadata()
        scene_name = app._build_scene_name(meta)
        
        print(f"    Nome generato: {scene_name}")
        
        # Verifica che contenga elementi attesi
        all_found = True
        for expected in case['expected_contains']:
            if expected not in scene_name:
                print(f"    ❌ MISSING: {expected}")
                all_found = False
            else:
                print(f"    ✅ FOUND: {expected}")
        
        if all_found:
            print(f"    🎯 OVERALL: PASS")
        else:
            print(f"    ❌ OVERALL: FAIL")

def main():
    """Esegue tutti i test"""
    print("🎬 SHRI MKV Assistant - Test Miglioramenti Serie TV")
    print("=" * 60)
    
    test_dlmux_webmux_detection()
    test_webrip_detection() 
    test_series_name_generation()
    
    print("\n" + "=" * 60)
    print("✅ Test completati!")

if __name__ == "__main__":
    main()