# -*- coding: utf-8 -*-
"""
Test per la correzione del rilevamento HDR/Dolby Vision
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkv_rename_assistant import MKVRenameAssistant
import tkinter as tk
from unittest.mock import Mock


def test_hdr_dv_detection():
    """Test del rilevamento HDR/Dolby Vision dai metadati MediaInfo"""
    
    print("🌈 Test Rilevamento HDR/Dolby Vision")
    print("=" * 50)
    
    # Setup
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Test cases basati su dati MediaInfo reali
    test_cases = [
        {
            "name": "Dolby Vision Profile 8.1 + HDR10 (caso specifico)",
            "filename": "Godzilla.1.2014.ITA.AC3.ENG.EAC3.UHDrip.HDR10.HEVC.2160p-Tib7.mkv",
            "hdr_format": "Dolby Vision, Version 1.0, Profile 8.1, dvhe.08.06, BL+RPU",
            "hdr_format_profile": "dvhe.08.06",
            "hdr_format_compatibility": "HDR10 compatible / SMPTE ST 2086, Version HDR10, HDR10 compatible",
            "color_primaries": "BT.2020",
            "transfer_characteristics": "SMPTE ST 2084",
            "expected_hdr": ["DV", "HDR10"],
            "expected_name": "Godzilla.1.2014.2160p.BluRay.DDP5.1.DV.HDR10.x265-Tib7.mkv"
        },
        {
            "name": "Solo Dolby Vision Profile 5",
            "filename": "Movie.2024.2160p.WEB-DL.DV.x265-GROUP.mkv",
            "hdr_format": "Dolby Vision, Version 1.0, Profile 5",
            "hdr_format_profile": "dvhe.05.06",
            "hdr_format_compatibility": "",
            "color_primaries": "BT.2020",
            "transfer_characteristics": "SMPTE ST 2084",
            "expected_hdr": ["DV"],
            "expected_name": "Movie.2024.2160p.WEB.WEB-DL.DDP5.1.DV.H.265-GROUP.mkv"
        },
        {
            "name": "Solo HDR10",
            "filename": "Action.Film.2023.2160p.BluRay.HDR.x265-TEAM.mkv",
            "hdr_format": "",
            "hdr_format_profile": "",
            "hdr_format_compatibility": "HDR10 compatible / SMPTE ST 2086, Version HDR10",
            "color_primaries": "BT.2020",
            "transfer_characteristics": "SMPTE ST 2084",
            "expected_hdr": ["HDR10"],
            "expected_name": "Action.Film.2023.2160p.BluRay.DDP5.1.HDR10.x265-TEAM.mkv"
        },
        {
            "name": "HDR generico (BT.2020 senza ST2084)",
            "filename": "Series.S01E01.2160p.WEB-DL.HDR.x265-RELEASE.mkv",
            "hdr_format": "",
            "hdr_format_profile": "",
            "hdr_format_compatibility": "",
            "color_primaries": "BT.2020",
            "transfer_characteristics": "BT.709",
            "expected_hdr": ["HDR"],
            "expected_name": "Series.S01E01.2160p.WEB.WEB-DL.DDP5.1.HDR.H.265-RELEASE.mkv"
        },
        {
            "name": "HLG (Hybrid Log-Gamma)",
            "filename": "Documentary.2024.2160p.HEVC.HLG-GROUP.mkv",
            "hdr_format": "",
            "hdr_format_profile": "",
            "hdr_format_compatibility": "",
            "color_primaries": "BT.2020",
            "transfer_characteristics": "ARIB STD-B67",
            "expected_hdr": ["HLG"],
            "expected_name": "Documentary.2024.2160p.BluRay.DDP5.1.HLG.x265-GROUP.mkv"
        },
        {
            "name": "Nessun HDR (SDR)",
            "filename": "Classic.Movie.1999.1080p.BluRay.x264-OLDIES.mkv",
            "hdr_format": "",
            "hdr_format_profile": "",
            "hdr_format_compatibility": "",
            "color_primaries": "BT.709",
            "transfer_characteristics": "BT.709",
            "expected_hdr": [],
            "expected_name": "Classic.Movie.1999.1080p.BluRay.DDP5.1.x264-OLDIES.mkv"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"   File: {os.path.basename(test_case['filename'])}")
        
        # Setup mock MediaInfo con dati HDR reali
        mock_general_track = Mock()
        mock_general_track.track_type = 'General'
        mock_general_track.file_name = test_case['filename']
        
        mock_video_track = Mock()
        mock_video_track.track_type = 'Video'
        mock_video_track.width = 3840 if '2160p' in test_case['filename'] else 1920
        mock_video_track.height = 2160 if '2160p' in test_case['filename'] else 1080
        mock_video_track.format = "HEVC"
        mock_video_track.writing_library = "x265 - 3.5"
        
        # Campi HDR dal MediaInfo
        mock_video_track.hdr_format = test_case['hdr_format']
        mock_video_track.hdr_format_profile = test_case['hdr_format_profile']
        mock_video_track.hdr_format_compatibility = test_case['hdr_format_compatibility']
        mock_video_track.color_primaries = test_case['color_primaries']
        mock_video_track.transfer_characteristics = test_case['transfer_characteristics']
        
        # Mock audio track
        mock_audio_track = Mock()
        mock_audio_track.track_type = 'Audio'
        mock_audio_track.format = 'E-AC-3'
        mock_audio_track.channel_s = '6'
        mock_audio_track.language = 'en'
        
        app.mediainfo_data = Mock()
        app.mediainfo_data.tracks = [mock_general_track, mock_video_track, mock_audio_track]
        app.current_file.set(test_case['filename'])
        
        try:
            # Test estrazione HDR
            meta = app.extract_metadata()
            detected_hdr = meta.get('hdr_info', [])
            
            print(f"   HDR Format: '{test_case['hdr_format']}'")
            print(f"   HDR Compatibility: '{test_case['hdr_format_compatibility']}'")
            print(f"   Detected HDR: {detected_hdr}")
            print(f"   Expected HDR: {test_case['expected_hdr']}")
            
            if detected_hdr == test_case['expected_hdr']:
                print("   ✅ PASS - HDR rilevato correttamente")
                passed += 1
            else:
                print("   ❌ FAIL - HDR rilevato erroneamente")
                failed += 1
                
            # Test generazione nome
            generated_name = app._build_scene_name(meta)
            print(f"   Generated: {generated_name}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    # Risultati
    print(f"\n" + "="*50)
    print(f"📊 Risultati: {passed} passati, {failed} falliti")
    
    if failed == 0:
        print("🎉 Tutti i test HDR/DV passati!")
        print("✅ Rilevamento HDR dai metadati MediaInfo funziona")
    else:
        print(f"⚠️  {failed} test falliti - verificare la logica HDR")
    
    root.destroy()
    return failed == 0


def test_specific_godzilla_case():
    """Test del caso specifico Godzilla segnalato"""
    
    print(f"\n🦖 Test Caso Specifico Godzilla")
    print("=" * 50)
    print("Input: Godzilla.1.2014.ITA.AC3.ENG.EAC3.UHDrip.HDR10.HEVC.2160p-Tib7")
    print("Output atteso: Godzilla.1.2014.2160p.BluRay.DDP5.1.DV.HDR10.x265-Tib7.mkv")
    print("MediaInfo HDR: Dolby Vision Profile 8.1 + HDR10 compatible")
    
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Mock esatto del caso Godzilla
    mock_general_track = Mock()
    mock_general_track.track_type = 'General'
    mock_general_track.file_name = 'Godzilla.1.2014.ITA.AC3.ENG.EAC3.UHDrip.HDR10.HEVC.2160p-Tib7.mkv'
    
    mock_video_track = Mock()
    mock_video_track.track_type = 'Video'
    mock_video_track.width = 3840
    mock_video_track.height = 2160
    mock_video_track.format = "HEVC"
    mock_video_track.writing_library = "x265 - 3.5"
    
    # Dati HDR esatti dal MediaInfo
    mock_video_track.hdr_format = "Dolby Vision, Version 1.0, Profile 8.1, dvhe.08.06, BL+RPU, no metadata compression, HDR10 compatible"
    mock_video_track.hdr_format_profile = "dvhe.08.06"
    mock_video_track.hdr_format_compatibility = "SMPTE ST 2086, Version HDR10, HDR10 compatible"
    mock_video_track.color_primaries = "BT.2020"
    mock_video_track.transfer_characteristics = "SMPTE ST 2084"
    
    mock_audio_track = Mock()
    mock_audio_track.track_type = 'Audio'
    mock_audio_track.format = 'E-AC-3'
    mock_audio_track.channel_s = '6'
    mock_audio_track.language = 'it'
    
    app.mediainfo_data = Mock()
    app.mediainfo_data.tracks = [mock_general_track, mock_video_track, mock_audio_track]
    app.current_file.set('Godzilla.1.2014.ITA.AC3.ENG.EAC3.UHDrip.HDR10.HEVC.2160p-Tib7.mkv')
    
    # Test
    meta = app.extract_metadata()
    hdr_info = meta.get('hdr_info', [])
    generated_name = app._build_scene_name(meta)
    
    print(f"\nAnalisi:")
    print(f"  HDR Format: '{mock_video_track.hdr_format}'")
    print(f"  HDR Compatibility: '{mock_video_track.hdr_format_compatibility}'")
    print(f"  HDR rilevato: {hdr_info}")
    print(f"  Tipo: {meta.get('type', 'N/A')}")
    print(f"  Nome generato: {generated_name}")
    
    expected_hdr = ["DV", "HDR10"]
    expected_name = "Godzilla.1.2014.2160p.BluRay.DDP5.1.DV.HDR10.x265-Tib7.mkv"
    
    hdr_success = hdr_info == expected_hdr
    name_success = generated_name == expected_name
    
    if hdr_success:
        print(f"  ✅ HDR SUCCESSO - Rilevato {hdr_info}")
    else:
        print(f"  ❌ HDR FALLIMENTO - Expected {expected_hdr}, got {hdr_info}")
    
    if name_success:
        print(f"  ✅ NOME SUCCESSO - Generato correttamente")
    else:
        print(f"  ❌ NOME FALLIMENTO - Expected {expected_name}")
    
    root.destroy()
    return hdr_success and name_success


if __name__ == "__main__":
    print("🌈 Test Correzione HDR/Dolby Vision")
    print("Verifica che DV e HDR10 siano rilevati dai metadati MediaInfo")
    print("=" * 60)
    
    success1 = test_hdr_dv_detection()
    success2 = test_specific_godzilla_case()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🏆 TUTTI I TEST HDR PASSATI!")
        print("✅ La correzione risolve il problema HDR/DV")
        print("💡 HDR/DV ora rilevati dai metadati MediaInfo reali")
    else:
        print("🔧 ALCUNI TEST HDR FALLITI")
        print("❌ Necessarie ulteriori correzioni")
    
    print(f"\nPer testare con file reali:")
    print("python mkv_rename_assistant.py")