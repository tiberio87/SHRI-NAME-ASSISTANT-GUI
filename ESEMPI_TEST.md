# MKV Rename Assistant - Esempi di Test

Questo file contiene esempi di nomi di file MKV e i risultati attesi per testare l'applicazione.

## 🎬 FILM ENCODE DA BLURAY

### Input di esempio:
- `Black.Dog.2024.ITALIAN.1080p.BluRay.DD5.1.x264-SPARKS.mkv`
- `Movie.Name.2020.1080p.BRRip.x265.DD.5.1-GROUP.mkv`
- `Action.Film.2023.2160p.UHD.BluRay.x265.HDR.DDP.7.1-RELEASE.mkv`

### Output atteso:
- `Black.Dog.2024.1080p.BluRay.DD5.1.x264-SPARKS.mkv`
- `Movie.Name.2020.1080p.BluRay.DD5.1.x265-GROUP.mkv`
- `Action.Film.2023.2160p.BluRay.DDP.7.1.x265-RELEASE.mkv`

## 🌐 FILM WEB-DL

### Input di esempio:
- `Streaming.Movie.2024.2160p.AMZN.WEB-DL.DDP5.1.Atmos.H.265-FHC.mkv`
- `Series.S01E01.2023.1080p.Netflix.WEB-DL.DD5.1.H.264-TEAM.mkv`
- `New.Film.2025.2160p.DSNP.WEB-DL.Atmos.DV.HDR.H.265-GROUP.mkv`

### Output atteso:
- `Streaming.Movie.2024.2160p.AMZN.WEB-DL.DDP5.1.Atmos.H.265-FHC.mkv`
- `Series.S01E01.2023.1080p.NF.WEB-DL.DD5.1.H.264-TEAM.mkv`
- `New.Film.2025.2160p.DSNP.WEB-DL.Atmos.DV.HDR.H.265-GROUP.mkv`

## 💿 FILM REMUX

### Input di esempio:
- `Epic.Movie.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HEVC.REMUX-iSlaNd.mkv`
- `Classic.Film.1999.BluRay.1080p.DTS-HD.MA.5.1.AVC.REMUX-GROUP.mkv`
- `Horror.Movie.2023.COMPLETE.UHD.BLURAY.UNTOUCHED-REMUX.mkv`

### Output atteso:
- `Epic.Movie.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-iSlaNd.mkv`
- `Classic.Film.1999.BluRay.1080p.DTS-HD.MA.5.1.AVC.REMUX-GROUP.mkv`
- `Horror.Movie.2023.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HVEC.REMUX-REMUX.mkv`

## 🧪 Come testare

1. **Prepara file di test** (opzionale):
   - Crea file vuoti con i nomi di esempio: `touch "nome.file.esempio.mkv"`
   - Oppure usa file MKV reali

2. **Avvia l'applicazione**:
   ```bash
   python mkv_rename_assistant.py
   ```

3. **Test manuale**:
   - Seleziona un file con nome disordinato
   - Clicca "Analizza File"
   - Clicca "Genera Nome"
   - Verifica che il risultato corrisponda ai pattern attesi

4. **Test automatico**:
   ```bash
   python test_scene_patterns.py
   ```

## 📋 Checklist di Test

### ✅ Caratteristiche da verificare:

- [ ] **Estrazione titolo/anno**: Riconosce titoli con punti, spazi, parentesi
- [ ] **Risoluzione**: Identifica correttamente 720p, 1080p, 2160p
- [ ] **Tipo di release**: Distingue ENCODE, REMUX, WEB-DL
- [ ] **Codec video**: Mappa correttamente x264/x265, AVC/HVEC, H.264/H.265
- [ ] **Audio**: Formatta DD5.1, DDP5.1, TrueHD.Atmos.7.1
- [ ] **Servizi streaming**: Riconosce AMZN, NF, DSNP, etc.
- [ ] **HDR**: Identifica DV, HDR10, HDR
- [ ] **Release group**: Estrae tag finale correttamente

### 🎯 Pattern specifici:

- [ ] **ENCODE**: `Titolo.Anno.Res.Source.Audio.Codec-Group`
- [ ] **WEB-DL**: `Titolo.Anno.Res.Service.WEB-DL.Audio.HDR.Codec-Group`
- [ ] **REMUX**: `Titolo.Anno.[UHD.]Source.Res.Audio.Codec.REMUX-Group`

### 🚀 Test avanzati:

- [ ] File con caratteri speciali nel nome
- [ ] File senza release group (→ NoGroup)
- [ ] File con tag invalidi (nogrp, unknown)
- [ ] File multi-lingua
- [ ] File con HDR/Dolby Vision

## 🐛 Problemi comuni

### Il nome generato non è corretto:
1. Verifica che MediaInfo sia installato
2. Controlla che i metadati del file siano completi
3. Modifica manualmente il campo "Nuovo nome" se necessario

### L'applicazione non riconosce il tipo:
1. Assicurati che il nome del file contenga marker riconoscibili
2. Controlla la presenza di "REMUX", "WEB-DL", servizi streaming
3. Verifica che la risoluzione sia rilevabile

### Release group non riconosciuto:
1. Il gruppo deve essere l'ultima parte del nome separata da `-`
2. Non deve contenere spazi o caratteri speciali
3. Tags come "nogrp", "unknown" vengono sostituiti con "NoGroup"

## 💡 Suggerimenti

- **Backup**: Fai sempre backup dei file prima di rinominarli
- **Test**: Usa prima file di prova per verificare i risultati
- **Editing**: Il campo "Nuovo nome" è editabile per correzioni manuali
- **Batch**: Per molti file, considera di usare script esterni che chiamano l'app

---

**Happy renaming! 🎉**