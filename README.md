# SHRI MKV Rename Assistant GUI

Rinomina automatica file MKV con integrazione TMDb e regole scene.

## 🚀 Quick Start

```bash
# Clone e setup
git clone https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI.git
cd SHRI-NAME-ASSISTANT-GUI
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate; Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# Avvia app
python mkv_rename_assistant.py
```

## 📖 Utilizzo

1. **Seleziona File MKV** → Sfoglia e scegli il file
2. **Analizza** → Estrae metadati (MediaInfo)
3. **Ricerca TMDb** → Trova film/serie corretti
4. **Genera Nome** → Crea nome scene-compliant
5. **Rinomina** → Applica nuovo nome

**Esempio:**
```
Input:  "The.Nice.Guys.2016.Italian.1080p.BluRay.x264.mkv"
Output: "The.Nice.Guys.2016.ITALIAN.1080p.BluRay.DD5.1.x264-GROUP.mkv"
```

## ✨ Caratteristiche

- 🤖 **Analisi Automatica**: Estrae metadati video/audio
- 🎬 **Integrazione TMDb**: Ricerca e correzione titoli/anni
- 🏷️ **Regole Scene**: Naming standardizzato
- 📊 **Supporto Completo**: REMUX, WEB-DL, WEBRip, HDR, Dolby Vision
- 🔍 **Rilevamento Intelligente**: Distingue automaticamente formati
- 👀 **Preview Tempo Reale**: Anteprima nome prima di rinominare

## ⚙️ Configurazione TMDb

La chiave API si configura in ordine di priorità:

1. **Variabile d'Ambiente**
   ```bash
   export TMDB_API_KEY="your-key"
   python mkv_rename_assistant.py
   ```

2. **File Locale** (`.tmdb_config`)
   ```bash
   echo "your-key" > .tmdb_config
   ```

3. **Dialog Interattivo** (primo avvio)
   - L'app chiede la chiave
   - Salva automaticamente in `.tmdb_config`

**Ottieni la chiave:** https://www.themoviedb.org/settings/api

## 🎯 Esempi Rinomina

### REMUX 4K
```
Input:  Black.Dog.2024.2160p.BluRay.REMUX.mkv
Output: Black.Dog.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HEVC.REMUX-GROUP.mkv
```

### WEB-DL con Correzione Anno
```
Input:  Senza.Sangue.2022.1080p.WEB-DL.mkv
        ↓ TMDb corregge anno: 2022 → 2025
Output: Senza.sangue.2025.1080p.WEB-DL.DD5.1.H.264-GROUP.mkv
```

### Serie TV
```
Input:  The.Midnight.Club.S01E01.1080p.WEBRip.mkv
Output: The.Midnight.Club.2022.S01E01.1080p.WEBRip.DD5.1.x264-GROUP.mkv
```

## 🔧 Supporto Formati

**Video:** H.264, H.265/HEVC, AV1, HDR10, Dolby Vision  
**Audio:** DD, DDP, TrueHD, Atmos, DTS-HD MA, FLAC  
**Source:** REMUX, WEB-DL, WEBRip, BluRay, UHD, LD  
**Servizi:** Netflix, Amazon, Disney+, Apple TV+, Hulu

## 🆘 Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| File non processato | Verifica formato .mkv e permessi |
| TMDb non trova | Controlla internet, API key, prova ricerca manuale |
| Nome errato | Verifica metadati nel pannello info, controlla rules |
| Errore rinomina | Controlla permessi cartella, file non in uso |

## 📄 Licenza

MIT License - vedi `LICENSE`

## 🤝 Contributi

1. Fork repository
2. Crea branch: `git checkout -b feature/name`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/name`
5. Apri Pull Request

- **Issues**: [GitHub Issues](https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI/discussions)

---

**⭐ Se questo progetto ti è utile, lascia una stella su GitHub!**