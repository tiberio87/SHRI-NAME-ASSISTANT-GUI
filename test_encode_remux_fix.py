# -*- coding: utf-8 -*-
"""
Test per la correzione della rilevazione ENCODE vs REMUX
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkv_rename_assistant import MKVRenameAssistant
import tkinter as tk
from unittest.mock import Mock


def test_encode_vs_remux_detection():
    """Test della rilevazione corretta di ENCODE vs REMUX"""
    
    print("🎯 Test Rilevazione ENCODE vs REMUX")
    print("=" * 50)
    
    # Setup
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Test cases
    test_cases = [
        {
            "name": "ENCODE con x264 in Writing Library",
            "filename": "Material.Love.2025.Bluray.1080p.AC3.ITA.ENG.x264-iSlaNd.mkv",
            "writing_library": "x264 core 164 r3095 baee400",
            "encoded_settings": "cabac=1 ref=3 deblock=1:0:0",
            "expected_type": "ENCODE",
            "expected_name_pattern": "Material.Love.2025.1080p.BluRay.DD5.1.x264-iSlaNd.mkv"
        },
        {
            "name": "ENCODE con x265 in Writing Library",
            "filename": "Movie.2024.1080p.BluRay.x265-GROUP.mkv",
            "writing_library": "x265 - 3.5:[Linux][GCC 9.3.0][64 bit] 8bit+10bit+12bit",
            "encoded_settings": "crf=18.0 preset=slow",
            "expected_type": "ENCODE",
            "expected_name_pattern": "Movie.2024.1080p.BluRay.x265-GROUP.mkv"
        },
        {
            "name": "REMUX senza Writing Library",
            "filename": "Epic.Movie.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HEVC.REMUX-GROUP.mkv",
            "writing_library": "",
            "encoded_settings": "",
            "expected_type": "REMUX",
            "expected_name_pattern": "Epic.Movie.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-GROUP.mkv"
        },
        {
            "name": "REMUX con marker nel nome",
            "filename": "Action.Film.2023.BluRay.1080p.DTS-HD.MA.5.1.AVC.REMUX-TEAM.mkv",
            "writing_library": "",
            "encoded_settings": "",
            "expected_type": "REMUX",
            "expected_name_pattern": "Action.Film.2023.BluRay.1080p.DTS-HD.MA.5.1.AVC.REMUX-TEAM.mkv"
        },
        {
            "name": "ENCODE con HandBrake",
            "filename": "Series.S01E01.2023.1080p.BluRay.x264-RELEASE.mkv",
            "writing_library": "HandBrake 1.6.1",
            "encoded_settings": "",
            "expected_type": "ENCODE",
            "expected_name_pattern": "Series.S01E01.2023.1080p.BluRay.x264-RELEASE.mkv"
        },
        {
            "name": "ENCODE con FFmpeg",
            "filename": "Documentary.2024.1080p.BluRay.x265-TEAM.mkv",
            "writing_library": "ffmpeg",
            "encoded_settings": "bitrate=5000000",
            "expected_type": "ENCODE",
            "expected_name_pattern": "Documentary.2024.1080p.BluRay.x265-TEAM.mkv"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"   File: {test_case['filename']}")
        print(f"   Writing Library: '{test_case['writing_library']}'")
        
        # Setup mock MediaInfo
        mock_general_track = Mock()
        mock_general_track.track_type = 'General'
        mock_general_track.file_name = test_case['filename']
        
        mock_video_track = Mock()
        mock_video_track.track_type = 'Video'
        mock_video_track.width = 1920
        mock_video_track.height = 1080
        mock_video_track.format = "HEVC" if "x265" in test_case['filename'] else "AVC"
        mock_video_track.writing_library = test_case['writing_library']
        mock_video_track.encoded_library_settings = test_case['encoded_settings']
        mock_video_track.bit_rate = 25000000  # 25 Mbps
        
        # Mock audio track
        mock_audio_track = Mock()
        mock_audio_track.track_type = 'Audio'
        mock_audio_track.format = 'AC-3'
        mock_audio_track.channel_s = '6'
        mock_audio_track.language = 'it'
        
        app.mediainfo_data = Mock()
        app.mediainfo_data.tracks = [mock_general_track, mock_video_track, mock_audio_track]
        
        # Set filename
        app.current_file.set(test_case['filename'])
        
        try:
            # Test rilevazione tipo
            is_remux = app._is_remux()
            detected_type = "REMUX" if is_remux else "ENCODE"
            
            print(f"   Detected Type: {detected_type}")
            print(f"   Expected Type: {test_case['expected_type']}")
            
            if detected_type == test_case['expected_type']:
                print("   ✅ PASS - Tipo rilevato correttamente")
                passed += 1
            else:
                print("   ❌ FAIL - Tipo rilevato erroneamente")
                failed += 1
                
            # Test generazione nome
            meta = app.extract_metadata()
            generated_name = app._build_scene_name(meta)
            
            print(f"   Generated: {generated_name}")
            print(f"   Expected: {test_case['expected_name_pattern']}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    # Risultati
    print(f"\n" + "="*50)
    print(f"📊 Risultati: {passed} passati, {failed} falliti")
    
    if failed == 0:
        print("🎉 Tutti i test passati!")
        print("✅ Rilevazione ENCODE/REMUX funziona correttamente")
    else:
        print(f"⚠️  {failed} test falliti - verificare la logica")
    
    root.destroy()
    return failed == 0


def test_specific_case():
    """Test del caso specifico segnalato"""
    
    print(f"\n🔍 Test Caso Specifico")
    print("=" * 50)
    print("Material.Love.2025.Bluray.1080p.AC3.ITA.ENG.x264-iSlaNd.mkv")
    print("Dovrebbe essere rilevato come ENCODE, non REMUX")
    
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Mock esatto del caso problematico
    mock_general_track = Mock()
    mock_general_track.track_type = 'General'
    mock_general_track.file_name = 'Material.Love.2025.Bluray.1080p.AC3.ITA.ENG.x264-iSlaNd.mkv'
    
    mock_video_track = Mock()
    mock_video_track.track_type = 'Video'
    mock_video_track.width = 1920
    mock_video_track.height = 1080
    mock_video_track.format = "AVC"
    mock_video_track.writing_library = "x264 core 164 r3095 baee400"  # Evidenza di encoding!
    mock_video_track.encoded_library_settings = "cabac=1 ref=3 deblock=1:0:0 analyse=0x3:0x113"
    mock_video_track.bit_rate = 8000000  # 8 Mbps (tipico per encode)
    
    mock_audio_track = Mock()
    mock_audio_track.track_type = 'Audio'
    mock_audio_track.format = 'AC-3'
    mock_audio_track.channel_s = '6'
    mock_audio_track.language = 'it'
    
    app.mediainfo_data = Mock()
    app.mediainfo_data.tracks = [mock_general_track, mock_video_track, mock_audio_track]
    app.current_file.set('Material.Love.2025.Bluray.1080p.AC3.ITA.ENG.x264-iSlaNd.mkv')
    
    # Test
    is_remux = app._is_remux()
    meta = app.extract_metadata()
    generated_name = app._build_scene_name(meta)
    
    print(f"\nAnalisi:")
    print(f"  Writing Library: '{mock_video_track.writing_library}'")
    print(f"  È REMUX?: {is_remux}")
    print(f"  Tipo rilevato: {meta.get('type', 'N/A')}")
    print(f"  Nome generato: {generated_name}")
    
    expected_type = "ENCODE"
    success = not is_remux and meta.get('type') == expected_type
    
    if success:
        print(f"  ✅ SUCCESSO - Rilevato correttamente come {expected_type}")
    else:
        print(f"  ❌ FALLIMENTO - Dovrebbe essere {expected_type}")
    
    root.destroy()
    return success


if __name__ == "__main__":
    print("🔧 Test Correzione ENCODE vs REMUX")
    print("Verifica che x264/x265 in Writing Library = ENCODE")
    print("=" * 60)
    
    success1 = test_encode_vs_remux_detection()
    success2 = test_specific_case()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🏆 TUTTI I TEST PASSATI!")
        print("✅ La correzione risolve il problema segnalato")
        print("💡 File con x264/x265 in Writing Library sono ora ENCODE")
    else:
        print("🔧 ALCUNI TEST FALLITI")
        print("❌ Necessarie ulteriori correzioni")
    
    print(f"\nPer testare con file reali:")
    print("python mkv_rename_assistant.py")