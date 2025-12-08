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
import requests
from config import RENAME_CONFIG, GUI_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES

# Load TMDb API key from environment or config file
def load_tmdb_api_key():
    """Carica la chiave TMDb da variabile d'ambiente o file config"""
    # PRIORITÀ 1: Variabile d'ambiente (per deploy/CI-CD)
    api_key = os.getenv('TMDB_API_KEY', '').strip()
    if api_key:
        return api_key
    
    # PRIORITÀ 2: File config locale (.env style)
    config_file = Path(__file__).parent / '.tmdb_config'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                api_key = f.read().strip()
                if api_key:
                    return api_key
        except Exception:
            pass
    
    # PRIORITÀ 3: Se non trovata, ritorna stringa vuota
    return ''


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
        self.scene_title = tk.StringVar()
        self.mediainfo_data = None
        
        # Pattern regex dal codice SHRI
        self.INVALID_TAG_PATTERN = re.compile(r"^(nogrp|nogroup|unknown|unk)$", re.IGNORECASE)
        self.WHITESPACE_PATTERN = re.compile(r"\s{2,}")
        self.MARKER_PATTERN = re.compile(r"\b(" + "|".join(RENAME_CONFIG["remux_markers"]) + r")\b", re.IGNORECASE)
        self.CINEMA_NEWS_PATTERN = re.compile(r"\b(HDTS|TS|MD|LD|CAM|HDCAM|TC|HDTC)\b", re.IGNORECASE)
        
        # TMDb API configuration - Carica da ambiente/config o chiedi all'utente
        self.TMDB_API_KEY = load_tmdb_api_key()
        
        # Se non trovata, chiedi all'utente
        if not self.TMDB_API_KEY:
            self._prompt_for_tmdb_key()
        
        self.setup_ui()
    
    def _prompt_for_tmdb_key(self):
        """Chiede all'utente di inserire la chiave TMDb se non trovata"""
        from tkinter import simpledialog
        
        msg = "Chiave TMDb non trovata!\n\n" \
              "Inserisci la tua chiave API TMDb:\n" \
              "(Puoi ottenerla gratuitamente da https://www.themoviedb.org/settings/api)\n\n" \
              "La chiave verrà salvata e potrai modificarla dopo."
        
        api_key = simpledialog.askstring("TMDb API Key", msg, show='*')
        
        if api_key:
            self.TMDB_API_KEY = api_key.strip()
            # Salva la chiave nel file .tmdb_config (non committare in git)
            config_file = Path(__file__).parent / '.tmdb_config'
            try:
                with open(config_file, 'w') as f:
                    f.write(self.TMDB_API_KEY)
                messagebox.showinfo("Successo", "Chiave TMDb salvata localmente!")
            except Exception as e:
                messagebox.showwarning("Avviso", f"Impossibile salvare la chiave: {e}\nVerrà usata solo questa sessione.")
        else:
            # L'utente ha cancellato - avvisa che TMDb non funzionerà
            messagebox.showwarning("Attenzione", 
                                 "TMDb non sarà disponibile senza una chiave valida.\n"
                                 "La ricerca TMDb sarà disabilitata.")
            self.TMDB_API_KEY = ""
        
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
        
        # Frame TMDb
        tmdb_frame = ttk.LabelFrame(main_frame, text="Ricerca TMDb", padding="5")
        tmdb_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        tmdb_frame.columnconfigure(1, weight=1)
        
        ttk.Label(tmdb_frame, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5)
        self.content_type = tk.StringVar(value="movie")
        ttk.Radiobutton(tmdb_frame, text="Film", variable=self.content_type, 
                       value="movie").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(tmdb_frame, text="Serie TV", variable=self.content_type, 
                       value="tv").grid(row=0, column=2, sticky="w", padx=5)
        
        ttk.Label(tmdb_frame, text="Titolo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_title = tk.StringVar()
        ttk.Entry(tmdb_frame, textvariable=self.search_title, width=50).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(tmdb_frame, text="🔍 Cerca TMDb", 
                  command=self.search_tmdb).grid(row=1, column=2, padx=5, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=5, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Informazioni file
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni File", padding="10")
        info_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        # Testo informazioni
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.grid(row=0, column=0, sticky="nsew")
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        
        info_frame.rowconfigure(0, weight=1)
        
        # Separatore
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Nome nuovo
        ttk.Label(main_frame, text="Nuovo nome:").grid(row=8, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.new_name, width=60).grid(
            row=8, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))
        
        # Titolo Scene-Compliant (per tracker)
        ttk.Label(main_frame, text="Titolo Tracker:").grid(row=9, column=0, sticky="w", pady=5)
        self.scene_title = tk.StringVar()
        scene_entry = ttk.Entry(main_frame, textvariable=self.scene_title, width=60, state="readonly")
        scene_entry.grid(row=9, column=1, sticky="ew", pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="📋", width=3,
                  command=self.copy_scene_title).grid(row=9, column=2, pady=5, padx=0)
        
        # Pulsanti azione
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Genera Nome", 
                  command=self.generate_name).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Rinomina File", 
                  command=self.rename_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset", 
                  command=self.reset_form).pack(side=tk.LEFT)
        
        main_frame.rowconfigure(6, weight=1)
        
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
            
            # Auto-estrai titolo per ricerca TMDb
            normalized_title = self._normalize_title_for_search(os.path.basename(filename))
            self.search_title.set(normalized_title)
            
            # Avvia il processo automatico: Analisi → TMDb → Genera Nome
            self.root.after(100, self.auto_process_file)
    
    def auto_process_file(self):
        """Processo automatico: Analisi → TMDb → Selezione Manuale → Attesa Genera Nome"""
        try:
            # Step 1: Analisi MediaInfo
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Analisi file in corso...\n")
            self.root.update()
            
            if not self.current_file.get() or not os.path.exists(self.current_file.get()):
                messagebox.showerror("Errore", "File non valido")
                return
            
            # Analizza con MediaInfo
            self.mediainfo_data = MediaInfo.parse(self.current_file.get())
            self.info_text.insert(tk.END, "✅ Analisi MediaInfo completata\n")
            self.root.update()
            
            # Step 2: Ricerca TMDb automatica
            self.info_text.insert(tk.END, "Ricerca TMDb in corso...\n")
            self.root.update()
            
            title = self.search_title.get().strip()
            if title:
                # Determina tipo automaticamente (serie TV o film)
                if self._is_tv_series(os.path.basename(self.current_file.get())):
                    self.content_type.set("tv")
                else:
                    self.content_type.set("movie")
                
                # Cerca su TMDb e mostra dialog selezione
                self._search_and_select_tmdb(title)
            else:
                self.info_text.insert(tk.END, "⚠️ Nessun titolo da cercare\n")
            
            # Mostra informazioni complete del file
            self.display_file_info()
            
        except Exception as e:
            self.info_text.insert(tk.END, f"❌ Errore: {str(e)}\n")
            messagebox.showerror("Errore", f"Errore durante il processo:\n{str(e)}")
    
    def _search_and_select_tmdb(self, title):
        """Cerca su TMDb e permette selezione manuale del risultato corretto"""
        try:
            # Verifica che la chiave TMDb sia disponibile
            if not self.TMDB_API_KEY:
                self.info_text.insert(tk.END, "⚠️ Chiave TMDb non configurata\n")
                messagebox.showwarning("TMDb Non Disponibile", 
                                     "La chiave API TMDb non è stata configurata.\n"
                                     "Puoi comunque generare il nome con le informazioni del file.")
                return
            
            content_type = self.content_type.get()
            endpoint = "movie" if content_type == "movie" else "tv"
            
            # Ricerca su TMDb
            search_url = f"https://api.themoviedb.org/3/search/{endpoint}"
            params = {
                "api_key": self.TMDB_API_KEY,
                "query": title,
                "language": "it-IT"
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if not results:
                self.info_text.insert(tk.END, "⚠️ Nessun risultato TMDb trovato\n")
                messagebox.showinfo("TMDb", f"Nessun risultato trovato per '{title}'.\nPuoi comunque generare il nome con le informazioni attuali.")
                return
            
            self.info_text.insert(tk.END, f"✅ Trovati {len(results)} risultati TMDb\n")
            
            # Mostra SEMPRE il dialog di selezione per permettere all'utente di scegliere
            selected = self._show_tmdb_selection_dialog(results, endpoint)
            if selected:
                # Applica correzioni TMDb e avvia automaticamente il workflow
                corrected_name = self._apply_tmdb_correction(selected)
                self.info_text.insert(tk.END, f"✅ TMDb selezionato: {corrected_name}\n")
                
                # Avvia automaticamente la generazione del nome
                self.info_text.insert(tk.END, "🎯 Generazione nome automatica...\n")
                self.root.update()
                
                # Genera automaticamente il nome con i dati TMDb corretti
                try:
                    self.generate_name()
                    self.info_text.insert(tk.END, "✅ Nome generato con successo!\n")
                    
                    # Mostra il risultato all'utente (SENZA chiedere di rinominare)
                    title_tmdb = selected.get("title") or selected.get("name", "")
                    date = selected.get("release_date") or selected.get("first_air_date", "")
                    year_tmdb = date.split("-")[0] if date else ""
                    
                    msg = f"✅ Processo completato!\n\n"
                    msg += f"TMDb: {title_tmdb}"
                    if year_tmdb:
                        msg += f" ({year_tmdb})"
                    msg += f"\n\nNuovo nome generato:\n{self.new_name.get()}"
                    msg += f"\n\nTitolo Tracker:\n{self.scene_title.get()}"
                    msg += "\n\nRinomina quando sei pronto usando il pulsante 'Rinomina File'"
                    
                    messagebox.showinfo("Ricerca e Generazione Completate", msg)
                    
                except Exception as e:
                    self.info_text.insert(tk.END, f"❌ Errore generazione nome: {str(e)}\n")
            else:
                self.info_text.insert(tk.END, "⚠️ TMDb annullato - puoi comunque generare il nome manualmente\n")
                
        except Exception as e:
            self.info_text.insert(tk.END, f"❌ Errore ricerca TMDb: {str(e)}\n")
            messagebox.showerror("Errore TMDb", f"Errore durante la ricerca: {e}")
            
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
    

    
    def _apply_tmdb_correction(self, tmdb_result):
        """Applica le correzioni TMDb al nome del file temporaneo"""
        try:
            # Ottieni informazioni corrette da TMDb
            title = tmdb_result.get("title") or tmdb_result.get("name", "")
            date = tmdb_result.get("release_date") or tmdb_result.get("first_air_date", "")
            year = date.split("-")[0] if date else ""
            
            # Per serie TV, mantieni info episodio dal nome originale
            original_filename = os.path.basename(self.current_file.get())
            if self.content_type.get() == "tv":
                episode_match = re.search(r'(?i)(S\d{1,2}E\d{1,2})', original_filename)
                if episode_match:
                    episode_info = episode_match.group(1).upper()
                    corrected_name = f"{title} {episode_info}"
                else:
                    corrected_name = title
            else:
                corrected_name = title
            
            # Aggiungi anno se disponibile
            if year:
                if self.content_type.get() == "tv" and episode_match:
                    # Per serie: Titolo Anno S01E01
                    corrected_name = f"{title} {year} {episode_info}"
                else:
                    # Per film: Titolo Anno
                    corrected_name = f"{title} {year}"
            
            # Aggiorna temporaneamente il nome corrente per la generazione
            self._temp_corrected_name = corrected_name + ".mkv"
            
            return corrected_name
            
        except Exception as e:
            print(f"Errore correzione TMDb: {e}")
            return None
            
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
            # Estrai solo il nome file, scarta il percorso
            basename_with_ext = os.path.basename(general_track.file_name)
            meta['basename'] = os.path.splitext(basename_with_ext)[0]
        
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
        
        # Mappa secondo gli esempi (con spazi corretti)
        if fmt == 'AC-3':
            return f'DD {channel_suffix}'
        elif fmt == 'E-AC-3':
            if has_atmos:
                return f'DD+ {channel_suffix} Atmos'
            return f'DD+ {channel_suffix}'
        elif fmt == 'TRUEHD' or fmt == 'MLP FBA':
            if has_atmos:
                return f'TrueHD {channel_suffix} Atmos'
            return f'TrueHD {channel_suffix}'
        elif fmt == 'DTS-HD MA':
            return f'DTS-HD MA {channel_suffix}'
        elif fmt == 'DTS':
            return f'DTS {channel_suffix}'
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
            
            # Genera anche il titolo scene-compliant per il tracker
            # Se disponibile, usa i dati corretti da TMDb
            tmdb_title = getattr(self, '_temp_tmdb_title', None)
            tmdb_year = getattr(self, '_temp_tmdb_year', None)
            
            # Altrimenti estrai da nome originale
            if not tmdb_title:
                tmdb_title, tmdb_year = self._extract_title_year(meta.get('basename', ''))
            
            scene_title = self._generate_scene_compliant_title(tmdb_title=tmdb_title, tmdb_year=tmdb_year)
            self.scene_title.set(scene_title)
            
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
                
                # Controlla se HDR10 è nel hdr_format
                if 'hdr10' in hdr_format and 'HDR10' not in hdr_components:
                    hdr_components.append('HDR10')
                elif 'hdr' in hdr_format and 'hdr10' not in hdr_format and 'HDR' not in hdr_components and 'HDR10' not in hdr_components:
                    hdr_components.append('HDR')
                
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
        """Estrae titolo e anno dal nome del file, con supporto serie TV e correzione TMDb"""
        # PRIORITÀ 1: Usa il nome corretto da TMDb se disponibile
        if hasattr(self, '_temp_corrected_name'):
            corrected_filename = self._temp_corrected_name
            delattr(self, '_temp_corrected_name')  # Rimuovi dopo l'uso
            
            # Pattern per serie TV nel nome corretto TMDb
            series_pattern = r'^(.*?)\s+(\d{4})\s+S(\d+)E(\d+)'  # Titolo Anno S01E01
            match = re.search(series_pattern, corrected_filename, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                year = match.group(2)
                season = match.group(3).zfill(2)
                episode = match.group(4).zfill(2)
                self._temp_series = f"S{season}E{episode}"
                return title, year
            
            # Pattern per serie senza anno: Titolo S01E01
            series_pattern_no_year = r'^(.*?)\s+S(\d+)E(\d+)'
            match = re.search(series_pattern_no_year, corrected_filename, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                season = match.group(2).zfill(2)
                episode = match.group(3).zfill(2)
                self._temp_series = f"S{season}E{episode}"
                return title, None
            
            # Pattern per film: Titolo Anno
            film_pattern = r'^(.*?)\s+(\d{4})'
            match = re.search(film_pattern, corrected_filename)
            if match:
                title = match.group(1).strip()
                year = match.group(2)
                return title, year
            
            # Solo titolo (rimuovi .mkv se presente)
            clean_title = corrected_filename.replace('.mkv', '').strip()
            return clean_title, None
        
        # PRIORITÀ 2: Analisi del nome file originale (fallback)
        # Converti punti in spazi per analisi (ma senza modificare il filename originale)
        filename_normalized = filename.replace('.', ' ')
        
        # Pattern per serie TV con S01E01 - semplificato senza anno
        series_pattern = r'^(.*?)\s+S(\d+)E(\d+)'  # Titolo S01E01
        
        # Controlla prima se è una serie TV
        match = re.search(series_pattern, filename_normalized, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            season = match.group(2).zfill(2)  # S01
            episode = match.group(3).zfill(2)  # E01
            
            # Salva info serie (senza anno per ora)
            self._temp_series = f"S{season}E{episode}"
            
            return title, None  # Nessun anno automatico per serie TV
        
        # Pattern comuni per film/contenuti normali (usa filename_normalized)
        patterns = [
            r'^(.*?)\s+(\d{4})\s+.*',  # Titolo Anno resto (separati da spazi)
            r'^(.*?)[\[\(](\d{4})[\]\)].*',  # Titolo [Anno] resto
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename_normalized)
            if match:
                title = match.group(1).strip()
                year = match.group(2)
                return title, year
        
        # Se non trova l'anno, prova solo il titolo
        title_match = re.search(r'^([^\s]+.*?)(?:\s|$)', filename_normalized)
        if title_match:
            title = title_match.group(1).strip()
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
        self.scene_title.set("")
        self.info_text.delete(1.0, tk.END)
        self.mediainfo_data = None
    
    def copy_scene_title(self):
        """Copia il titolo scene-compliant negli appunti"""
        scene_title = self.scene_title.get()
        if not scene_title:
            messagebox.showwarning("Avviso", "Nessun titolo tracker disponibile.\nGenera prima il nome.")
            return
        
        try:
            # Copia negli appunti
            self.root.clipboard_clear()
            self.root.clipboard_append(scene_title)
            self.root.update()
            messagebox.showinfo("Successo", f"Titolo copiato negli appunti!\n\n{scene_title}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile copiare negli appunti:\n{str(e)}")
    
    def _generate_scene_compliant_title(self, tmdb_title=None, tmdb_year=None):
        """
        Genera il titolo scene-compliant per il tracker nel formato:
        Titolo Anno LINGUE RISOLUZIONE FONTE AUDIO_CODEC CANALI HDR_INFO CODEC_VIDEO-RELEASE_GROUP
        
        Esempi:
        - Warfare - Tempo di guerra 2025 ENGLISH - ITALIAN 1080p BluRay DD+ 5.1 x264-iSlaNd
        - The Abandons 2025 S01 ENGLISH - ITALIAN 2160p NF WEB-DL DD+ 5.1 DV HDR H.265-G66
        """
        if not self.mediainfo_data:
            return ""
        
        # Estrai metadati dal file
        meta = self.extract_metadata()
        
        # 1. TITOLO (da TMDb se disponibile, altrimenti dal file)
        if tmdb_title:
            title = tmdb_title
        else:
            title, _ = self._extract_title_year(meta.get('basename', ''))
            title = title or "Unknown"
        
        # 2. ANNO (da TMDb se disponibile, altrimenti dal file)
        year = tmdb_year or ""
        
        # 3. SERIE TV - aggiunge S01 o S01E01 invece di anno
        # Estrai stagione ed episodio dal basename
        season_match = re.search(r'S(\d+)', meta.get('basename', ''), re.IGNORECASE)
        episode_match = re.search(r'E(\d+)', meta.get('basename', ''), re.IGNORECASE)
        
        if season_match or self._is_tv_series(meta.get('basename', '')):
            # È una serie TV
            if season_match:
                season_num = season_match.group(1).zfill(2)
                season_episode = f"S{season_num}"
                
                # Aggiungi episodio se presente
                if episode_match:
                    episode_num = episode_match.group(1).zfill(2)
                    season_episode = f"S{season_num}E{episode_num}"
                
                # Per serie TV, se abbiamo l'anno da TMDb, lo includiamo prima della stagione
                if year:
                    scene_title = f"{title} {year} {season_episode}"
                else:
                    scene_title = f"{title} {season_episode}"
            else:
                scene_title = title
        else:
            # Film - aggiungi anno
            scene_title = f"{title} {year}" if year else title
        
        # 4. LINGUE (ordine alfabetico da tracce audio)
        languages = meta.get('audio_languages', [])
        if languages:
            # Mappa codice lingua a nome completo
            lang_mapping = {
                'en': 'ENGLISH',
                'it': 'ITALIAN',
                'fr': 'FRENCH',
                'de': 'GERMAN',
                'es': 'SPANISH',
                'pt': 'PORTUGUESE',
                'ja': 'JAPANESE',
                'zh': 'CHINESE',
                'ko': 'KOREAN',
                'ru': 'RUSSIAN',
            }
            
            lang_names = []
            for lang_code in sorted(languages):  # Ordine alfabetico
                lang_name = lang_mapping.get(lang_code.lower(), lang_code.upper())
                if lang_name not in lang_names:
                    lang_names.append(lang_name)
            
            languages_str = " - ".join(lang_names) if lang_names else ""
        else:
            languages_str = ""
        
        # 5. RISOLUZIONE
        resolution = meta.get('resolution', '1080p')
        
        # 6. FONTE (BluRay, WEB-DL, NF, etc.)
        source_parts = []
        
        # Servizio streaming (NF, AMZN, DSNP, etc.)
        service = meta.get('service', '')
        if service:
            service_name = RENAME_CONFIG["service_mapping"].get(service, service)
            source_parts.append(service_name)
        
        # Tipo di release (BluRay, WEB-DL, REMUX, etc.)
        release_type = meta.get('type', 'UNKNOWN')
        if release_type == 'REMUX':
            source_parts.append('BluRay')  # REMUX è una variante di BluRay nel formato scene
        elif release_type == 'WEBDL':
            source_parts.append('WEB-DL')
        elif release_type == 'WEBRIP':
            source_parts.append('WEBRip')
        elif release_type == 'ENCODE':
            source_parts.append('BluRay')
        elif release_type == 'DVDRIP':
            source_parts.append('DVDRip')
        else:
            source_parts.append('BluRay')  # Default
        
        source_str = " ".join(source_parts) if source_parts else "Unknown"
        
        # 7. AUDIO CODEC + CANALI
        audio_info = meta.get('audio', '')
        
        # 8. HDR INFO (solo se presente)
        hdr_info = meta.get('hdr_info', [])
        hdr_str = " ".join(hdr_info) if hdr_info else ""
        
        # 9. CODEC VIDEO
        if meta.get('type') == 'WEBDL':
            # Per WEB-DL usa il codec H.264/H.265
            video_codec = self._get_webdl_codec(meta)
        elif meta.get('type') == 'REMUX':
            # Per REMUX usa x265/x264 nel formato scene
            codec = meta.get('video_codec', '')
            if 'HEVC' in codec or 'H.265' in codec or 'x265' in codec:
                video_codec = 'x265'
            else:
                video_codec = 'x264'
        else:
            # Per ENCODE usa x264/x265
            video_codec = self._get_encode_codec(meta)
        
        # 10. RELEASE GROUP - Validazione e pulizia da SHRI
        release_group = meta.get('tag', '')
        
        # Se non presente, estrai dal basename e valida
        if not release_group:
            release_group = self._extract_clean_release_group(meta.get('basename', ''))
        else:
            # Pulisci il tag da trattini iniziali
            release_group = release_group.lstrip('-').strip()
            # Valida: se contiene invalid patterns, sostituisci con NoGroup
            if self.INVALID_TAG_PATTERN.search(release_group):
                release_group = 'NoGroup'
        
        # 10b. RILEVAMENTO REMUX da markers (VU, UNTOUCHED, etc.)
        basename = meta.get('basename', '')
        has_remux_marker = self.MARKER_PATTERN.search(basename) is not None
        if has_remux_marker and meta.get('type') != 'REMUX':
            # Se rilevi REMUX marker nel filename, aggiungi al source
            if 'REMUX' not in source_str:
                source_str = f"{source_str} REMUX"
        
        # ASSEMBLA IL TITOLO FINALE
        scene_parts = [scene_title]
        
        if languages_str:
            scene_parts.append(languages_str)
        
        scene_parts.append(resolution)
        scene_parts.append(source_str)
        
        if audio_info:
            scene_parts.append(audio_info)
        
        if hdr_str:
            scene_parts.append(hdr_str)
        
        scene_parts.append(f"{video_codec}-{release_group}")
        
        final_title = " ".join(scene_parts)
        
        # Pulisci spazi multipli (da SHRI WHITESPACE_PATTERN)
        final_title = self.WHITESPACE_PATTERN.sub(" ", final_title).strip()
        
        return final_title

    def _extract_clean_release_group(self, basename):
        """
        Estrae e valida il release group dal basename seguendo le regole SHRI.
        Accetta solo tag validi, altrimenti ritorna 'NoGroup'
        
        Logica:
        1. Estrai l'ultima parte dopo - (hyphen) se presente
        2. Se contiene REMUX markers (VU, UNTOUCHED, etc.), usa il marker come tag
        3. Altrimenti prova l'ultima parte separata da .
        4. Valida che non sia un tag non valido (nogroup, nogrp, unknown, unk)
        5. Valida lunghezza e caratteri alfanumerici
        """
        if not basename:
            return 'NoGroup'
        
        # Rimuovi estensione file (solo estensioni note)
        # splitext è problematico per file come "x264-GROUP.mkv" perché vede ".x264-GROUP" come estensione
        name_no_ext = basename
        for ext in ['.mkv', '.avi', '.mp4', '.mov', '.flv', '.wmv', '.webm', '.m4v']:
            if basename.lower().endswith(ext):
                name_no_ext = basename[:-len(ext)]
                break
        
        # PRIORITY 1: Cerca formato "something-RELEASEGRP" (hyphen + release group alla fine)
        # Questo è il formato più comune per release group
        if '-' in name_no_ext:
            parts = name_no_ext.rsplit('-', 1)  # Split dall'ultima occorrenza
            if len(parts) == 2:
                potential_tag = parts[1].strip()
                
                # Se è un formato valido (alfanumerico, non troppo lungo)
                if potential_tag and len(potential_tag) <= 30 and potential_tag.replace('_', '').isalnum():
                    # Valida che non sia un tag non valido
                    if not self.INVALID_TAG_PATTERN.search(potential_tag):
                        return potential_tag
        
        # PRIORITY 2: Se contiene REMUX markers, usali come tag
        # (VU1080, VU720, VU, UNTOUCHED, REMUX, etc.)
        marker_match = self.MARKER_PATTERN.search(name_no_ext)
        if marker_match:
            marker_tag = marker_match.group(1)
            if marker_tag and marker_tag.replace('_', '').isalnum() and len(marker_tag) <= 30:
                return marker_tag
        
        # PRIORITY 3: Se nessun hyphen o estrazione fallita, estrai l'ultima parola separata da .
        # MA solo se sembra un release group valido (non solo parole generiche)
        parts = name_no_ext.split('.')
        
        if not parts:
            return 'NoGroup'
        
        potential_tag = parts[-1].strip()
        
        # Se la parte è "Movie" o altre parole comuni senza pattern, è il titolo, non un release group
        # Release group devono avere almeno uno di questi: numeri, hyphen, underscore, etc.
        # Accetta solo se ha almeno un numero o è un release group noto
        if potential_tag and not any(c.isdigit() or c in ('_', '-') for c in potential_tag):
            # Nessun numero, hyphen o underscore - probabilmente è il titolo
            return 'NoGroup'
        
        # Validazioni:
        # 1. Non vuoto
        # 2. Non più lungo di 30 caratteri
        # 3. Solo caratteri alfanumerici e underscore
        # 4. Non corrisponde ai tag non validi (nogroup, etc.)
        if (not potential_tag 
            or len(potential_tag) > 30 
            or not potential_tag.replace('_', '').isalnum()):
            return 'NoGroup'
        
        # Controlla se è un tag non valido (nogroup, nogrp, unknown, unk)
        if self.INVALID_TAG_PATTERN.search(potential_tag):
            return 'NoGroup'
        
        return potential_tag

    def _normalize_title_for_search(self, filename):
        """Normalizza il nome del file per la ricerca TMDb con pulizia più aggressiva"""
        # Rimuovi estensione
        name = os.path.splitext(filename)[0]
        
        # Rimuovi pattern comuni per serie TV (mantieni solo titolo)
        if self._is_tv_series(name):
            # Tronca tutto a partire dal primo marker stagione/episodio
            episode_match = re.search(r'(?i)\b(?:S\d{1,2}E\d{1,2}|\d{1,2}x\d{2}|Season\s?\d+|\bS\d{1,2}\b|\bEp?\d{1,3}\b)', name)
            if episode_match:
                name = name[:episode_match.start()].strip()
        
        # Prima rimuovi l'anno se presente per evitare interferenze
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        found_year = year_match.group() if year_match else None
        
        # Rimuovi pattern comuni - ordine specifico per evitare frammenti
        tag_patterns = [
            # Audio codec prima (per evitare E-AC-3 -> E AC) - ORDINE IMPORTANTE!
            r'\bE-?AC-?3\b',    # Cattura E-AC-3, E-AC3, EAC-3, EAC3
            r'\bAC-?3\b',       # Cattura AC-3, AC3
            r'\bDTS-HD\.MA\b',
            r'\bDTS-HD\b',
            r'\bTrueHD\b',
            r'\bDD[\+P]?[0-9\.]*\b',
            r'\bDDP[0-9\.]*\b',
            r'\bAAC[0-9\.]*\b',
            r'\bATMOS\b',
            
            # Marker REMUX e non-compresso
            r'\b(?:UNTOUCHED|VU|DOWNCONVERT)\b',
            
            # Formati video HD (FullHD, HD, SD, etc.)
            r'\b(?:FullHD|FULLHD|SD|HDReady|HD)\b',
            
            # Formati video e risoluzioni (PRIMA di HDR/UHD perché sono più specifici)
            r'\b(?:1080p|720p|2160p|480p|540p|8k)\b',
            r'\b(?:h\.?264|h264|x\.?264|x264|h\.?265|h265|x\.?265|x265|avc|hevc|av1|hvec)\b',
            # Cattura anche il numero isolato che rimane dopo separatori convertiti (es: "H 264" -> "264")
            r'\b264\b', r'\b265\b',
            
            # HDR e video tech - SEPARATE da risoluzioni per evitare conflitti
            r'\b(?:HDR|HDR10|HLG|DV|DOLBY[-_.]?VISION)\b',  # HDR specifici
            r'\b(?:UHD|4K)\b',  # Format specifici
            
            # Tipi di release
            r'\b(?:BDRIP|BRRIP|BLURAY|BD|BDREMUX|HDRIP|DVDRIP|WEBRIP|WEB[-_.]?DL|WEBDL|WEB)\b',
            r'\b(?:DLMUX|WEBMUX|REMUX|PROPER|REPACK|READNFO|INTERNAL|LIMITED|UNRATED)\b',
            
            # Color space (dopo HDR specifici per evitare conflitti)
            r'\b(?:SDR|REC\.?709|REC\.?2020|BT\.?709|BT\.?2020)\b',
            
            # Lingue
            r'\b(?:ITA|ENG|ITALIAN|ENGLISH|MULTI|SUB|SUBS|DUBBED|DUB)\b',
            
            # Servizi streaming
            r'\b(?:AMZN|AMAZON|NETFLIX|NF|DSNP|DISNEY|HULU|ATVP|APPLE|MAX|HBO|PARAMOUNT|PEACOCK|CRUNCHYROLL|FUNIMATION)\b',
            
            # Altri tag
            r'\b(?:DIRECTOR\'?S?\.?CUT|EXTENDED|THEATRICAL|UNCUT|REMASTERED|CRITERION|RESYNC)\b',
            
            # Anno (dopo aver salvato quello trovato)
            r'\b(19|20)\d{2}\b',
            
            # Release group (alla fine) - Pattern più specifico
            r'[-_](?:[A-Za-z0-9]+)$',
            r'\[[^\]]*\]$',
        ]
        
        # PRIMA di convertire i separatori, rimuovi i numeri decimali (5.1, 2.0, etc.)
        name = re.sub(r'\b\d+\.\d+\b', '', name)
        
        # Pulisci separatori e caratteri speciali
        name = re.sub(r'[._\-\(\)\[\]]+', ' ', name)
        
        # Adesso applica i pattern regex (dopo aver convertito separatori in spazi)
        for pattern in tag_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Rimuovi parole singole rimaste (es: "E", "AC", "3")
        # LISTA ESTESA di frammenti comuni da rimuovere
        fragments_to_remove = {
            'AC', 'E', 'DL', 'WEB', 'HD', 'BD', 'DVD',
            'P', 'I', 'DDP', 'DD',  # Frammenti audio
            'H', 'X',  # Frammenti codec
            'MA', 'S', 'RM', 'RIP',  # Altri frammenti
            '3', '5', '7',  # Numeri singoli comuni
            'AVC', 'HEVC', 'H264', 'H265',  # Codec rimasti
        }
        
        # Release groups comuni (parole che spesso rimangono ma non fanno parte del titolo)
        release_groups_common = {
            'FHC', 'ABC', 'TASKO', 'XYZ', 'TEAM', 'CREW', 'GROUP',
            'PROPER', 'REPACK', 'REMUX', 'SCENE',
            'INTERNAL', 'LIMITED',
        }
        
        # Rilevi pattern release group (release group è tipicamente alfanumerico maiuscolo alla fine)
        # Es: "Title Something DDNCREW" -> DDNCREW è release group
        # Es: "Title Something iSlaNd" -> iSlaNd è release group (mix case)
        words = name.split()
        
        # Rimuovi release group dalla fine - Pattern: contiene lettere e/o numeri, 2+ caratteri
        # Controllo se ultima parola sembra un release group (non tutte minuscole, non è parola comune)
        if words:
            last_word = words[-1]
            last_word_lower = last_word.lower()
            # È release group se:
            # 1. È maiuscolo/mixcase (contiene uppercase) E non è parola italiana comune
            # 2. È lista nota di release groups
            is_likely_release_group = (
                (any(c.isupper() for c in last_word) and last_word_lower not in ['a', 'i', 'la', 'di', 'da', 'un']) 
                or last_word.upper() in release_groups_common
            )
            # Escludi parole comuni come "The", "A", etc.
            is_common_title_word = last_word_lower in ['the', 'a', 'an', 'una', 'un', 'il', 'lo', 'la']
            
            if is_likely_release_group and not is_common_title_word and not last_word.isdigit():
                words.pop()
        
        cleaned_words = []
        for idx, word in enumerate(words):
            # Mantieni solo parole significative
            # Rimuovi solo: lettere singole (non comuni) oppure frammenti tecnici noti
            word_lower = word.lower()
            
            # Parole comuni italiane/inglesi monosillabiche da mantenere
            is_common_word = word_lower in [
                'a', 'i', 'o', 'e', 'u',  # Articoli/preposizioni IT
                'la', 'il', 'lo', 'le', 'gli',  # Articoli IT
                'un', 'una', 'uno',  # Articoli indeterminativi IT
                'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'è',  # Preposizioni IT
                'the', 'a', 'an',  # Articoli EN
                'of', 'in', 'at', 'by', 'to', 'or', 'as',  # Preposizioni EN
            ]
            
            # Frammenti tecnici da rimuovere (hanno senso solo nel contesto metadata)
            is_tech_fragment = word.upper() in [
                'AC', 'DL', 'WEB', 'BD', 'DVD', 'P', 'DDP', 'DD', 'H', 'X', 'MA', 'S', 'RM', 'RIP', 'E',
                'AVC', 'HEVC', 'H264', 'H265'
            ]
            
            # Mantieni numeri SE:
            # - all'inizio (es: "12 Rounds") OPPURE
            # - circondati da parole significative (es: "Rounds 3 Lockdown")
            is_number = word.isdigit()
            is_start_number = is_number and idx == 0
            has_prev_word = idx > 0 and len(words[idx-1]) > 1
            has_next_word = idx < len(words) - 1 and len(words[idx+1]) > 1
            is_surrounded_number = is_number and has_prev_word and has_next_word
            
            # Rimuovi solo se: parola singola non comune E frammento tecnico
            should_keep = (len(word) > 1 or is_common_word or is_start_number or is_surrounded_number) and not is_tech_fragment
            
            if should_keep:
                cleaned_words.append(word)
        
        # Ricostruisci il titolo
        name = ' '.join(cleaned_words)
        
        # Pulisci spazi multipli e trim
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Se il risultato è vuoto o troppo corto, usa il nome originale
        if not name or len(name) < 3:
            name = os.path.splitext(filename)[0]
            name = re.sub(r'[._-]', ' ', name)
            name = re.sub(r'\s+', ' ', name).strip()
        
        return name


    def search_tmdb(self):
        """Cerca su TMDb il titolo specificato"""
        title = self.search_title.get().strip()
        if not title:
            messagebox.showerror("Errore", "Inserisci un titolo da cercare")
            return
            
        try:
            content_type = self.content_type.get()
            endpoint = "movie" if content_type == "movie" else "tv"
            
            # Ricerca su TMDb
            search_url = f"https://api.themoviedb.org/3/search/{endpoint}"
            params = {
                "api_key": self.TMDB_API_KEY,
                "query": title,
                "language": "it-IT"
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if not results:
                messagebox.showinfo("TMDb", f"Nessun risultato trovato per '{title}'")
                return
            
            # Se ci sono più risultati, chiedi all'utente di scegliere
            if len(results) > 1:
                selected = self._show_tmdb_selection_dialog(results, endpoint)
                if not selected:
                    return
            else:
                selected = results[0]
            
            # Aggiorna il nome del file con le informazioni TMDb
            self._update_name_with_tmdb_info(selected, endpoint)
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Errore TMDb", f"Errore di connessione: {e}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la ricerca TMDb: {e}")
    
    def _show_tmdb_selection_dialog(self, results, endpoint):
        """Mostra dialog per selezione da risultati TMDb con preview"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleziona il Film/Serie TV Corretto - TMDb")
        dialog.geometry("700x500")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        selected_result = None
        
        # Frame principale
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Titolo del dialog
        title_label = ttk.Label(main_frame, 
                               text=f"Trovati {len(results)} risultati per il {'film' if endpoint == 'movie' else 'serie TV'}:", 
                               font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 15))
        
        instruction_label = ttk.Label(main_frame, 
                                    text="Seleziona il risultato corretto per applicare titolo e anno giusti:",
                                    font=("Arial", 10))
        instruction_label.pack(anchor="w", pady=(0, 10))
        
        # Lista con scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        listbox = tk.Listbox(list_frame, font=("Arial", 10), height=12)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Popola lista con informazioni dettagliate
        for i, result in enumerate(results):
            title = result.get("title") or result.get("name", "")
            date = result.get("release_date") or result.get("first_air_date", "")
            year = date.split("-")[0] if date else "Anno sconosciuto"
            overview = result.get("overview", "Nessuna descrizione disponibile")
            
            # Tronca overview se troppo lungo
            if len(overview) > 80:
                overview = overview[:80] + "..."
            
            display_text = f"{i+1}. {title} ({year})\n   {overview}"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
        
        # Seleziona automaticamente il primo risultato
        listbox.selection_set(0)
        listbox.activate(0)
        
        # Frame info selezione
        info_frame = ttk.LabelFrame(main_frame, text="Anteprima Selezione", padding="10")
        info_frame.pack(fill="x", pady=(10, 0))
        
        info_label = ttk.Label(info_frame, text="", font=("Arial", 9), wraplength=600)
        info_label.pack(anchor="w")
        
        def update_preview(event=None):
            selection = listbox.curselection()
            if selection:
                result = results[selection[0]]
                title = result.get("title") or result.get("name", "")
                date = result.get("release_date") or result.get("first_air_date", "")
                year = date.split("-")[0] if date else ""
                
                preview_text = f"Titolo: {title}\nAnno: {year if year else 'Non specificato'}"
                if date:
                    preview_text += f"\nData completa: {date}"
                
                info_label.config(text=preview_text)
        
        # Aggiorna preview quando cambia selezione
        listbox.bind("<<ListboxSelect>>", update_preview)
        update_preview()  # Mostra preview iniziale
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        def on_select():
            nonlocal selected_result
            selection = listbox.curselection()
            if selection:
                selected_result = results[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("Attenzione", "Seleziona un risultato dalla lista")
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="✅ Usa Questo Risultato", 
                  command=on_select).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="❌ Annulla", 
                  command=on_cancel).pack(side="right")
        
        # Info aggiuntiva
        help_label = ttk.Label(main_frame, 
                              text="💡 Suggerimento: Doppio clic per selezione rapida",
                              font=("Arial", 8), foreground="gray")
        help_label.pack(anchor="w", pady=(5, 0))
        
        # Gestione doppio click
        listbox.bind("<Double-1>", lambda e: on_select())
        
        # Focus sulla lista
        listbox.focus_set()
        
        dialog.wait_window()
        return selected_result
    
    def _update_name_with_tmdb_info(self, tmdb_result, endpoint):
        """Aggiorna il nome del file con le informazioni TMDb"""
        try:
            # Ottieni informazioni base
            title = tmdb_result.get("title") or tmdb_result.get("name", "")
            date = tmdb_result.get("release_date") or tmdb_result.get("first_air_date", "")
            year = date.split("-")[0] if date else ""
            
            # Salva i dati TMDb temporaneamente per use in generate_name()
            self._temp_tmdb_title = title
            self._temp_tmdb_year = year
            
            # Per serie TV, cerca pattern episodio nel nome originale
            original_filename = os.path.basename(self.current_file.get())
            if endpoint == "tv":
                episode_match = re.search(r'(?i)(S\d{1,2}E\d{1,2})', original_filename)
                if episode_match:
                    episode_info = episode_match.group(1).upper()
                    new_title = f"{title} {episode_info}"
                else:
                    new_title = title
            else:
                new_title = title
            
            # Aggiorna il titolo per la ricerca (mostra all'utente cosa è stato trovato)
            if year:
                display_title = f"{title} ({year})"
            else:
                display_title = title
                
            # Mostra messaggio di successo
            msg = f"Trovato su TMDb:\n{display_title}"
            if endpoint == "tv" and episode_match:
                msg += f"\nEpisodio: {episode_info}"
            
            messagebox.showinfo("TMDb", msg)
            
            # Suggerisci di rigenerare il nome
            if messagebox.askyesno("TMDb", "Vuoi rigenerare automaticamente il nome del file?"):
                # Aggiorna temporaneamente il nome base per la generazione
                original_current = self.current_name.get()
                
                # Crea un nome temporaneo con le info TMDb
                temp_name = f"{title}"
                if year:
                    temp_name += f" {year}"
                if endpoint == "tv" and episode_match:
                    temp_name += f" {episode_info}"
                temp_name += ".mkv"
                
                self.current_name.set(temp_name)
                
                # Genera il nuovo nome
                self.generate_name()
                
                # Ripristina il nome originale
                self.current_name.set(original_current)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'aggiornamento: {e}")


def main():
    root = tk.Tk()
    app = MKVRenameAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()