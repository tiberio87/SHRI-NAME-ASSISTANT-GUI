# 🚀 SHRI MKV Rename Assistant - Development Branch

Questa è la **branch di sviluppo** per il MKV Rename Assistant. Usa questa branch per implementare nuove funzionalità e miglioramenti.

## 📋 Setup Sviluppo

### 1. Clone del Repository
```bash
git clone https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI.git
cd SHRI-NAME-ASSISTANT-GUI
git checkout dev
```

### 2. Setup Ambiente Python
```bash
# Crea virtual environment
python -m venv .venv

# Attiva l'ambiente (Windows)
.venv\Scripts\activate

# Installa dipendenze
pip install pymediainfo tkinter
```

### 3. Avvio Rapido
```bash
# Windows - doppio click su:
start_mkv_assistant.bat

# Oppure manuale:
python mkv_rename_assistant.py
```

## 🗂️ Struttura Progetto

```
├── mkv_rename_assistant.py    # 🎯 Applicazione principale GUI
├── config.py                  # ⚙️ Configurazioni e mappings
├── start_mkv_assistant.bat    # 🚀 Launcher Windows
├── test_*.py                  # 🧪 Suite di test completa
├── ESEMPI_TEST.md            # 📖 Esempi e casi test
├── README_MKV_ASSISTANT.md   # 📋 Documentazione utente
└── DEV_README.md             # 🔧 Questa guida sviluppo
```

## 🧪 Test Suite

### Esegui Tutti i Test
```bash
python test_mkv_assistant.py      # Test generali
python test_resolution_fix.py     # Test classificazione risoluzione
python test_encode_remux_fix.py   # Test ENCODE/REMUX detection
python test_hdr_fix.py           # Test HDR/Dolby Vision
python test_scene_patterns.py    # Test pattern scene naming
```

### Coverage Attuale: **100%** ✅
- ✅ Classificazione risoluzione (1920x804 → 1080p fix)
- ✅ Detection ENCODE/REMUX (Writing Library fix)  
- ✅ Estrazione HDR/DV da MediaInfo
- ✅ Pattern scene naming completi
- ✅ GUI workflow completo

## 🎯 Roadmap Sviluppo Futuro

### 🔥 Priority 1 - Funzionalità Core
- [ ] **Batch Processing**: Rinomina multipla file in una cartella
- [ ] **Undo System**: Possibilità di annullare rename
- [ ] **Preview Mode**: Anteprima nomi prima del rename
- [ ] **Custom Rules**: Regole personalizzabili per utenti avanzati

### ⚡ Priority 2 - UX/UI Improvements  
- [ ] **Drag & Drop**: Trascina file direttamente nell'app
- [ ] **Dark Theme**: Tema scuro per l'interfaccia
- [ ] **Progress Bar**: Indicatore progresso per operazioni lunghe
- [ ] **Recent Files**: Lista file rinominati recentemente

### 🚀 Priority 3 - Advanced Features
- [ ] **Plugin System**: Sistema di plugin per estendere funzionalità
- [ ] **API Integration**: Integrazione con database online (TMDb, etc.)
- [ ] **Auto-Detection**: Detection automatica show/movie da filename
- [ ] **Backup System**: Backup automatico nomi originali

### 🔧 Priority 4 - Technical Improvements
- [ ] **Config GUI**: Interfaccia grafica per modificare configurazioni
- [ ] **Logging System**: Log dettagliati delle operazioni
- [ ] **Error Recovery**: Gestione robusta degli errori
- [ ] **Performance**: Ottimizzazioni per file molto grandi

## 🛠️ Workflow Sviluppo

### 1. Creazione Feature Branch
```bash
git checkout dev
git pull origin dev
git checkout -b feature/nome-feature
```

### 2. Sviluppo e Test
```bash
# Sviluppa la feature
# Scrivi/aggiorna test
python test_*.py  # Verifica tutti i test passano
```

### 3. Commit e Push
```bash
git add .
git commit -m "feat: descrizione feature"
git push origin feature/nome-feature
```

### 4. Pull Request
- Crea PR da `feature/nome-feature` → `dev`
- Review e merge in `dev`
- Periodicamente merge `dev` → `master` per release

## 📝 Coding Standards

### Stile Codice
- **PEP 8** compliance
- Docstrings per tutte le funzioni
- Type hints dove possibile
- Commenti in italiano per coerenza

### Test Requirements
- Ogni nuova feature deve avere test
- Mantenere 100% pass rate
- Test sia positivi che edge cases
- Mock MediaInfo per test deterministici

### Commit Messages
```
feat: aggiunta nuova funzionalità
fix: correzione bug
test: aggiornamento/aggiunta test
docs: aggiornamento documentazione
refactor: refactoring senza cambio funzionalità
style: formattazione codice
```

## 🐛 Debug & Troubleshooting

### MediaInfo Issues
```python
# Test MediaInfo manuale
from pymediainfo import MediaInfo
media_info = MediaInfo.parse("file.mkv")
for track in media_info.tracks:
    print(f"{track.track_type}: {track.to_data()}")
```

### GUI Debug
```python
# Abilita debug mode in mkv_rename_assistant.py
DEBUG = True  # Mostra stack traces completi
```

### Performance Profiling
```bash
python -m cProfile -o profile.stats mkv_rename_assistant.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

## 📞 Contatti & Support

- **Repository**: https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI
- **Issues**: Usa GitHub Issues per bug reports
- **Discussions**: GitHub Discussions per domande generali
- **Wiki**: Documentazione estesa nel GitHub Wiki

---

## 🎉 Quick Start per Nuovi Developer

```bash
# 1. Setup completo in 3 comandi
git clone https://github.com/tiberio87/SHRI-NAME-ASSISTANT-GUI.git
cd SHRI-NAME-ASSISTANT-GUI && git checkout dev
python -m venv .venv && .venv\Scripts\activate && pip install pymediainfo

# 2. Test che tutto funziona
python test_mkv_assistant.py

# 3. Avvia l'app
python mkv_rename_assistant.py
```

**Buono sviluppo! 🚀**