# MKV Rename Assistant

Un'applicazione GUI per rinominare file MKV secondo le regole della scena, basata sul codice del tracker ShareIsland (SHRI).

## Caratteristiche

- **Interfaccia grafica intuitiva** - Facile da usare per tutti
- **Analisi automatica dei metadati** - Estrae informazioni dai file MKV usando MediaInfo
- **Regole della scena** - Applica le naming convention standard della scena
- **Anteprima del nome** - Mostra il nuovo nome prima di rinominare
- **Sicurezza** - Controlla che non esistano file duplicati prima di rinominare

## Installazione

### Prerequisiti

- Python 3.8 o superiore
- MediaInfo installato sul sistema

### Dipendenze Python

```bash
pip install pymediainfo
```

**Nota**: tkinter è incluso nella maggior parte delle installazioni Python.

### Installazione MediaInfo

#### Windows
1. Scarica MediaInfo da https://mediaarea.net/en/MediaInfo/Download/Windows
2. Installa la versione CLI o GUI
3. Assicurati che `mediainfo` sia nel PATH del sistema

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install mediainfo
```

#### macOS
```bash
brew install mediainfo
```

## Utilizzo

1. **Avvia l'applicazione**:
   ```bash
   python mkv_rename_assistant.py
   ```

2. **Seleziona un file MKV**:
   - Clicca su "Sfoglia..." per selezionare il file MKV da rinominare

3. **Analizza il file**:
   - Clicca su "Analizza File" per estrarre i metadati
   - Visualizza le informazioni del file nella sezione dedicata

4. **Genera il nuovo nome**:
   - Clicca su "Genera Nome" per applicare le regole della scena
   - Il nuovo nome apparirà nel campo "Nuovo nome"

5. **Rinomina il file**:
   - Verifica che il nuovo nome sia corretto
   - Clicca su "Rinomina File" per applicare le modifiche

## Regole di Naming

L'applicazione applica le seguenti regole della scena basate sui pattern reali:

### Formato ENCODE da BluRay:
```
Titolo.Anno.Risoluzione.Source.Audio.Codec-ReleaseGroup.mkv
```

**Esempi:**
- `Black.Dog.2024.1080p.BluRay.DD5.1.x264-iSlaNd.mkv`
- `Black.Dog.2024.1080p.BluRay.DD5.1.x265-iSlaNd.mkv`
- `Black.Dog.2024.2160p.BluRay.DDP.7.1.DV.HDR10.x265-iSlaNd.mkv`

### Formato WEB-DL:
```
Titolo.Anno.Risoluzione.Servizio.WEB-DL.Audio.HDR.Codec-ReleaseGroup.mkv
```

**Esempi:**
- `Hedda.2025.2160p.AMZN.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-FHC.mkv`
- `Hedda.2025.1080p.AMZN.WEB-DL.DDP5.1.Atmos.H.264-FHC.mkv`

### Formato REMUX:
```
Titolo.Anno.[UHD.]Source.Risoluzione.Audio.Codec.REMUX-ReleaseGroup.mkv
```

**Esempi:**
- `Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd.mkv`
- `Black.Dog.2024.BluRay.1080p.TrueHD.Atmos.7.1.AVC.REMUX-iSlaNd.mkv`

### Componenti supportati:

- **Risoluzione**: 480p, 576p, 720p, 1080p, 2160p
- **Source**: BluRay, WEB
- **Servizi**: AMZN (Amazon), NF (Netflix), DSNP (Disney+), HULU, ATVP (Apple TV+)
- **Codec ENCODE**: x264, x265
- **Codec WEB-DL**: H.264, H.265  
- **Codec REMUX**: AVC, HVEC
- **Audio**: DD5.1, DDP5.1, TrueHD.Atmos.7.1, DTS-HD.MA.7.1
- **HDR**: DV (Dolby Vision), HDR10, HDR
- **Tipi**: REMUX, WEB-DL, WEBRip, ENCODE

## Funzionalità Avanzate

### Rilevamento automatico del tipo:
- **REMUX**: Detecta marker come "REMUX", "UNTOUCHED", "VU" nel nome
- **ENCODE**: File compressi con codec specifici
- **DVDRIP**: File derivati da DVD

### Gestione multilingua:
- Priorità: Lingua originale → ITALIAN → ENGLISH → Altri
- Format: `ITALIAN-ENGLISH` per audio doppio
- `Multi` per più di 3 lingue

### Release Group:
- Estrazione automatica dal nome del file
- Validazione contro tag invalidi (nogrp, unknown, etc.)
- Fallback a "NoGroup" se non trovato

## Limitazioni

- Supporta solo file MKV
- Richiede MediaInfo installato sul sistema
- Le regole di naming sono specifiche per la scena italiana
- Alcuni metadati potrebbero non essere rilevati correttamente

## Troubleshooting

### Errore "MediaInfo non trovato"
- Assicurati che MediaInfo sia installato
- Verifica che sia nel PATH del sistema
- Su Windows, riavvia il command prompt dopo l'installazione

### Il file non viene analizzato
- Controlla che il file sia un MKV valido
- Verifica i permessi di lettura del file
- Controlla che il file non sia in uso da altri programmi

### Nome generato non corretto
- Verifica che i metadati del file siano completi
- Alcuni file potrebbero richiedere editing manuale del nome
- Il campo "Nuovo nome" è editabile per correzioni manuali

## Struttura del Progetto

```
SHRI-NAME-ASSISTANT-GUI/
├── mkv_rename_assistant.py  # Applicazione principale
├── SHRI - Rename Assistant.py  # Codice originale SHRI
└── README.md  # Questo file
```

## Contribuire

Per contribuire al progetto:

1. Fork del repository
2. Crea un branch per le tue modifiche
3. Testa le modifiche
4. Invia una pull request

## Licenza

Questo progetto è basato sul codice del tracker ShareIsland (SHRI) e mantiene la stessa licenza.

## Crediti

- Basato sul codice del tracker ShareIsland (SHRI)
- Utilizza MediaInfo per l'analisi dei file
- Interfaccia grafica con tkinter

---

**Nota**: Questo tool è destinato all'uso personale e educativo. Rispetta sempre le leggi sul copyright e i termini di servizio dei tracker.