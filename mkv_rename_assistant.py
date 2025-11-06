# -*- coding: utf-8 -*-
"""
MKV Rename Assistant - GUI Application
Rinomina file MKV secondo le regole della scena basandosi sul codice SHRI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from pathlib import Path
from pymediainfo import MediaInfo
import json
from config import RENAME_CONFIG, GUI_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES


class MKVRenameAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title(GUI_CONFIG["window_title"])
        self.root.geometry(GUI_CONFIG["window_size"])
        self.root.resizable(True, True)
        
        # Variabili
        self.current_file = tk.StringVar()
        self.current_name = tk.StringVar()
        self.new_name = tk.StringVar()
        self.mediainfo_data = None
        
        # Pattern regex dal codice SHRI
        self.INVALID_TAG_PATTERN = re.compile(r"-(nogrp|nogroup|unknown|unk)", re.IGNORECASE)
        self.WHITESPACE_PATTERN = re.compile(r"\s{2,}")
        self.MARKER_PATTERN = re.compile(r"\b(" + "|".join(RENAME_CONFIG["remux_markers"]) + r")\b", re.IGNORECASE)
        self.CINEMA_NEWS_PATTERN = re.compile(r"\b(HDTS|TS|MD|LD|CAM|HDCAM|TC|HDTC)\b", re.IGNORECASE)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurazione della griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="MKV Rename Assistant", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Selezione file
        ttk.Label(main_frame, text="File MKV:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.current_file, width=60).grid(
            row=1, column=1, sticky="ew", pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="Sfoglia...", 
                  command=self.browse_file).grid(row=1, column=2, pady=5)
        
        # Nome attuale
        ttk.Label(main_frame, text="Nome attuale:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.current_name, width=60, 
                 state="readonly").grid(row=2, column=1, columnspan=2, 
                                       sticky="ew", pady=5, padx=(10, 0))
        
        # Pulsante analizza
        ttk.Button(main_frame, text="Analizza File", 
                  command=self.analyze_file).grid(row=3, column=1, pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Informazioni file
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni File", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        # Testo informazioni
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.grid(row=0, column=0, sticky="nsew")
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        
        info_frame.rowconfigure(0, weight=1)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=6, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Nome nuovo
        ttk.Label(main_frame, text="Nuovo nome:").grid(row=7, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.new_name, width=60).grid(
            row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Genera Nome", 
                  command=self.generate_name).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Rinomina File", 
                  command=self.rename_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_form).pack(side=tk.LEFT)
        
        main_frame.rowconfigure(5, weight=1)
        
    def browse_file(self):
        """Apre dialog per selezionare file MKV"""
        filename = filedialog.askopenfilename(
            title="Seleziona file MKV",
            filetypes=GUI_CONFIG["supported_filetypes"]
        )
        if filename:
            self.current_file.set(filename)
            self.current_name.set(os.path.basename(filename))
            self.info_text.delete(1.0, tk.END)
            self.new_name.set("")
            
    def analyze_file(self):
        """Analizza il file MKV selezionato"""
        if not self.current_file.get():
            messagebox.showerror("Errore", ERROR_MESSAGES["no_file_selected"])
            return
            
        if not os.path.exists(self.current_file.get()):
            messagebox.showerror("Errore", ERROR_MESSAGES["file_not_exists"])
            return
            
        try:
            # Analizza con MediaInfo
            self.mediainfo_data = MediaInfo.parse(self.current_file.get())
            self.display_file_info()
            messagebox.showinfo("Successo", SUCCESS_MESSAGES["analysis_complete"])
            
        except Exception as e:
            messagebox.showerror("Errore", f"{ERROR_MESSAGES['analysis_error']}\n{str(e)}")
            
    def display_file_info(self):
        """Mostra le informazioni complete del file nella text area"""
        if not self.mediainfo_data:
            return
            
        self.info_text.delete(1.0, tk.END)
        
        # Info generali
        general_track = next((track for track in self.mediainfo_data.tracks 
                            if track.track_type == 'General'), None)
        
        if general_track:
            self.info_text.insert(tk.END, "=== INFORMAZIONI GENERALI ===\n")
            self.info_text.insert(tk.END, f"Nome file: {general_track.file_name}\n")
            if general_track.file_size:
                size_gb = int(general_track.file_size) / (1024**3)
                self.info_text.insert(tk.END, f"Dimensione: {size_gb:.2f} GB\n")
            if general_track.duration:
                duration_min = int(general_track.duration) / 60000
                self.info_text.insert(tk.END, f"Durata: {duration_min:.0f} minuti\n")
            if hasattr(general_track, 'overall_bit_rate') and general_track.overall_bit_rate:
                bitrate_mbps = int(general_track.overall_bit_rate) / 1000000
                self.info_text.insert(tk.END, f"Bitrate totale: {bitrate_mbps:.1f} Mbps\n")
            self.info_text.insert(tk.END, "\n")
        
        # Info video dettagliate
        video_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Video']
        
        if video_tracks:
            self.info_text.insert(tk.END, "=== VIDEO (DETTAGLIATO) ===\n")
            for i, track in enumerate(video_tracks):
                self.info_text.insert(tk.END, f"Track {i+1}:\n")
                
                # Info base
                self.info_text.insert(tk.END, f"  Codec: {track.format or 'N/A'}")
                if hasattr(track, 'format_profile') and track.format_profile:
                    self.info_text.insert(tk.END, f" ({track.format_profile})")
                self.info_text.insert(tk.END, "\n")
                
                self.info_text.insert(tk.END, f"  Risoluzione: {track.width}x{track.height}\n")
                
                if track.bit_rate:
                    bitrate_mbps = int(track.bit_rate) / 1000000
                    self.info_text.insert(tk.END, f"  Bitrate: {bitrate_mbps:.1f} Mbps\n")
                    
                if track.frame_rate:
                    self.info_text.insert(tk.END, f"  Frame rate: {track.frame_rate} fps\n")
                
                # Informazioni di encoding
                if hasattr(track, 'writing_library') and track.writing_library:
                    self.info_text.insert(tk.END, f"  Writing library: {track.writing_library}\n")
                    
                if hasattr(track, 'encoded_library_settings') and track.encoded_library_settings:
                    settings = str(track.encoded_library_settings)
                    if len(settings) > 60:
                        settings = settings[:60] + "..."
                    self.info_text.insert(tk.END, f"  Encoded settings: {settings}\n")
                
                # Informazioni HDR/DV
                if hasattr(track, 'hdr_format') and track.hdr_format:
                    self.info_text.insert(tk.END, f"  HDR Format: {track.hdr_format}\n")
                    
                if hasattr(track, 'hdr_format_profile') and track.hdr_format_profile:
                    self.info_text.insert(tk.END, f"  HDR Profile: {track.hdr_format_profile}\n")
                    
                if hasattr(track, 'hdr_format_compatibility') and track.hdr_format_compatibility:
                    self.info_text.insert(tk.END, f"  HDR Compatibility: {track.hdr_format_compatibility}\n")
                    
                if hasattr(track, 'color_primaries') and track.color_primaries:
                    self.info_text.insert(tk.END, f"  Color primaries: {track.color_primaries}\n")
                    
                if hasattr(track, 'transfer_characteristics') and track.transfer_characteristics:
                    self.info_text.insert(tk.END, f"  Transfer characteristics: {track.transfer_characteristics}\n")
                
                # Bit depth
                if hasattr(track, 'bit_depth') and track.bit_depth:
                    self.info_text.insert(tk.END, f"  Bit depth: {track.bit_depth} bits\n")
                
                self.info_text.insert(tk.END, "\n")
        
        # Info audio dettagliate
        audio_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Audio']
        
        if audio_tracks:
            self.info_text.insert(tk.END, "=== AUDIO (DETTAGLIATO) ===\n")
            for i, track in enumerate(audio_tracks):
                self.info_text.insert(tk.END, f"Track {i+1}:\n")
                
                # Info base
                self.info_text.insert(tk.END, f"  Formato: {track.format or 'N/A'}")
                if hasattr(track, 'format_profile') and track.format_profile:
                    self.info_text.insert(tk.END, f" ({track.format_profile})")
                self.info_text.insert(tk.END, "\n")
                
                # Nome commerciale
                if hasattr(track, 'format_commercial_ifany') and track.format_commercial_ifany:
                    self.info_text.insert(tk.END, f"  Nome commerciale: {track.format_commercial_ifany}\n")
                
                self.info_text.insert(tk.END, f"  Lingua: {track.language or 'N/A'}\n")
                self.info_text.insert(tk.END, f"  Canali: {track.channel_s or 'N/A'}\n")
                
                if track.bit_rate:
                    bitrate_kbps = int(track.bit_rate) / 1000
                    self.info_text.insert(tk.END, f"  Bitrate: {bitrate_kbps:.0f} kbps\n")
                
                # Informazioni aggiuntive audio
                if hasattr(track, 'format_additionalfeatures') and track.format_additionalfeatures:
                    self.info_text.insert(tk.END, f"  Features: {track.format_additionalfeatures}\n")
                    
                if hasattr(track, 'compression_mode') and track.compression_mode:
                    self.info_text.insert(tk.END, f"  Compression: {track.compression_mode}\n")
                
                # Titolo del track (se presente)
                if hasattr(track, 'title') and track.title:
                    self.info_text.insert(tk.END, f"  Titolo: {track.title}\n")
                
                self.info_text.insert(tk.END, "\n")
        
        # Info sottotitoli dettagliate
        text_tracks = [track for track in self.mediainfo_data.tracks 
                      if track.track_type == 'Text']
        
        if text_tracks:
            self.info_text.insert(tk.END, "=== SOTTOTITOLI (DETTAGLIATO) ===\n")
            for i, track in enumerate(text_tracks):
                self.info_text.insert(tk.END, f"Track {i+1}:\n")
                self.info_text.insert(tk.END, f"  Formato: {track.format or 'N/A'}\n")
                self.info_text.insert(tk.END, f"  Lingua: {track.language or 'N/A'}\n")
                
                # Titolo del sottotitolo
                if hasattr(track, 'title') and track.title:
                    self.info_text.insert(tk.END, f"  Titolo: {track.title}\n")
                    
                # Codec ID
                if hasattr(track, 'codec_id') and track.codec_id:
                    self.info_text.insert(tk.END, f"  Codec ID: {track.codec_id}\n")
                
                self.info_text.insert(tk.END, "\n")
        
        # Sezione metadati estratti per il rename
        self.info_text.insert(tk.END, "=== METADATI ESTRATTI PER RENAME ===\n")
        try:
            meta = self.extract_metadata()
            self.info_text.insert(tk.END, f"Risoluzione rilevata: {meta.get('resolution', 'N/A')}\n")
            self.info_text.insert(tk.END, f"Formato: {meta.get('video_format', 'N/A')}\n")
            # Per REMUX e WEB-DL puro non mostra compressore (non sono compressi)
            compressor_value = meta.get('compressor', 'Non applicabile' if meta.get('type') in ['REMUX', 'WEBDL'] else 'N/A')
            self.info_text.insert(tk.END, f"Compressore: {compressor_value}\n")
            self.info_text.insert(tk.END, f"Tipo rilevato: {meta.get('type', 'N/A')}\n")
            self.info_text.insert(tk.END, f"Source rilevato: {meta.get('source', 'N/A')}\n")
            self.info_text.insert(tk.END, f"Audio rilevato: {meta.get('audio', 'N/A')}\n")
            self.info_text.insert(tk.END, f"Lingue audio: {', '.join(meta.get('audio_languages', []))}\n")
            self.info_text.insert(tk.END, f"HDR rilevato: {', '.join(meta.get('hdr_info', []))}\n")
            self.info_text.insert(tk.END, f"Servizio: {meta.get('service', 'N/A')}\n")
            self.info_text.insert(tk.END, f"Release group: {meta.get('tag', 'N/A')}\n")
            
            # Verifica REMUX basata sui metadati corretti
            tipo = meta.get('type', '').upper()
            is_remux = tipo == 'REMUX'
            self.info_text.insert(tk.END, f"È REMUX?: {'Sì' if is_remux else 'No'}\n")
            
        except Exception as e:
            self.info_text.insert(tk.END, f"Errore estrazione metadati: {e}\n")
                
    def extract_metadata(self):
        """Estrae metadati necessari per la rinomina"""
        if not self.mediainfo_data:
            return {}
            
        meta = {}
        
        # Tracks
        general_track = next((track for track in self.mediainfo_data.tracks 
                            if track.track_type == 'General'), None)
        video_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Video']
        audio_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Audio']
        text_tracks = [track for track in self.mediainfo_data.tracks 
                      if track.track_type == 'Text']
        
        # Nome file originale
        if general_track and general_track.file_name:
            meta['name'] = general_track.file_name
            meta['basename'] = os.path.splitext(general_track.file_name)[0]
        
        # Risoluzione - logica migliorata per gestire aspect ratio diversi
        if video_tracks and video_tracks[0].width and video_tracks[0].height:
            width = int(video_tracks[0].width)
            height = int(video_tracks[0].height)
            
            # Classifica basandosi sulla dimensione maggiore per evitare problemi con aspect ratio diversi
            if width >= 3840 or height >= 2160:
                meta['resolution'] = '2160p'
            elif width >= 1920 or height >= 1080:
                # Se larghezza è 1920+ o altezza è 1080+ classifico come 1080p 
                # Esempi: 1920x1080 = 1080p, 1920x804 = 1080p (widescreen), 1440x1080 = 1080p
                meta['resolution'] = '1080p'
            elif width >= 1280 or height >= 720:
                meta['resolution'] = '720p'
            elif height >= 576:
                meta['resolution'] = '576p'
            elif height >= 480:
                meta['resolution'] = '480p'
            else:
                meta['resolution'] = f'{height}p'
        
        # Formato e codec video
        if video_tracks and video_tracks[0].format:
            codec = video_tracks[0].format.upper()
            if 'HEVC' in codec or 'H.265' in codec:
                meta['video_format'] = 'HEVC'
                meta['video_codec'] = 'x265'
                meta['compressor'] = 'x265'
            elif 'AVC' in codec or 'H.264' in codec:
                meta['video_format'] = 'AVC'
                meta['video_codec'] = 'x264'
                meta['compressor'] = 'x264'
            else:
                meta['video_format'] = codec
                meta['video_codec'] = codec
                meta['compressor'] = codec
        
        # Source - cerca di dedurre dalla risoluzione e altre info
        if 'resolution' in meta:
            # Usa basename o current_file come fallback
            basename = meta.get('basename', '')
            if not basename:
                basename = os.path.basename(self.current_file.get())
            filename_upper = basename.upper()
            
            # PRIORITÀ 1: Controlla se è una serie TV (S01E01) - quasi sempre WEB
            if self._is_tv_series(basename):
                meta['source'] = 'WEB'
                # Prima controlla marker espliciti WEBRip
                if any(keyword in filename_upper for keyword in ['WEBRIP', 'WEB.RIP', 'WEB-RIP']):
                    meta['type'] = 'WEBRIP'
                # Poi controlla se ha writing library encoded (indica WEBRip)
                elif self._has_encoded_writing_library():
                    meta['type'] = 'WEBRIP'
                # Se ha marker WEB-DL ma NO writing library, è WEB-DL puro
                elif any(keyword in filename_upper for keyword in ['WEB-DL', 'WEBDL', 'WEB.DL', 'DLMUX', 'WEBMUX']):
                    meta['type'] = 'WEBDL'
                else:
                    # Default per serie TV senza marker è WEB-DL
                    meta['type'] = 'WEBDL'
            # PRIORITÀ 2: Marker espliciti WEB-DL/WEBRip (per film)
            elif any(keyword in filename_upper for keyword in ['WEB-DL', 'WEBDL', 'WEB.DL', 'DLMUX', 'WEBMUX']):
                meta['source'] = 'WEB'
                # Se troviamo x264/x265 nella writing library, è un WEBRip
                if self._has_encoded_writing_library():
                    meta['type'] = 'WEBRIP'
                else:
                    meta['type'] = 'WEBDL'
            elif any(keyword in filename_upper for keyword in ['WEBRIP', 'WEB.RIP', 'WEB-RIP']):
                meta['source'] = 'WEB' 
                meta['type'] = 'WEBRIP'
            elif any(service in filename_upper for service in ['AMZN', 'NETFLIX', 'DSNP', 'HULU', 'ATVP']):
                meta['source'] = 'WEB'
                meta['type'] = 'WEBDL'  # Default per servizi streaming
            # PRIORITÀ 3: Risoluzione alta - solo per film senza marker serie
            elif meta['resolution'] in ['2160p', '1080p']:
                # Determina se è REMUX o ENCODE basandosi su analisi MediaInfo
                if self._is_remux():
                    meta['source'] = 'BluRay'
                    meta['type'] = 'REMUX'
                else:
                    # È un ENCODE se non è REMUX
                    meta['source'] = 'BluRay'
                    meta['type'] = 'ENCODE'
            elif meta['resolution'] == '720p':
                meta['source'] = 'BluRay'
                meta['type'] = 'ENCODE'
            else:
                meta['source'] = 'DVD'
                meta['type'] = 'DVDRIP'
        
        # Rimuovi compressore per file non compressi (REMUX e WEB-DL puro)
        if meta.get('type') in ['REMUX', 'WEBDL'] and 'compressor' in meta:
            del meta['compressor']
        
        # Audio - prendi il primo track audio
        if audio_tracks:
            audio_track = audio_tracks[0]
            meta['audio'] = self._get_audio_format(audio_track)
            
            # Lingue audio
            languages = []
            for track in audio_tracks:
                if track.language:
                    lang = self._normalize_language(track.language)
                    if lang and lang not in languages:
                        languages.append(lang)
            meta['audio_languages'] = languages
        
        # Servizio streaming - cerca nel nome del file
        filename_upper = meta.get('basename', '').upper()
        for service_key in ['AMZN', 'NETFLIX', 'NF', 'DSNP', 'DISNEY', 'HULU', 'ATVP', 'APPLE']:
            if service_key in filename_upper:
                meta['service'] = service_key
                break
        
        # HDR info - estrai dai metadati MediaInfo
        meta['hdr_info'] = self._get_hdr_info(meta)
        
        # Tag del release group
        meta['tag'] = self._extract_release_group()
        
        return meta
    
    def _is_remux(self):
        """Determina se il file è un REMUX controllando marker nel nome e MediaInfo"""
        if not self.mediainfo_data:
            return False
            
        # Controlla il nome del file per marker REMUX espliciti
        filename = os.path.basename(self.current_file.get()).upper()
        if 'REMUX' in filename:
            return True
            
        # Controlla per marker VU/UNTOUCHED
        if self.MARKER_PATTERN.search(filename):
            return True
        
        # Analisi MediaInfo per determinare se è encoded
        video_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Video']
        
        if video_tracks:
            track = video_tracks[0]
            
            # Controlla Writing library - se contiene x264/x265/encoder è sicuramente un ENCODE
            writing_library = getattr(track, 'writing_library', '') or ''
            writing_library = str(writing_library).lower()
            
            # Se trova evidenza di encoding, NON è un REMUX
            encoding_indicators = [
                'x264', 'x265', 'handbrake', 'ffmpeg', 'mencoder', 
                'staxrip', 'megui', 'xvid', 'divx', 'encoder'
            ]
            
            for indicator in encoding_indicators:
                if indicator in writing_library:
                    return False  # È un ENCODE, non un REMUX
            
            # Controlla anche Encoded_Library_Settings per segni di encoding
            encoded_settings = getattr(track, 'encoded_library_settings', '') or ''
            encoded_settings = str(encoded_settings).lower()
            
            if encoded_settings and not isinstance(encoded_settings, dict):
                # Se ci sono impostazioni di encoding, è un ENCODE
                encoding_settings_indicators = ['crf=', 'bitrate=', 'preset=', 'tune=']
                for indicator in encoding_settings_indicators:
                    if indicator in encoded_settings:
                        return False  # È un ENCODE
            
            # Controlla Format_Settings per segni di encoding
            format_settings = getattr(track, 'format_settings', '') or ''
            format_settings = str(format_settings).lower()
            
            if 'cabac' in format_settings or 'bframes' in format_settings:
                # Queste impostazioni indicano encoding, non remux
                return False
                
        # Se non trova marker REMUX nel nome E non trova evidenza di encoding
        # considera il bitrate per una decisione finale
        if video_tracks:
            track = video_tracks[0]
            bitrate = getattr(track, 'bit_rate', None)
            
            if bitrate:
                try:
                    bitrate_mbps = int(bitrate) / 1000000
                    # REMUX di solito hanno bitrate molto alti (>15 Mbps per 1080p)
                    if bitrate_mbps > 15:
                        return True
                except (ValueError, TypeError):
                    pass
                
        return False
    
    def _has_encoded_writing_library(self):
        """Controlla se la writing library indica che il file è stato encodato (x264/x265)"""
        if not self.mediainfo_data:
            return False
            
        video_tracks = [track for track in self.mediainfo_data.tracks 
                       if track.track_type == 'Video']
        
        if video_tracks:
            track = video_tracks[0]
            
            # Controlla Writing library per encoding indicators
            writing_library = getattr(track, 'writing_library', '') or ''
            writing_library = str(writing_library).lower()
            
            # Indicatori di encoding che suggeriscono WEBRip invece di WEB-DL
            encoding_indicators = [
                'x264', 'x265', 'handbrake', 'ffmpeg', 'mencoder', 
                'staxrip', 'megui', 'xvid', 'divx', 'encoder'
            ]
            
            for indicator in encoding_indicators:
                if indicator in writing_library:
                    return True  # È stato encodato - WEBRip
                    
            # Controlla anche Encoded_Library_Settings
            encoded_settings = getattr(track, 'encoded_library_settings', '') or ''
            encoded_settings = str(encoded_settings).lower()
            
            if encoded_settings:
                encoding_settings_indicators = ['crf=', 'bitrate=', 'preset=', 'tune=']
                for indicator in encoding_settings_indicators:
                    if indicator in encoded_settings:
                        return True  # È stato encodato - WEBRip
                        
        return False  # Non trova indicatori di encoding - WEB-DL
    
    def _is_tv_series(self, filename):
        """Controlla se il file è una serie TV basandosi sul formato S01E01"""
        series_pattern = r'S\d+E\d+'
        return re.search(series_pattern, filename, re.IGNORECASE) is not None
    
    def _get_audio_format(self, audio_track):
        """Ottiene il formato audio dettagliato secondo gli esempi"""
        if not audio_track.format:
            return 'Unknown'
            
        fmt = audio_track.format.upper()
        channels = getattr(audio_track, 'channel_s', '2')
        
        # Determina il numero di canali
        channel_count = str(channels)
        if channel_count == '6':
            channel_suffix = '5.1'
        elif channel_count == '8':
            channel_suffix = '7.1'
        elif channel_count == '2':
            channel_suffix = '2.0'
        else:
            channel_suffix = channel_count
        
        # Controlla per Atmos
        has_atmos = False
        if hasattr(audio_track, 'format_additionalfeatures'):
            features = str(audio_track.format_additionalfeatures).upper()
            has_atmos = 'ATMOS' in features or 'JOC' in features
        
        # Mappa secondo gli esempi
        if fmt == 'AC-3':
            return f'DD{channel_suffix}'
        elif fmt == 'E-AC-3':
            if has_atmos:
                return f'DDP{channel_suffix}.Atmos'
            return f'DDP{channel_suffix}'
        elif fmt == 'TRUEHD' or fmt == 'MLP FBA':
            if has_atmos:
                return f'TrueHD.Atmos.{channel_suffix}'
            return f'TrueHD.{channel_suffix}'
        elif fmt == 'DTS-HD MA':
            return f'DTS-HD.MA.{channel_suffix}'
        elif fmt == 'DTS':
            return f'DTS.{channel_suffix}'
        else:
            return RENAME_CONFIG["audio_format_mapping"].get(fmt, fmt)
    
    def _normalize_language(self, language):
        """Normalizza i codici lingua"""
        if not language:
            return None
            
        lang = language.lower()
        
        # Usa il mapping dalla configurazione
        return RENAME_CONFIG["language_mapping"].get(lang, language.upper())
    
    def _extract_release_group(self):
        """Estrae il release group dal nome del file"""
        filename = os.path.basename(self.current_file.get())
        name_no_ext = os.path.splitext(filename)[0]
        
        # Cerca pattern comune: Nome-Group
        parts = re.split(r'[-.]', name_no_ext)
        if len(parts) > 1:
            potential_tag = parts[-1].strip()
            
            # Verifica che non sia un tag invalido
            if (potential_tag and 
                not self.INVALID_TAG_PATTERN.search(potential_tag) and
                len(potential_tag) <= 30 and
                potential_tag.replace('_', '').isalnum()):
                return potential_tag
                
        return RENAME_CONFIG["default_release_group"]
    
    def generate_name(self):
        """Genera il nuovo nome secondo le regole della scena"""
        if not self.mediainfo_data:
            messagebox.showerror("Errore", ERROR_MESSAGES["no_file_selected"])
            return
            
        try:
            meta = self.extract_metadata()
            new_name = self._build_scene_name(meta)
            self.new_name.set(new_name)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la generazione del nome:\n{str(e)}")
    
    def _build_scene_name(self, meta):
        """Costruisce il nome secondo le regole della scena basandosi sugli esempi forniti"""
        # Estrai informazioni dal nome originale
        original_name = meta.get('basename', '')
        
        # Cerca di estrarre titolo e anno
        title, year = self._extract_title_year(original_name)
        
        # Inizializza componenti
        components = []
        
        # Titolo e anno
        if title:
            components.append(title.replace(' ', '.'))
            
        # Controlla se è una serie TV (ha info episodio)
        is_series = hasattr(self, '_temp_series')
        
        # Anno - solo se presente (non più anno di default)
        if year:
            components.append(year)
            
        # Aggiungi info serie se presente
        if is_series:
            components.append(self._temp_series)
            delattr(self, '_temp_series')  # Pulisci dopo l'uso
        
        # Determina il tipo di release
        release_type = meta.get('type', 'ENCODE')
        
        # Costruzione specifica per tipo
        if release_type == 'REMUX':
            # Pattern REMUX: Title.Year.UHD.BluRay.Resolution.Audio.Codec.REMUX-Group
            # Es: Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd
            
            # UHD per 2160p
            if meta.get('resolution') == '2160p':
                components.append('UHD')
            
            # Source
            if meta.get('source'):
                components.append(meta['source'])
            
            # Resolution
            if meta.get('resolution'):
                components.append(meta['resolution'])
            
            # Audio dettagliato
            if meta.get('audio'):
                components.append(meta['audio'])
            
            # Codec video (HVEC per HEVC, AVC per AVC)
            video_codec = self._get_remux_codec(meta)
            if video_codec:
                components.append(video_codec)
            
            # REMUX marker
            components.append('REMUX')
            
        elif release_type in ['WEBDL', 'WEBRIP']:
            # Pattern WEB-DL: Title.Year.Resolution.Service.WEB-DL.Audio.HDR.Codec-Group
            # Es: Hedda.2025.2160p.AMZN.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-FHC
            
            # Resolution
            if meta.get('resolution'):
                components.append(meta['resolution'])
            
            # Service
            service = self._get_service_name(meta)
            if service:
                components.append(service)
            
            # Type
            type_str = 'WEB-DL' if release_type == 'WEBDL' else 'WEBRip'
            components.append(type_str)
            
            # Audio
            if meta.get('audio'):
                components.append(meta['audio'])
            
            # HDR info
            hdr_info = meta.get('hdr_info', [])
            if hdr_info:
                components.extend(hdr_info)
            
            # Codec video - formato diverso per WEB-DL vs WEBRip
            if release_type == 'WEBDL':
                # WEB-DL usa H.264/H.265
                video_codec = self._get_webdl_codec(meta)
            else:
                # WEBRip usa x264/x265 
                video_codec = self._get_encode_codec(meta)
            
            if video_codec:
                components.append(video_codec)
                
        else:
            # Pattern ENCODE: Title.Year.Resolution.Source.Audio.HDR.Codec-Group  
            # Es: Black.Dog.2024.1080p.BluRay.DD5.1.x264-iSlaNd
            # Es: Godzilla.1.2014.2160p.BluRay.DDP5.1.DV.HDR10.x265-Tib7
            
            # Resolution
            if meta.get('resolution'):
                components.append(meta['resolution'])
            
            # Source
            if meta.get('source'):
                components.append(meta['source'])
            
            # Audio
            if meta.get('audio'):
                components.append(meta['audio'])
            
            # HDR info per ENCODE
            hdr_info = meta.get('hdr_info', [])
            if hdr_info:
                components.extend(hdr_info)
            
            # Codec video (x264/x265)
            video_codec = self._get_encode_codec(meta)
            if video_codec:
                components.append(video_codec)
        
        # Unisci componenti
        name = '.'.join(filter(None, components))
        
        # Aggiungi release group
        if meta.get('tag') and meta['tag'] != 'NoGroup':
            name += f"-{meta['tag']}"
        
        # Pulisci spazi multipli e caratteri non validi
        name = self.WHITESPACE_PATTERN.sub('.', name)
        name = re.sub(r'\.{2,}', '.', name)  # Rimuovi punti multipli
        
        return name + '.mkv'
    
    def _get_remux_codec(self, meta):
        """Ottiene il codec per REMUX (HVEC/AVC format)"""
        codec = meta.get('video_codec', '')
        mapping = {
            'x265': 'HVEC',
            'HEVC': 'HVEC', 
            'H.265': 'HVEC',
            'x264': 'AVC',
            'AVC': 'AVC',
            'H.264': 'AVC'
        }
        return mapping.get(codec, codec)
    
    def _get_webdl_codec(self, meta):
        """Ottiene il codec per WEB-DL (H.264/H.265 format)"""
        codec = meta.get('video_codec', '')
        mapping = {
            'x265': 'H.265',
            'HEVC': 'H.265',
            'H.265': 'H.265', 
            'x264': 'H.264',
            'AVC': 'H.264',
            'H.264': 'H.264'
        }
        return mapping.get(codec, codec)
    
    def _get_encode_codec(self, meta):
        """Ottiene il codec per ENCODE (x264/x265 format)"""
        codec = meta.get('video_codec', '')
        mapping = {
            'HEVC': 'x265',
            'H.265': 'x265',
            'AVC': 'x264', 
            'H.264': 'x264'
        }
        return mapping.get(codec, codec)
    
    def _get_service_name(self, meta):
        """Ottiene il nome del servizio streaming"""
        service = meta.get('service', '')
        if not service:
            # Prova a dedurre dal nome del file
            filename = meta.get('basename', '').upper()
            if 'AMZN' in filename or 'AMAZON' in filename:
                return 'AMZN'
            elif 'NETFLIX' in filename or 'NF.' in filename:
                return 'NF'
            elif 'DISNEY' in filename or 'DSNP' in filename:
                return 'DSNP'
        
        return RENAME_CONFIG["service_mapping"].get(service, service)
    
    def _get_hdr_info(self, meta):
        """Ottiene informazioni HDR/DV dai metadati MediaInfo"""
        hdr_components = []
        
        # Prima controlla i metadati MediaInfo per informazioni HDR reali
        if self.mediainfo_data:
            video_tracks = [track for track in self.mediainfo_data.tracks 
                           if track.track_type == 'Video']
            
            if video_tracks:
                track = video_tracks[0]
                
                # Controlla HDR Format per Dolby Vision
                hdr_format = getattr(track, 'hdr_format', '') or ''
                hdr_format = str(hdr_format).lower()
                
                if 'dolby vision' in hdr_format or 'dv' in hdr_format:
                    hdr_components.append('DV')
                
                # Controlla HDR Format Profile per dettagli aggiuntivi
                hdr_format_profile = getattr(track, 'hdr_format_profile', '') or ''
                hdr_format_profile = str(hdr_format_profile).lower()
                
                # Cerca profile Dolby Vision (dvhe.xx.xx)
                if 'dvhe.' in hdr_format_profile:
                    if 'DV' not in hdr_components:
                        hdr_components.append('DV')
                
                # Controlla HDR Format Compatibility per HDR10
                hdr_compatibility = getattr(track, 'hdr_format_compatibility', '') or ''
                hdr_compatibility = str(hdr_compatibility).lower()
                
                if 'hdr10' in hdr_compatibility:
                    hdr_components.append('HDR10')
                elif 'hdr' in hdr_compatibility and 'hdr10' not in hdr_components:
                    hdr_components.append('HDR')
                
                # Controlla anche altri campi HDR
                hdr_format_settings = getattr(track, 'hdr_format_settings', '') or ''
                hdr_format_settings = str(hdr_format_settings).lower()
                
                if 'hdr10' in hdr_format_settings and 'HDR10' not in hdr_components:
                    hdr_components.append('HDR10')
                
                # Controlla Color primaries per BT.2020 (indicativo di HDR)
                color_primaries = getattr(track, 'color_primaries', '') or ''
                transfer_characteristics = getattr(track, 'transfer_characteristics', '') or ''
                
                if 'bt.2020' in str(color_primaries).lower() or 'bt2020' in str(color_primaries).lower():
                    if not hdr_components:  # Solo se non abbiamo già trovato info HDR
                        if 'smpte st 2084' in str(transfer_characteristics).lower() or 'pq' in str(transfer_characteristics).lower():
                            hdr_components.append('HDR10')
                        elif 'arib std-b67' in str(transfer_characteristics).lower() or 'hlg' in str(transfer_characteristics).lower():
                            hdr_components.append('HLG')
                        else:
                            hdr_components.append('HDR')
        
        # Se non trova nulla nei metadati, cerca nel nome del file come fallback
        if not hdr_components:
            filename = meta.get('basename', '').upper()
            
            if 'DV' in filename or 'DOLBY.VISION' in filename:
                hdr_components.append('DV')
            
            if 'HDR10' in filename:
                hdr_components.append('HDR10') 
            elif 'HDR' in filename and 'HDR10' not in filename:
                hdr_components.append('HDR')
        
        # Rimuovi duplicati mantenendo ordine
        seen = set()
        result = []
        for item in hdr_components:
            if item not in seen:
                seen.add(item)
                result.append(item)
        
        return result
    
    def _extract_title_year(self, filename):
        """Estrae titolo e anno dal nome del file, con supporto serie TV"""
        # Pattern per serie TV con S01E01 - semplificato senza anno
        series_pattern = r'^(.*?)\s+S(\d+)E(\d+)'  # Titolo S01E01
        
        # Controlla prima se è una serie TV
        match = re.search(series_pattern, filename, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            season = match.group(2).zfill(2)  # S01
            episode = match.group(3).zfill(2)  # E01
            
            # Salva info serie (senza anno per ora)
            self._temp_series = f"S{season}E{episode}"
            
            return title, None  # Nessun anno automatico per serie TV
        
        # Pattern comuni per film/contenuti normali
        patterns = [
            r'^(.*?)\.(\d{4})\..*',  # Titolo.Anno.resto
            r'^(.*?)[\.\s](\d{4})[\.\s].*',  # Titolo Anno resto
            r'^(.*?)[\[\(](\d{4})[\]\)].*',  # Titolo [Anno] resto
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                title = match.group(1).replace('.', ' ').strip()
                year = match.group(2)
                return title, year
        
        # Se non trova l'anno, prova solo il titolo
        title_match = re.search(r'^([^\.]+)', filename)
        if title_match:
            title = title_match.group(1).replace('.', ' ').strip()
            return title, None
            
        return filename, None
    
    def rename_file(self):
        """Rinomina il file con il nuovo nome"""
        if not self.current_file.get():
            messagebox.showerror("Errore", ERROR_MESSAGES["no_file_selected"])
            return
            
        if not self.new_name.get():
            messagebox.showerror("Errore", ERROR_MESSAGES["no_new_name"])
            return
            
        current_path = Path(self.current_file.get())
        new_path = current_path.parent / self.new_name.get()
        
        if new_path.exists():
            messagebox.showerror("Errore", ERROR_MESSAGES["file_exists"])
            return
            
        try:
            current_path.rename(new_path)
            messagebox.showinfo("Successo", f"{SUCCESS_MESSAGES['rename_complete']}\n\nNuovo nome:\n{self.new_name.get()}")
            
            # Aggiorna i campi
            self.current_file.set(str(new_path))
            self.current_name.set(self.new_name.get())
            
        except Exception as e:
            messagebox.showerror("Errore", f"{ERROR_MESSAGES['rename_error']}\n{str(e)}")
    
    def reset_form(self):
        """Resetta il form"""
        self.current_file.set("")
        self.current_name.set("")
        self.new_name.set("")
        self.info_text.delete(1.0, tk.END)
        self.mediainfo_data = None


def main():
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()