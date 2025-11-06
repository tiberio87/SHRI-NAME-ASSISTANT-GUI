# -*- coding: utf-8 -*-
"""
Test per MKV Rename Assistant
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Aggiungi il percorso del modulo principale
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mkv_rename_assistant import MKVRenameAssistant
import tkinter as tk


class TestMKVRenameAssistant(unittest.TestCase):
    
    def setUp(self):
        """Setup per i test"""
        self.root = tk.Tk()
        self.app = MKVRenameAssistant(self.root)
        
    def tearDown(self):
        """Cleanup dopo i test"""
        self.root.destroy()
        
    def test_extract_title_year(self):
        """Test estrazione titolo e anno"""
        test_cases = [
            ("Avatar.2009.1080p.BluRay.x264-SPARKS", ("Avatar", "2009")),
            ("The.Matrix.1999.720p.BRRip.x264", ("The Matrix", "1999")),
            ("Inception[2010]DvDrip", ("Inception", "2010")),
            ("Titanic (1997) BluRay", ("Titanic", "1997")),
            ("Movie.Without.Year.1080p", ("Movie Without Year", None))
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.app._extract_title_year(filename)
                self.assertEqual(result, expected)
                
    def test_normalize_language(self):
        """Test normalizzazione lingue"""
        test_cases = [
            ("it", "ITALIAN"),
            ("eng", "ENGLISH"), 
            ("spa", "SPANISH"),
            ("fra", "FRENCH"),
            ("ger", "GERMAN"),
            ("unknown", "UNKNOWN")
        ]
        
        for lang_code, expected in test_cases:
            with self.subTest(lang_code=lang_code):
                result = self.app._normalize_language(lang_code)
                self.assertEqual(result, expected)
                
    def test_get_audio_format(self):
        """Test mapping formato audio"""
        # Mock oggetto audio track
        mock_track = Mock()
        
        test_cases = [
            ("AC-3", "DD"),
            ("E-AC-3", "DDP"),
            ("TrueHD", "TrueHD"),
            ("DTS", "DTS"),
            ("AAC", "AAC")
        ]
        
        for audio_format, expected in test_cases:
            with self.subTest(audio_format=audio_format):
                mock_track.format = audio_format
                result = self.app._get_audio_format(mock_track)
                self.assertEqual(result, expected)
                
    def test_extract_release_group(self):
        """Test estrazione release group"""
        # Mock file path
        test_cases = [
            ("/path/Avatar.2009.1080p.BluRay.x264-SPARKS.mkv", "SPARKS"),
            ("/path/Movie.Name.2020.1080p.WEB-DL-NoGroup.mkv", "NoGroup"),
            ("/path/Bad.Movie.2020-nogrp.mkv", "NoGroup"),  # Tag invalido
            ("/path/Movie.Without.Tag.mkv", "NoGroup")
        ]
        
        for filepath, expected in test_cases:
            with self.subTest(filepath=filepath):
                self.app.current_file.set(filepath)
                result = self.app._extract_release_group()
                self.assertEqual(result, expected)
                
    def test_build_scene_name(self):
        """Test costruzione nome secondo regole scena"""
        meta = {
            'basename': 'Avatar.2009.1080p.BluRay.x264-SPARKS',
            'resolution': '1080p',
            'source': 'BluRay',
            'video_codec': 'x264',
            'audio': 'DTS',
            'audio_languages': ['ENGLISH'],
            'tag': 'SPARKS',
            'type': 'ENCODE'
        }
        
        result = self.app._build_scene_name(meta)
        
        # Verifica che il nome contenga i componenti principali
        self.assertIn('Avatar', result)
        self.assertIn('2009', result)
        self.assertIn('1080p', result)
        self.assertIn('BluRay', result)
        self.assertIn('x264', result)
        self.assertIn('DTS', result)
        self.assertIn('SPARKS', result)
        self.assertTrue(result.endswith('.mkv'))
        
    def test_is_remux_detection(self):
        """Test rilevamento REMUX"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.REMUX.x265-GROUP", True),
            ("Movie.2020.1080p.BluRay.UHD.UNTOUCHED-GROUP", True), 
            ("Movie.2020.1080p.BluRay.VU-GROUP", True),
            ("Movie.2020.1080p.BluRay.x264-GROUP", False)
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                self.app.current_file.set(f"/path/{filename}.mkv")
                result = self.app._is_remux()
                self.assertEqual(result, expected)


class TestSceneNamingRules(unittest.TestCase):
    """Test specifici per le regole di naming della scena"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.app = MKVRenameAssistant(self.root)
        
    def tearDown(self):
        self.root.destroy()
        
    def test_multi_language_handling(self):
        """Test gestione lingue multiple"""
        meta = {
            'basename': 'Movie.2020.Multi.1080p',
            'audio_languages': ['ITALIAN', 'ENGLISH', 'FRENCH'],
            'tag': 'GROUP'
        }
        
        result = self.app._build_scene_name(meta)
        self.assertIn('Multi', result)
        
    def test_italian_english_dual(self):
        """Test gestione dual audio italiano-inglese"""
        meta = {
            'basename': 'Movie.2020.ITA.ENG.1080p',
            'audio_languages': ['ITALIAN', 'ENGLISH'],
            'tag': 'GROUP'
        }
        
        result = self.app._build_scene_name(meta)
        # Dovrebbe contenere ITALIAN-ENGLISH o gestire il dual audio
        self.assertTrue('ITALIAN' in result or 'ITA' in result)
        
    def test_remux_naming(self):
        """Test naming per REMUX"""
        meta = {
            'basename': 'Movie.2020.1080p.BluRay.REMUX',
            'resolution': '1080p',
            'source': 'BluRay',
            'type': 'REMUX',
            'video_codec': 'x265',
            'tag': 'GROUP'
        }
        
        result = self.app._build_scene_name(meta)
        self.assertIn('REMUX', result)
        self.assertIn('BluRay', result)


def run_tests():
    """Esegue tutti i test"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMKVRenameAssistant))
    suite.addTests(loader.loadTestsFromTestCase(TestSceneNamingRules))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("MKV Rename Assistant - Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ Tutti i test sono passati!")
    else:
        print("\n❌ Alcuni test sono falliti!")
        
    print("\nPer eseguire l'applicazione principale:")
    print("python mkv_rename_assistant.py")