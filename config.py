# -*- coding: utf-8 -*-
"""
Configurazione per MKV Rename Assistant
"""

# Configurazioni per la rinomina
RENAME_CONFIG = {
    # Usa il titolo italiano se disponibile nei metadati
    "use_italian_title": True,
    
    # Aggiungi automaticamente [SUBS] per sottotitoli italiani senza audio italiano
    "add_subs_tag": True,
    
    # Formato preferito per le lingue multiple
    "multi_language_format": "ITALIAN-ENGLISH",  # o "Multi"
    
    # Release group di default se non trovato
    "default_release_group": "NoGroup",
    
    # Pattern per identificare REMUX
    "remux_markers": ["REMUX", "UNTOUCHED", "VU1080", "VU720", "VU"],
    
    # Mapping codec video
    "video_codec_mapping": {
        "HEVC": "x265",
        "H.265": "x265", 
        "AVC": "x264",
        "H.264": "x264",
        "MPEG-4 Visual": "XviD",
        "MPEG-2 Video": "MPEG2"
    },
    
    # Mapping codec video per REMUX (formato diverso)
    "remux_codec_mapping": {
        "HEVC": "HVEC",
        "H.265": "HVEC",
        "AVC": "AVC", 
        "H.264": "AVC"
    },
    
    # Mapping codec video per WEB-DL (formato H.xxx)
    "webdl_codec_mapping": {
        "HEVC": "H.265",
        "H.265": "H.265",
        "AVC": "H.264",
        "H.264": "H.264"
    },
    
    # Mapping formato audio
    "audio_format_mapping": {
        "AAC": "AAC",
        "AC-3": "DD5.1",
        "E-AC-3": "DDP5.1", 
        "Dolby Digital Plus": "DDP5.1",
        "TrueHD": "TrueHD.Atmos.7.1",
        "MLP FBA": "TrueHD.Atmos.7.1",
        "DTS": "DTS",
        "DTS-HD MA": "DTS-HD.MA.7.1",
        "DTS-HD HRA": "DTS-HD.HRA",
        "FLAC": "FLAC",
        "PCM": "PCM"
    },
    
    # Mapping servizi streaming
    "service_mapping": {
        "AMZN": "AMZN",
        "Amazon": "AMZN",
        "Netflix": "NF", 
        "Disney+": "DSNP",
        "Hulu": "HULU",
        "HBO Max": "HMAX",
        "Apple TV+": "ATVP",
        "Paramount+": "PMTP"
    },
    
    # Mapping lingue
    "language_mapping": {
        "it": "ITALIAN",
        "ita": "ITALIAN", 
        "italian": "ITALIAN",
        "italiano": "ITALIAN",
        "en": "ENGLISH",
        "eng": "ENGLISH",
        "english": "ENGLISH",
        "es": "SPANISH", 
        "spa": "SPANISH",
        "spanish": "SPANISH",
        "fr": "FRENCH",
        "fra": "FRENCH", 
        "french": "FRENCH",
        "de": "GERMAN",
        "ger": "GERMAN",
        "german": "GERMAN",
        "ja": "JAPANESE",
        "jpn": "JAPANESE",
        "japanese": "JAPANESE"
    },
    
    # Pattern per titoli da escludere
    "exclude_title_patterns": [
        r"^(sample|trailer|preview)",
        r"(bonus|extra|deleted.scenes)"
    ],
    
    # Separatori permessi nel nome finale
    "allowed_separators": [".", "-"],
    
    # Estensioni supportate
    "supported_extensions": [".mkv", ".mp4", ".avi"],
    
    # Dimensione minima file (in MB) per essere considerato un film
    "min_movie_size_mb": 500
}

# Configurazioni GUI
GUI_CONFIG = {
    "window_title": "MKV Rename Assistant - Scene Rules",
    "window_size": "800x700",
    "font_family": "Arial",
    "font_size": 10,
    "info_text_height": 10,
    "supported_filetypes": [
        ("File MKV", "*.mkv"),
        ("File Video", "*.mkv *.mp4 *.avi"),
        ("Tutti i file", "*.*")
    ]
}

# Messaggi di errore personalizzati
ERROR_MESSAGES = {
    "no_file_selected": "Seleziona prima un file!",
    "file_not_exists": "Il file selezionato non esiste!",
    "analysis_error": "Errore durante l'analisi del file:",
    "mediainfo_error": "MediaInfo non trovato. Assicurati che sia installato.",
    "rename_error": "Errore durante la rinomina:",
    "file_exists": "Un file con questo nome esiste già!",
    "no_new_name": "Genera prima il nuovo nome!",
    "invalid_extension": "Il file deve avere estensione .mkv"
}

# Messaggi di successo
SUCCESS_MESSAGES = {
    "analysis_complete": "File analizzato con successo!",
    "rename_complete": "File rinominato con successo!",
    "name_generated": "Nome generato secondo le regole della scena"
}