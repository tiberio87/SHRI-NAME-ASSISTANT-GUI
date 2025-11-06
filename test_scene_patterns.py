# -*- coding: utf-8 -*-
"""
Test specifici per i pattern di naming scene
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkv_rename_assistant import MKVRenameAssistant
import tkinter as tk


def test_scene_patterns():
    """Test dei pattern di naming secondo gli esempi forniti"""
    
    print("🎬 Test Pattern Naming Scene")
    print("=" * 50)
    
    # Setup
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Test cases basati sugli esempi forniti
    test_cases = [
        {
            "name": "FILM ENCODE DA BLURAY 1080p x264",
            "meta": {
                'basename': 'Black.Dog.2024.1080p.BluRay.DD5.1.x264-iSlaNd',
                'resolution': '1080p',
                'source': 'BluRay',
                'type': 'ENCODE',
                'video_codec': 'x264',
                'audio': 'DD5.1',
                'tag': 'iSlaNd'
            },
            "expected": "Black.Dog.2024.1080p.BluRay.DD5.1.x264-iSlaNd.mkv"
        },
        {
            "name": "FILM ENCODE DA BLURAY 1080p x265",
            "meta": {
                'basename': 'Black.Dog.2024.1080p.BluRay.DD5.1.x265-iSlaNd',
                'resolution': '1080p',
                'source': 'BluRay',
                'type': 'ENCODE',
                'video_codec': 'x265',
                'audio': 'DD5.1',
                'tag': 'iSlaNd'
            },
            "expected": "Black.Dog.2024.1080p.BluRay.DD5.1.x265-iSlaNd.mkv"
        },
        {
            "name": "FILM ENCODE DA BLURAY 2160p HDR",
            "meta": {
                'basename': 'Black.Dog.2024.2160p.BluRay.DDP.7.1.DV.HDR10.x265-iSlaNd',
                'resolution': '2160p',
                'source': 'BluRay',
                'type': 'ENCODE',
                'video_codec': 'x265',
                'audio': 'DDP.7.1',
                'tag': 'iSlaNd'
            },
            "expected": "Black.Dog.2024.2160p.BluRay.DDP.7.1.x265-iSlaNd.mkv"
        },
        {
            "name": "FILM WEB-DL 2160p AMZN",
            "meta": {
                'basename': 'Hedda.2025.2160p.AMZN.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-FHC',
                'resolution': '2160p',
                'source': 'WEB',
                'type': 'WEBDL',
                'video_codec': 'H.265',
                'audio': 'DDP5.1.Atmos',
                'service': 'AMZN',
                'tag': 'FHC'
            },
            "expected": "Hedda.2025.2160p.AMZN.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-FHC.mkv"
        },
        {
            "name": "FILM WEB-DL 1080p AMZN",
            "meta": {
                'basename': 'Hedda.2025.1080P.AMZN.WEB-DL.DDP5.1.Atmos.H.264-FHC',
                'resolution': '1080p',
                'source': 'WEB',
                'type': 'WEBDL',
                'video_codec': 'H.264',
                'audio': 'DDP5.1.Atmos',
                'service': 'AMZN',
                'tag': 'FHC'
            },
            "expected": "Hedda.2025.1080p.AMZN.WEB-DL.DDP5.1.Atmos.H.264-FHC.mkv"
        },
        {
            "name": "FILM REMUX UHD 2160p",
            "meta": {
                'basename': 'Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd',
                'resolution': '2160p',
                'source': 'BluRay',
                'type': 'REMUX',
                'video_codec': 'HVEC',
                'audio': 'TrueHD.Atmos.7.1',
                'tag': 'iSlaNd'
            },
            "expected": "Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd.mkv"
        },
        {
            "name": "FILM REMUX 1080p",
            "meta": {
                'basename': 'Black.Dog.2024.BluRay.1080p.TrueHD.Atmos.7.1.AVC.REMUX-iSlaNd',
                'resolution': '1080p',
                'source': 'BluRay',
                'type': 'REMUX',
                'video_codec': 'AVC',
                'audio': 'TrueHD.Atmos.7.1',
                'tag': 'iSlaNd'
            },
            "expected": "Black.Dog.2024.BluRay.1080p.TrueHD.Atmos.7.1.AVC.REMUX-iSlaNd.mkv"
        }
    ]
    
    # Esegui test
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['meta']['basename']}")
        
        try:
            result = app._build_scene_name(test_case['meta'])
            expected = test_case['expected']
            
            print(f"   Output: {result}")
            print(f"   Expected: {expected}")
            
            if result == expected:
                print("   ✅ PASS")
                passed += 1
            else:
                print("   ❌ FAIL")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    # Risultati finali
    print("\n" + "=" * 50)
    print(f"📊 Risultati Test: {passed} passati, {failed} falliti")
    
    if failed == 0:
        print("🎉 Tutti i test sono passati!")
    else:
        print(f"⚠️  {failed} test falliti - verifica la logica di naming")
    
    root.destroy()
    return failed == 0


def test_extraction_functions():
    """Test delle funzioni di estrazione metadati"""
    
    print("\n🔍 Test Funzioni Estrazione")
    print("=" * 50)
    
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    
    # Test estrazione titolo e anno
    test_cases = [
        ("Black.Dog.2024.1080p.BluRay", ("Black Dog", "2024")),
        ("Hedda.2025.2160p.AMZN", ("Hedda", "2025")),
        ("The.Matrix.1999.720p", ("The Matrix", "1999")),
        ("Movie[2020]1080p", ("Movie", "2020"))
    ]
    
    print("\nTest estrazione titolo/anno:")
    for filename, expected in test_cases:
        result = app._extract_title_year(filename)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename} -> {result} (expected: {expected})")
    
    # Test codec mapping
    print("\nTest codec mapping:")
    test_codecs = [
        ("x264", "AVC", "H.264"),  # encode, remux, webdl
        ("x265", "HVEC", "H.265"),
        ("HEVC", "HVEC", "H.265"),
        ("AVC", "AVC", "H.264")
    ]
    
    for original, remux_expected, webdl_expected in test_codecs:
        meta_remux = {'video_codec': original, 'type': 'REMUX'}
        meta_webdl = {'video_codec': original, 'type': 'WEBDL'}
        
        remux_result = app._get_remux_codec(meta_remux)
        webdl_result = app._get_webdl_codec(meta_webdl)
        
        remux_status = "✅" if remux_result == remux_expected else "❌"
        webdl_status = "✅" if webdl_result == webdl_expected else "❌"
        
        print(f"  {remux_status} REMUX {original} -> {remux_result}")
        print(f"  {webdl_status} WEB-DL {original} -> {webdl_result}")
    
    root.destroy()


if __name__ == "__main__":
    print("🎯 MKV Rename Assistant - Test Pattern Scene")
    print("Verifica conformità ai pattern forniti")
    print("=" * 60)
    
    # Esegui test
    success = test_scene_patterns()
    test_extraction_functions()
    
    print("\n" + "=" * 60)
    if success:
        print("🏆 TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("L'applicazione è pronta per l'uso.")
    else:
        print("🔧 ALCUNI TEST FALLITI - Necessarie correzioni")
    
    print("\nPer avviare l'applicazione:")
    print("python mkv_rename_assistant.py")