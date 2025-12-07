# Configurazione TMDb API

L'applicazione supporta multiple modalità per configurare la chiave TMDb API, con priorità:

## 1. Variabile d'Ambiente (CONSIGLIATO per CI/CD e Deploy)

Imposta la variabile d'ambiente `TMDB_API_KEY`:

### Windows (PowerShell)
```powershell
$env:TMDB_API_KEY="tua_chiave_qui"
python mkv_rename_assistant.py
```

### Windows (CMD)
```cmd
set TMDB_API_KEY=tua_chiave_qui
python mkv_rename_assistant.py
```

### Linux/Mac
```bash
export TMDB_API_KEY="tua_chiave_qui"
python mkv_rename_assistant.py
```

### Docker / Ambiente Build
```dockerfile
ENV TMDB_API_KEY="tua_chiave_qui"
```

### GitHub Actions
```yaml
env:
  TMDB_API_KEY: ${{ secrets.TMDB_API_KEY }}
```

## 2. File Configurazione Locale (Per Sviluppo)

Crea un file `.tmdb_config` nella cartella principale:

```bash
echo "tua_chiave_qui" > .tmdb_config
```

**IMPORTANTE**: Questo file è nel `.gitignore` e non sarà committato

### Usando il file di esempio:
```bash
cp .tmdb_config.example .tmdb_config
# Modifica il file con il tuo editor
```

## 3. Dialog Interattivo (Se Non Trovata)

Se la chiave non viene trovata nelle prime due modalità, l'app chiederà:

1. Dialogo popup per inserire la chiave
2. Salva automaticamente in `.tmdb_config` (locale, non committato)
3. Usabile solo per questa sessione se il salvataggio fallisce

## Come Ottenere la Chiave TMDb

1. **Registrati/Accedi** su https://www.themoviedb.org/
2. **Vai alle Settings**: https://www.themoviedb.org/settings/api
3. **Richiedi Accesso API**:
   - Crea un nuovo account API
   - Seleziona "Developer"
   - Accetta i termini di servizio
4. **Copia la chiave** "API Key (v3 auth)"
5. **Pronta!** Ora puoi usarla nelle modalità sopra descritte

## Priorità Caricamento

```
1. TMDB_API_KEY (variabile d'ambiente)  ← PRIMA
2. .tmdb_config (file locale)           ← SECONDA  
3. Dialog interattivo                    ← TERZA
4. Non disponibile                       ← ULTIMA (ricerca disabilitata)
```

## Per i Maintainer / Build CI-CD

### GitHub Actions (Example)
```yaml
name: Build

on: [push]

env:
  TMDB_API_KEY: ${{ secrets.TMDB_API_KEY }}

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build with TMDb API
        run: |
          python -m PyInstaller --onefile --windowed mkv_rename_assistant.py
```

### Proteggere la Chiave su GitHub

⚠️ **MAI** mettere la chiave direttamente nel codice o nei file tracciati!

**Usa GitHub Secrets**:
1. Vai al repo → Settings → Secrets and variables → Actions
2. Clicca "New repository secret"
3. Name: `TMDB_API_KEY`
4. Value: (la tua chiave)
5. Usa in workflow: `${{ secrets.TMDB_API_KEY }}`

## Troubleshooting

### Errore: "Chiave TMDb non trovata"
- ✅ Verifica che la variabile d'ambiente sia impostata
- ✅ Verifica che `.tmdb_config` esista e abbia la chiave
- ✅ Riprova il dialog interattivo

### Ricerca TMDb non funziona
- ✅ Verifica che la chiave sia corretta
- ✅ Controlla la tua connessione internet
- ✅ La chiave potrebbe essere scaduta (ricrea l'accesso API)

### Build automation fallisce
- ✅ Assicurati che `TMDB_API_KEY` sia in GitHub Secrets
- ✅ Che sia passato al job di build
- ✅ Non mettere `.tmdb_config` in repository

## Sicurezza

✅ **Best Practices**:
- `.tmdb_config` è nel `.gitignore` ← NON verrà committato
- Usa variabili d'ambiente per deploy/CI-CD
- GitHub Secrets per valori sensibili
- La chiave rimane locale nel file di configurazione

⚠️ **ATTENZIONE**:
- Non debuggare con output della chiave
- Non farla apparire nei log
- Se compromessa, rigenerarla da TMDb settings
