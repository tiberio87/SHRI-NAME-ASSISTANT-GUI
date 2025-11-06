@echo off
echo MKV Rename Assistant - Scene Rules
echo.
echo Controllo dipendenze...

:: Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato. Installa Python 3.8 o superiore.
    pause
    exit /b 1
)

:: Controlla se MediaInfo è disponibile
mediainfo --version >nul 2>&1
if errorlevel 1 (
    echo ATTENZIONE: MediaInfo non trovato nel PATH.
    echo L'applicazione potrebbe non funzionare correttamente.
    echo Scarica MediaInfo da: https://mediaarea.net/en/MediaInfo/Download/Windows
    echo.
)

:: Controlla se il virtual environment esiste
if exist ".venv\Scripts\python.exe" (
    echo Uso del virtual environment...
    .venv\Scripts\python.exe mkv_rename_assistant.py
) else (
    echo Virtual environment non trovato, uso Python di sistema...
    
    :: Installa dipendenze se necessario
    echo Controllo dipendenze Python...
    python -c "import pymediainfo" >nul 2>&1
    if errorlevel 1 (
        echo Installazione pymediainfo...
        pip install pymediainfo
    )
    
    :: Avvia l'applicazione
    python mkv_rename_assistant.py
)

if errorlevel 1 (
    echo.
    echo ERRORE: L'applicazione è terminata con errori.
    pause
)