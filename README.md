# SHRI MKV Rename Assistant GUI

Interfaccia grafica avanzata per la rinomina automatica di file MKV con integrazione TMDb e regole della scena.

## 🚀 Novità v2.0: Flusso Automatico TMDb

**PROCESSO COMPLETAMENTE AUTOMATICO:**
1. **Selezione File** → **Analisi TMDb** → **Correzione Automatica** → **Nome Generato**

### Esempio Pratico
```
File originale: "Senza.Sangue.2022.1080p.WEB-DL.DD5.1.H.264-NoGroup.mkv"
                    ↓ 
TMDb trova: "Senza sangue" (2025) ← Anno corretto!
                    ↓
Nome finale: "Senza.sangue.2025.1080p.WEB-DL.DD5.1.H.264-FHC.mkv"
```

**✅ CORREGGE AUTOMATICAMENTE:**
- Anni errati (2022 → 2025)  
- Titoli imprecisi
- Informazioni mancanti
- Format standardizzati

## 🎯 Caratteristiche

### Core Features
- **🤖 Processo Automatico**: Selezione → TMDb → Rinomina
- **🎬 Integrazione TMDb**: Database film/serie TV con correzione automatica
- **📊 Analisi MediaInfo**: Estrazione completa metadati video/audio
- **🏷️ Regole Scene**: Naming secondo convenzioni standard
- **🔍 Rilevamento Intelligente**: WEB-DL vs WEBRip, REMUX vs ENCODE
- **👀 Preview Tempo Reale**: Anteprima nome finale prima rinomina

### Formati Supportati
- **Video**: H.264, H.265/HEVC, AV1, HDR10, Dolby Vision
- **Audio**: DD, DDP, TrueHD, Atmos, DTS-HD MA
- **Release**: REMUX, WEB-DL, WEBRip, BluRay, UHD
- **Servizi**: Netflix, Amazon, Disney+, Apple TV+, Hulu

## 🛠️ Installazione

### Prerequisiti
- Python 3.8+
- pip (gestore pacchetti Python)

### Setup Rapido
```bash
# Clona repository
git clone https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI.git
cd SHRI-NAME-ASSISTANT-GUI

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente virtuale
# Windows:
venv\Scripts\activate
# Linux/Mac:  
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Avvia applicazione
python mkv_rename_assistant.py
```

## 📋 Utilizzo

### Flusso Automatico (Raccomandato)
1. **Seleziona File MKV** → L'app fa tutto automaticamente:
   - ✅ Analisi MediaInfo
   - ✅ Ricerca TMDb 
   - ✅ Correzione informazioni
   - ✅ Generazione nome finale
2. **Verifica Risultato** → Nome corretto mostrato
3. **Rinomina** → Clicca per applicare

### Flusso Manuale (Avanzato)
1. **Sfoglia** → Seleziona file MKV
2. **Analizza** → Estrai metadati MediaInfo
3. **TMDb** → Cerca e correggi manualmente
4. **Genera** → Crea nome scene-compliant
5. **Rinomina** → Applica nuovo nome

## 🎭 Esempi di Rinomina

### Film REMUX 4K
```
Input:  Black.Dog.2024.Messy.Name.2160p.BluRay.REMUX.mkv
TMDb:   Black Dog (2024) ← Titolo corretto
Output: Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd.mkv
```

### Film WEB-DL con Correzione Anno
```
Input:  Senza.Sangue.2022.1080p.WEB-DL.DD5.1.H.264-NoGroup.mkv
TMDb:   Senza sangue (2025) ← Anno corretto 2022→2025
Output: Senza.sangue.2025.1080p.WEB-DL.DD5.1.H.264-FHC.mkv
```

### Serie TV WEBRip
```
Input:  The.Midnight.Club.S01E01.Random.Title.1080p.WEBRip.x264-Group.mkv
TMDb:   The Midnight Club (2022) ← Titolo standardizzato
Output: The.Midnight.Club.2022.S01E01.1080p.NF.WEBRip.DD5.1.x264-FHC.mkv
```

### WEB-DL vs WEBRip (Rilevamento Automatico)
```
WEB-DL:  No encoding → "Title.2024.1080p.AMZN.WEB-DL.DD5.1.H.264-Group.mkv"
WEBRip:  x264 encoded → "Title.2024.1080p.NF.WEBRip.DD5.1.x264-Group.mkv"
```

## ⚙️ Configurazione

### TMDb API
L'API key è già configurata. Per personalizzare, modifica in `mkv_rename_assistant.py`:
```python
self.TMDB_API_KEY = "your-api-key-here"
```

### Regole Naming
Il file `config.py` contiene:
- **Marker REMUX**: Pattern identificazione file non compressi
- **Mapping Audio**: Conversioni formato standard  
- **Mapping Lingua**: Codici lingua standardizzati
- **Servizi Streaming**: Abbreviazioni e mappings

## 🔧 Funzionalità Avanzate

### Rilevamento Intelligente
- **REMUX**: Bitrate alto + no encoding indicators
- **WEB-DL**: Source puro senza re-encoding
- **WEBRip**: Encoding indicators in MediaInfo
- **HDR/DV**: Parsing automatico metadati colore

### Correzione TMDb
- **Titoli**: Standardizzazione automatica
- **Anni**: Correzione basata su database ufficiale
- **Serie TV**: Mantenimento info episodio (S01E01)
- **Fallback**: Usa info file se TMDb non disponibile

## 🐛 Risoluzione Problemi

### File non Processato
- ✅ Verifica formato .mkv
- ✅ Controlla permessi lettura
- ✅ MediaInfo installato correttamente

### TMDb non Funziona  
- ✅ Connessione internet attiva
- ✅ API key valida
- ✅ Titolo troppo generico → prova ricerca manuale

### Nome Errato Generato
- ✅ Verifica metadati nel pannello info
- ✅ Controlla regole in config.py
- ✅ TMDb ha trovato film/serie corretti?

### Errore Rinomina
- ✅ Permessi scrittura cartella
- ✅ File non in uso da altri programmi
- ✅ Nome destinazione non esistente

## 🤝 Contributi

1. Fork del progetto
2. Crea branch feature (`git checkout -b feature/tmdb-enhancement`)  
3. Commit modifiche (`git commit -m 'Add TMDb auto-correction'`)
4. Push al branch (`git push origin feature/tmdb-enhancement`)
5. Apri Pull Request

## 📄 Licenza

Distribuito sotto Licenza MIT. Vedi `LICENSE` per dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI/discussions)

---

**⭐ Se questo progetto ti è utile, lascia una stella su GitHub!**