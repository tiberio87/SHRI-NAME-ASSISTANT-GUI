# -*- coding: utf-8 -*-
"""
Test per la correzione della classificazione della risoluzione
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkv_rename_assistant import MKVRenameAssistant
import tkinter as tk
from unittest.mock import Mock


def test_resolution_classification():
    """Test della classificazione corretta della risoluzione"""
    
    print("🎯 Test Classificazione Risoluzione")
    print("=" * 50)
    
    # Setup
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Test cases per diverse risoluzioni
    test_cases = [
        # (width, height, expected_resolution, description)
        (1920, 1080, '1080p', "Standard 1080p"),
        (1920, 804, '1080p', "Widescreen 1920x804 (dovrebbe essere 1080p, non 720p)"),
        (1920, 800, '1080p', "Widescreen 1920x800"),
        (1920, 858, '1080p', "Widescreen 1920x858"),
        (1920, 872, '1080p', "Widescreen 1920x872"),
        (1920, 960, '1080p', "Widescreen 1920x960"),
        (1280, 720, '720p', "Standard 720p"),
        (1280, 536, '720p', "Widescreen 1280x536"),
        (3840, 2160, '2160p', "Standard 4K"),
        (3840, 1608, '2160p', "4K Widescreen"),
        (1440, 1080, '1080p', "1440x1080 (dovrebbe essere 1080p)"),
        (720, 576, '576p', "Standard DVD PAL"),
        (720, 480, '480p', "Standard DVD NTSC"),
    ]
    
    passed = 0
    failed = 0
    
    for width, height, expected, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  Input: {width}x{height}")
        
        # Mock dei tracks per MediaInfo
        mock_general_track = Mock()
        mock_general_track.track_type = 'General'
        mock_general_track.file_name = 'test.mkv'
        
        mock_video_track = Mock()
        mock_video_track.track_type = 'Video'
        mock_video_track.width = width
        mock_video_track.height = height
        mock_video_track.format = "AVC"
        
        # Mock mediainfo_data con struttura corretta
        app.mediainfo_data = Mock()
        app.mediainfo_data.tracks = [mock_general_track, mock_video_track]
        
        # Estrai metadati
        try:
            meta = app.extract_metadata()
            result = meta.get('resolution', 'N/A')
            
            print(f"  Output: {result}")
            print(f"  Expected: {expected}")
            
            if result == expected:
                print("  ✅ PASS")
                passed += 1
            else:
                print("  ❌ FAIL")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    # Test specifico per il problema segnalato
    print(f"\n" + "="*50)
    print("🔍 Test Specifico: 1920x804 con x264/x265")
    
    widescreen_cases = [
        (1920, 804, 'x264', '1080p'),
        (1920, 804, 'x265', '1080p'),
        (1920, 800, 'x264', '1080p'),
        (1920, 858, 'x265', '1080p'),
    ]
    
    for width, height, codec, expected in widescreen_cases:
        mock_general_track = Mock()
        mock_general_track.track_type = 'General'
        mock_general_track.file_name = 'test.mkv'
        
        mock_video_track = Mock()
        mock_video_track.track_type = 'Video'
        mock_video_track.width = width
        mock_video_track.height = height
        mock_video_track.format = "HEVC" if codec == "x265" else "AVC"
        
        app.mediainfo_data = Mock()
        app.mediainfo_data.tracks = [mock_general_track, mock_video_track]
        
        meta = app.extract_metadata()
        resolution = meta.get('resolution', 'N/A')
        video_codec = meta.get('video_codec', 'N/A')
        
        print(f"  {width}x{height} {codec} -> {resolution} (expected: {expected})")
        
        if resolution == expected:
            print("    ✅ PASS")
            passed += 1
        else:
            print("    ❌ FAIL")
            failed += 1
    
    # Risultati finali
    print(f"\n" + "="*50)
    print(f"📊 Risultati: {passed} passati, {failed} falliti")
    
    if failed == 0:
        print("🎉 Tutti i test della risoluzione passati!")
        print("✅ Fix implementato correttamente!")
    else:
        print(f"⚠️  {failed} test falliti - necessarie ulteriori correzioni")
    
    root.destroy()
    return failed == 0


def test_aspect_ratio_examples():
    """Test con esempi reali di aspect ratio problematici"""
    
    print(f"\n📐 Test Aspect Ratio Problematici")
    print("=" * 50)
    
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Esempi reali di film con aspect ratio diversi
    real_examples = [
        # Film in formato scope (2.39:1)
        (1920, 804, "Film in formato Scope 2.39:1"),
        (1920, 800, "Film in formato Scope variante"),
        
        # Film in formato flat (1.85:1)  
        (1920, 1038, "Film in formato Flat 1.85:1"),
        
        # Film in formato academy modificato
        (1920, 872, "Film formato Academy modificato"),
        
        # Alcuni encode particolari
        (1920, 858, "Encode con crop particolare"),
        (1920, 960, "Encode 2:1 aspect ratio"),
    ]
    
    all_passed = True
    
    for width, height, description in real_examples:
        mock_general_track = Mock()
        mock_general_track.track_type = 'General'
        mock_general_track.file_name = 'test.mkv'
        
        mock_video_track = Mock()
        mock_video_track.track_type = 'Video'
        mock_video_track.width = width
        mock_video_track.height = height
        mock_video_track.format = "AVC"
        
        app.mediainfo_data = Mock()
        app.mediainfo_data.tracks = [mock_general_track, mock_video_track]
        
        meta = app.extract_metadata()
        resolution = meta.get('resolution', 'N/A')
        
        print(f"  {description}")
        print(f"    {width}x{height} -> {resolution}")
        
        if resolution == '1080p':
            print("    ✅ Correttamente classificato come 1080p")
        else:
            print(f"    ❌ Erroneamente classificato come {resolution}")
            all_passed = False
    
    root.destroy()
    return all_passed


if __name__ == "__main__":
    print("🔧 Test Correzione Classificazione Risoluzione")
    print("Verifica che 1920x804 e simili siano classificati come 1080p")
    print("=" * 60)
    
    success1 = test_resolution_classification()
    success2 = test_aspect_ratio_examples()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🏆 TUTTI I TEST PASSATI!")
        print("✅ La correzione funziona correttamente")
        print("💡 1920x804 e aspect ratio simili sono ora classificati come 1080p")
    else:
        print("🔧 ALCUNI TEST FALLITI")
        print("❌ Necessarie ulteriori correzioni")
    
    print(f"\nPer testare con file reali:")
    print("python mkv_rename_assistant.py")