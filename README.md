# 🎬 SHRI MKV Rename Assistant

**GUI application per rinominare file MKV secondo le regole scene**

Applicazione con interfaccia grafica che analizza i file MKV usando MediaInfo e genera automaticamente nomi compatibili con le regole scene (ENCODE, WEB-DL, REMUX).

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ⚡ Quick Start

### 1. Installazione
```bash
# Clone del repository
git clone https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI.git
cd SHRI-NAME-ASSISTANT-GUI

# Setup ambiente Python
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# oppure
.venv\Scripts\activate     # Windows

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Avvio
```bash
python mkv_rename_assistant.py
```

## 🎯 Funzionalità

- ✅ **Interfaccia Grafica**: GUI intuitiva con tkinter
- ✅ **MediaInfo Integration**: Analisi completa metadati video/audio
- ✅ **Scene Compliance**: Nomi conformi alle regole scene
- ✅ **Detection Automatico**: Risoluzione, codec, HDR, servizi streaming
- ✅ **Preview**: Anteprima del nome generato prima del rename

### Supporto Formati
- **Risoluzione**: 480p, 720p, 1080p, 2160p (4K)
- **Codec Video**: x264, x265, AVC, HEVC
- **HDR**: HDR10, Dolby Vision, HDR10+, HLG
- **Audio**: AC3, DTS, AAC, FLAC, TrueHD, Atmos
- **Servizi**: Netflix, Amazon Prime, Disney+, HBO Max, Apple TV+

## 📖 Uso

1. **Seleziona File**: Clicca "Seleziona File MKV"
2. **Analizza**: L'app estrae automaticamente i metadati
3. **Preview**: Visualizza informazioni file e nome suggerito
4. **Rinomina**: Clicca "Rinomina File" per applicare

### Esempi Output
```
Film.2023.2160p.BluRay.DDP5.1.DV.HDR10.x265-GROUP.mkv
Serie.S01E01.1080p.WEB-DL.DD5.1.H264-GROUP.mkv  
Documentario.2023.720p.HDTV.x264-GROUP.mkv
```

## 🔧 Requisiti

- **Python**: 3.8+  
- **Dipendenze**: pymediainfo
- **MediaInfo**: Installato nel sistema
- **SO**: Windows, Linux, macOS

## 📚 Documentazione

- [📋 Guida Completa](README_MKV_ASSISTANT.md) - Documentazione dettagliata
- [🔧 Sviluppo](../../tree/dev) - Branch development per contributi

## 🤝 Contributi

Per contribuire al progetto:

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/nome-feature`)  
3. Commit modifiche (`git commit -m 'Aggiunta feature'`)
4. Push branch (`git push origin feature/nome-feature`)
5. Apri Pull Request

**Branch di sviluppo**: [`dev`](../../tree/dev)

## 📄 Licenza

Questo progetto è sotto licenza MIT - vedi [LICENSE](LICENSE) per dettagli.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)  

---

**Sviluppato per la community scene italiana** 🇮🇹