#!/usr/bin/env python3
"""
Test per correzione priorità serie TV
"""

import sys
import os

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock
import tkinter as tk
from mkv_rename_assistant import MKVRenameAssistant

def create_mock_mediainfo_remux(filename="test.mkv"):
    """Crea un mock MediaInfo che sembrerebbe un REMUX (senza writing library)"""
    mock_media = Mock()
    
    # General track
    general_track = Mock()
    general_track.track_type = 'General'
    general_track.file_name = filename
    
    # Video track che sembra REMUX (no writing library, bitrate alto)
    video_track = Mock()
    video_track.track_type = 'Video'
    video_track.format = 'HEVC'
    video_track.width = 3840
    video_track.height = 2160
    video_track.writing_library = None  # Nessuna writing library = sembra REMUX
    video_track.encoded_library_settings = None
    video_track.format_settings = None
    video_track.bit_rate = '25000000'  # 25 Mbps = alto bitrate da REMUX
    # No HDR per semplicità
    video_track.hdr_format = None
    video_track.hdr_format_profile = None
    video_track.hdr_format_compatibility = None
    video_track.color_primaries = None
    video_track.transfer_characteristics = None
    
    # Audio track
    audio_track = Mock()
    audio_track.track_type = 'Audio'
    audio_track.format = 'AC-3'
    audio_track.format_commercial_ifany = 'Dolby Digital'
    audio_track.channel_s = '6'
    audio_track.language = 'en'
    
    mock_media.tracks = [general_track, video_track, audio_track]
    return mock_media

def test_tv_series_priority():
    """Test che le serie TV abbiano priorità su REMUX detection"""
    print("🧪 Test Priorità Serie TV su REMUX...")
    
    root = tk.Tk()
    root.withdraw()  # Nascondi finestra per i test
    app = MKVRenameAssistant(root)
    
    test_cases = [
        {
            'filename': 'Dying for Sex S01E01 Una bibita dietetica conveniente.mkv',
            'expected_type': 'WEBDL',  # Dovrebbe essere WEB-DL, non REMUX
            'expected_source': 'WEB'
        },
        {
            'filename': 'Game of Thrones S08E06 2160p UHD BluRay.mkv',
            'expected_type': 'WEBDL',  # Serie TV = WEB anche se sembra BluRay
            'expected_source': 'WEB'
        },
        {
            'filename': 'The Boys S03E08 Final Episode.mkv',
            'expected_type': 'WEBDL',
            'expected_source': 'WEB'
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n  Test {i+1}: {case['filename']}")
        
        # Setup mock che sembrerebbe un REMUX
        app.current_file.set(case['filename'])
        app.mediainfo_data = create_mock_mediainfo_remux(filename=case['filename'])
        
        # Extract metadata
        meta = app.extract_metadata()
        
        print(f"    Rilevato: Type={meta['type']}, Source={meta['source']}")
        
        # Verifica che sia WEB e non REMUX
        if meta['type'] == case['expected_type'] and meta['source'] == case['expected_source']:
            print(f"    ✅ PASS - Correttamente classificato come {meta['source']}/{meta['type']}")
        else:
            print(f"    ❌ FAIL - Expected: {case['expected_source']}/{case['expected_type']}, Got: {meta['source']}/{meta['type']}")

def test_film_still_remux():
    """Test che i film (senza S01E01) possano ancora essere REMUX"""
    print("\n🧪 Test Film Possono Ancora Essere REMUX...")
    
    root = tk.Tk()
    root.withdraw()
    app = MKVRenameAssistant(root)
    
    test_cases = [
        {
            'filename': 'Avatar The Way of Water 2022 2160p BluRay REMUX.mkv',
            'expected_type': 'REMUX',  # Film senza S01E01 può essere REMUX
            'expected_source': 'BluRay'
        },
        {
            'filename': 'Top Gun Maverick 2022 UHD BluRay.mkv',
            'expected_type': 'REMUX',  # Dovrebbe rilevare come REMUX per film
            'expected_source': 'BluRay'
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n  Test {i+1}: {case['filename']}")
        
        # Setup mock REMUX
        app.current_file.set(case['filename'])
        app.mediainfo_data = create_mock_mediainfo_remux(filename=case['filename'])
        
        # Extract metadata
        meta = app.extract_metadata()
        
        print(f"    Rilevato: Type={meta['type']}, Source={meta['source']}")
        
        # Verifica
        if meta['type'] == case['expected_type'] and meta['source'] == case['expected_source']:
            print(f"    ✅ PASS - Correttamente classificato come {meta['source']}/{meta['type']}")
        else:
            print(f"    ❌ FAIL - Expected: {case['expected_source']}/{case['expected_type']}, Got: {meta['source']}/{meta['type']}")

def main():
    """Esegue tutti i test"""
    print("🎬 SHRI MKV Assistant - Test Priorità Serie TV")
    print("=" * 60)
    
    test_tv_series_priority()
    test_film_still_remux()
    
    print("\n" + "=" * 60)
    print("✅ Test completati!")

if __name__ == "__main__":
    main()