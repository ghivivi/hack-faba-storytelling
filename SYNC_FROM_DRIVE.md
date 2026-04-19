# 📦 Faba Google Drive Sync - SYNC_FROM_DRIVE.md

Script per sincronizzare file MP3 da Google Drive al dispositivo Faba. Ideale per ricevere registrazioni audio da altre persone e aggiungerle automaticamente al Faba.

## 🎯 Caso d'uso

**Scenario tipico:**
1. Nonni/zii/amici registrano storie audio su smartphone
2. Le caricano su una cartella Google Drive condivisa
3. Tu colleghi il Faba al PC
4. Esegui lo script per scaricare e processare automaticamente i nuovi file
5. I file vengono aggiunti al Faba con ID autoincrementale
6. I file processati vengono archiviati su Drive

## 🔧 Requisiti

### 1. Installa rclone

**Linux/macOS:**
```bash
curl https://rclone.org/install.sh | sudo bash
```

**Windows:**
- Scarica da: https://rclone.org/downloads/
- Estrai e aggiungi al PATH

### 2. Installa dipendenze Python

```bash
pip install mutagen
```

### 3. Configura Google Drive (Prima volta)

```bash
./sync_from_drive.py --setup
```

Questo ti guiderà attraverso:
1. Configurazione di rclone
2. Autenticazione con Google
3. Creazione del remote "gdrive"

**Note:**
- Si aprirà il browser per autenticarti con Google
- Autorizza rclone ad accedere al tuo Google Drive
- Il token sarà salvato localmente in modo sicuro

## 📁 Struttura Cartelle Google Drive

Crea questa struttura sul tuo Google Drive:

```
Faba/
  ├── incoming/      ← Carica qui i nuovi MP3
  └── processed/     ← I file processati vengono spostati qui automaticamente
```

**Come crearla:**
1. Vai su drive.google.com
2. Crea una cartella "Faba"
3. Al suo interno, crea "incoming" e "processed"
4. Condividi la cartella "incoming" con chi deve caricare file

## 🚀 Utilizzo

### 1. Lista File Disponibili

Vedi quali file sono pronti per essere scaricati:

```bash
./sync_from_drive.py --list
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  File disponibili su Google Drive                      ║
╚════════════════════════════════════════════════════════╝

📁 3 file trovati:

  • storia_nonna.mp3
    Dimensione: 2.34 MB
    Modificato: 2026-02-10 14:30:00

  • canzone_zio.mp3
    Dimensione: 1.87 MB
    Modificato: 2026-02-10 15:45:00

  • favola_mamma.mp3
    Dimensione: 3.12 MB
    Modificato: 2026-02-10 16:20:00
```

### 2. Sincronizza Tutti i File

Scarica e processa automaticamente tutti i file disponibili:

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01
```

**Processo automatico:**
1. 📂 Scansiona Google Drive
2. ⬇️  Scarica i file MP3
3. 🎵 Mostra opzioni di processamento:
   - Opzione 1: Tutti i file in una figura (es. album/storia multiparte)
   - Opzione 2: Una figura per ogni file (es. storie separate)
4. 🔐 Cifra e aggiunge al Faba
5. 📦 Sposta i file processati in "processed/"

### 3. Opzioni Avanzate

#### Specifica prefisso ID personalizzato

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01 --prefix 8
```

Usa range 8xxx invece del default 9xxx.

#### Usa cartella Google Drive diversa

```bash
./sync_from_drive.py --sync-all --remote gdrive:MyCustomFolder
```

## 📝 Esempi Completi

### Esempio 1: Setup Iniziale

```bash
# 1. Prima configurazione
./sync_from_drive.py --setup

# 2. Crea le cartelle su Google Drive (via browser)
# drive.google.com → Crea "Faba/incoming" e "Faba/processed"

# 3. Condividi "Faba/incoming" con chi deve caricare file

# 4. Testa la connessione
./sync_from_drive.py --list
```

### Esempio 2: Workflow Tipico

```bash
# 1. Controlla se ci sono nuovi file
./sync_from_drive.py --list

# Output:
# 📁 2 file trovati:
#   • storia_compleanno.mp3 (2.5 MB)
#   • canzone_natale.mp3 (1.8 MB)

# 2. Collega il Faba al PC
# (Es. /dev/sdb1 montato in /mnt/faba)

# 3. Sincronizza
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01

# Output:
# ⬇️  Download in corso...
#   Downloading storia_compleanno.mp3... ✓
#   Downloading canzone_natale.mp3... ✓
#
# ✓ 2 file scaricati
#
# Come vuoi processare questi file?
# 1. Crea nuova figura con tutti i file
# 2. Crea una figura per ogni file
# 3. Annulla
#
# Scelta (1-3): 2
#
# [Processa i file con add_tracks.py]
#
# ✓ 2/2 figure create
# 📦 Spostamento file processati...
#   ✓ storia_compleanno.mp3 → processed/
#   ✓ canzone_natale.mp3 → processed/
#
# ✓ Sincronizzazione completata!

# 4. Smonta il Faba
sudo umount /mnt/faba
```

### Esempio 3: Storia Multiparte

Se qualcuno carica una storia in più parti:

```
Drive/Faba/incoming:
  parte1.mp3
  parte2.mp3
  parte3.mp3
```

```bash
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01

# Scegli opzione 1: "Crea nuova figura con tutti i file"
# Risultato: K9001 con CP01.MKI, CP02.MKI, CP03.MKI
```

### Esempio 4: Più Contributori

**Setup per famiglia:**

1. Crea cartella condivisa su Google Drive
2. Invita famiglia: nonna@gmail.com, zio@gmail.com, etc.
3. Ogni persona può caricare file in "incoming/"
4. Tu sincronizzi quando vuoi

**Organizzazione file suggerita:**
```
incoming/
  nonna_storia_1.mp3
  nonna_storia_2.mp3
  zio_canzone_natale.mp3
  mamma_favola.mp3
```

## ❓ FAQ

### Q: Posso usare Dropbox invece di Google Drive?
**A:** Sì! rclone supporta molti provider. Configura con:
```bash
rclone config
# Seleziona "dropbox" invece di "drive"
```
Poi usa: `--remote dropbox:Faba`

### Q: Cosa succede se qualcuno carica file mentre sto sincronizzando?
**A:** Lo script scarica solo i file presenti al momento della scansione. I nuovi file saranno disponibili alla prossima sincronizzazione.

### Q: I file vengono cancellati da Google Drive?
**A:** No, vengono **spostati** nella cartella "processed/" con timestamp. Puoi cancellarli manualmente quando vuoi.

### Q: Posso sincronizzare senza conferma manuale?
**A:** Attualmente lo script chiede sempre conferma. Per automatizzare completamente, potresti modificare lo script, ma è più sicuro mantenere la conferma.

### Q: Cosa succede se il download fallisce a metà?
**A:** I file sono scaricati in una cartella temporanea. Se il processo fallisce, la cartella temporanea viene pulita automaticamente.

### Q: Posso sincronizzare da più cartelle Drive?
**A:** Sì, esegui lo script più volte con `--remote` diversi:
```bash
./sync_from_drive.py --sync-all --remote gdrive:Famiglia
./sync_from_drive.py --sync-all --remote gdrive:Amici
```

### Q: Come verifico la configurazione rclone?
**A:**
```bash
# Lista remotes configurati
rclone listremotes

# Testa la connessione
rclone ls gdrive:

# Lista file in una cartella
rclone ls gdrive:Faba/incoming
```

### Q: Quali formati audio sono supportati?
**A:** Solo MP3. Se hai file in altri formati (WAV, FLAC, M4A), convertili prima:
```bash
ffmpeg -i input.wav -codec:a libmp3lame -b:a 128k output.mp3
```

### Q: Posso usare questo script su Windows?
**A:** Sì, ma:
1. Installa Python 3
2. Installa rclone per Windows
3. Modifica i percorsi (es. `E:\FABA\MKI01` invece di `/mnt/faba/MKI01`)

### Q: Lo script funziona anche senza connessione internet?
**A:** No, richiede connessione per accedere a Google Drive.

## 🔐 Sicurezza e Privacy

### Token di Accesso
- rclone salva i token in `~/.config/rclone/rclone.conf`
- I token sono criptati
- Solo tu puoi accedere al tuo Drive
- Revoca accesso da: https://myaccount.google.com/permissions

### Condivisione Cartelle
- Condividi solo la cartella "incoming", non l'intera cartella "Faba"
- Gli altri utenti possono solo caricare, non vedere o modificare file processati
- Puoi revocare l'accesso in qualsiasi momento da Google Drive

### Best Practices
- Non condividere il file `rclone.conf`
- Usa sempre HTTPS (rclone lo fa di default)
- Rivedi periodicamente i permessi su Google Drive

## 🚨 Risoluzione Problemi

### Errore: "rclone non è installato"
```bash
# Linux
curl https://rclone.org/install.sh | sudo bash

# Verifica installazione
rclone version
```

### Errore: "Remote 'gdrive' non configurato"
```bash
./sync_from_drive.py --setup
# Oppure
rclone config
```

### Errore: "Cartella Faba/incoming non trovata"
- Vai su drive.google.com
- Crea manualmente le cartelle `Faba/incoming` e `Faba/processed`
- Verifica: `rclone ls gdrive:Faba`

### Errore: "Token scaduto"
```bash
rclone config reconnect gdrive:
```

### Download molto lento
- Controlla la tua connessione internet
- Google Drive potrebbe limitare il bandwidth
- Prova più tardi

### Errore: "Il modulo 'mutagen' è richiesto"
```bash
pip install mutagen
```

## 🔗 Comandi Correlati

- `add_tracks.py` - Aggiunge manualmente tracce al Faba
- `remove_ads.py` - Rimuove pubblicità
- `rclone config` - Gestisce configurazione remotes
- `rclone ls gdrive:` - Lista file su Drive
- `rclone copy` - Copia manuale file

## 📚 Risorse

- **rclone Documentation**: https://rclone.org/docs/
- **Google Drive API**: https://developers.google.com/drive
- **Supported Cloud Providers**: https://rclone.org/#providers

## 💡 Tips & Tricks

### 1. Alias per Comandi Frequenti

Aggiungi al tuo `~/.bashrc` o `~/.zshrc`:

```bash
alias faba-list='cd ~/hack-faba-storytelling && ./sync_from_drive.py --list'
alias faba-sync='cd ~/hack-faba-storytelling && ./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01'
```

Poi usa semplicemente:
```bash
faba-list
faba-sync
```

### 2. Script di Montaggio Automatico

Crea `mount_faba.sh`:
```bash
#!/bin/bash
sudo mount /dev/sdb1 /mnt/faba
cd ~/hack-faba-storytelling
./sync_from_drive.py --sync-all --faba-dir /mnt/faba/MKI01
sudo umount /mnt/faba
echo "✓ Faba aggiornato e smontato!"
```

### 3. Notifiche Push (opzionale)

Usa servizi come ntfy.sh per ricevere notifiche quando nuovi file sono caricati su Drive.

### 4. Organizzazione File su Drive

Usa prefissi nei nomi file per organizzare:
```
incoming/
  [STORIA]_cappuccetto_rosso.mp3
  [MUSICA]_canzone_natale.mp3
  [FAVOLA]_tre_porcellini.mp3
```

Poi processa in batch per tipologia.

## 📦 Backup e Archivio

I file in `processed/` sono automaticamente archiviati con timestamp. Per liberare spazio:

```bash
# Lista file vecchi (via web)
# drive.google.com/drive/folders/...

# Oppure via rclone
rclone ls gdrive:Faba/processed

# Scarica archivio completo
rclone copy gdrive:Faba/processed ~/faba_backup/

# Poi cancella da Drive se necessario
```

## 🎉 Workflow Completo: Dalla Registrazione al Faba

1. **Registra audio** (smartphone/tablet)
2. **Carica su Drive** → Faba/incoming/
3. **Collega Faba** al PC
4. **Esegui sync** → `./sync_from_drive.py --sync-all`
5. **Scegli modalità** (figura singola o multiple)
6. **Programma NFC tag** con l'ID creato (es. K9001)
7. **Smonta Faba**
8. **Test sul dispositivo** 🎵

Fatto! I tuoi contenuti personalizzati sono ora sul Faba! 🎉
