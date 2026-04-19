# 💾 Faba Backup Tool - BACKUP.md

Script per creare backup completo del disco Faba con compressione massima. **Essenziale** prima di operazioni che modificano il disco.

## 🎯 Perché fare backup?

Prima di operazioni come:
- ❌ **Rimozione pubblicità** (`remove_ads.py`)
- ➕ **Aggiunta tracce** (`add_tracks.py`)
- 🔄 **Rinumerazione file**
- 🔧 **Modifiche manuali**

**Un backup completo ti protegge** da:
- Errori durante le operazioni
- File corrotti
- Perdita accidentale di dati
- Problemi hardware del disco

## 🚀 Utilizzo Rapido

### 1. Backup Base (Compressione Massima)

```bash
./backup_faba.py /mnt/faba/MKI01
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  Faba Backup Tool - Creazione backup...                ║
╚════════════════════════════════════════════════════════╝

📂 Scansione directory Faba...

Statistiche:
  Figure trovate: 15
  File totali: 120
  Dimensione totale: 150.45 MB

📦 Creazione backup: faba_backup_20260210_143022.zip
   Compressione: Massima (può richiedere tempo)

  📁 K0010 (8 tracce)... ✓
  📁 K0011 (8 tracce)... ✓
  ...

✓ Backup creato con successo!

Dettagli backup:
  File: ./backups/faba_backup_20260210_143022.zip
  Dimensione originale: 150.45 MB
  Dimensione backup: 48.23 MB
  Compressione: 67.9%

🔐 Calcolo checksum...
  SHA256: a3f5c8e9...

📝 Metadata salvato in:
  ./backups/faba_backup_20260210_143022_metadata.json

🔍 Verifica integrità backup...
✓ Backup verificato correttamente
  Figure nel backup: 15
  Data backup: 2026-02-10T14:30:22.123456

═══════════════════════════════════════════════════════════
✓ Backup completato e verificato!
═══════════════════════════════════════════════════════════

Backup salvato in:
  ./backups/faba_backup_20260210_143022.zip
```

### 2. Backup Veloce (Compressione Standard)

```bash
./backup_faba.py /mnt/faba/MKI01 --fast
```

**Quando usarlo:**
- Backup rapidi durante sessioni di lavoro
- Test frequenti
- Disco SSD lento in scrittura

**Differenze:**
- 🚀 3-4x più veloce
- 💾 File ~20-30% più grande
- ✅ Comunque sicuro

### 3. Backup + Upload Google Drive

```bash
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive
```

**Requisiti:**
- rclone configurato (`./sync_from_drive.py --setup`)
- Connessione internet

**Risultato:**
- Backup locale creato
- Upload automatico su `gdrive:Faba/backups/`
- Doppia sicurezza (locale + cloud)

### 4. Backup in Cartella Specifica

```bash
./backup_faba.py /mnt/faba/MKI01 --output ~/my-backups
```

**Utile per:**
- Salvare su disco esterno
- Organizzare backup per data
- Archiviazione NAS

## 📋 Comandi Avanzati

### Lista Backup Disponibili

```bash
./backup_faba.py --list
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║  Backup Disponibili                                    ║
╚════════════════════════════════════════════════════════╝

📦 faba_backup_20260210_143022.zip
   Data: 2026-02-10 14:30:22
   Dimensione: 48.23 MB
   Figure: 15
   File: 120
   Compressione: 67.9%
   SHA256: a3f5c8e9...

📦 faba_backup_20260209_093015.zip
   Data: 2026-02-09 09:30:15
   Dimensione: 47.89 MB
   Figure: 14
   File: 112
   Compressione: 68.2%
   SHA256: b2e4d7a1...
```

### Verifica Integrità Backup

```bash
./backup_faba.py --verify backups/faba_backup_20260210_143022.zip
```

**Output:**
```
🔍 Verifica integrità backup...
✓ Backup verificato correttamente
  Figure nel backup: 15
  Data backup: 2026-02-10T14:30:22.123456
```

## 📦 Cosa Include il Backup

### Struttura ZIP
```
faba_backup_20260210_143022.zip
├── K0010/
│   ├── CP01.MKI
│   ├── CP02.MKI
│   └── ...
├── K0011/
│   ├── CP01.MKI
│   └── ...
├── ...
└── backup_metadata.json  (informazioni sul backup)
```

### File Metadata (JSON)
```json
{
  "backup_date": "2026-02-10T14:30:22.123456",
  "source_path": "/mnt/faba/MKI01",
  "compression_level": 9,
  "backup_size": 50567890,
  "compression_ratio": 67.9,
  "checksum_sha256": "a3f5c8e9...",
  "statistics": {
    "total_files": 120,
    "total_size": 157734912,
    "figures": [
      {
        "id": "K0010",
        "tracks": 8,
        "size": 12345678
      },
      ...
    ]
  }
}
```

## 🔄 Ripristino da Backup

### Ripristino Completo

```bash
# 1. Estrai il backup
unzip backups/faba_backup_20260210_143022.zip -d /mnt/faba/MKI01/

# 2. Verifica che tutto sia stato estratto
ls -la /mnt/faba/MKI01/
```

### Ripristino Figura Singola

```bash
# Estrai solo una figura specifica
unzip backups/faba_backup_20260210_143022.zip "K0015/*" -d /mnt/faba/MKI01/
```

### Ripristino File Specifico

```bash
# Estrai un singolo file
unzip backups/faba_backup_20260210_143022.zip "K0015/CP03.MKI" -d /mnt/faba/MKI01/
```

## 📝 Workflow Consigliato

### Prima di Modifiche Importanti

```bash
# 1. Collega il Faba
sudo mount /dev/sdb1 /mnt/faba

# 2. Crea backup
./backup_faba.py /mnt/faba/MKI01

# 3. Esegui modifiche
./remove_ads.py /mnt/faba/MKI01 --backup --renumber

# 4. Se tutto OK, smonta
sudo umount /mnt/faba

# 5. (Opzionale) Archivia vecchi backup dopo qualche giorno
```

### Backup Periodici Automatici

Crea uno script `auto_backup.sh`:

```bash
#!/bin/bash
# Auto backup del Faba ogni volta che viene collegato

FABA_DIR="/mnt/faba/MKI01"
BACKUP_DIR="$HOME/faba-backups"

# Controlla se il Faba è montato
if [ -d "$FABA_DIR" ]; then
    echo "Faba rilevato, creazione backup..."
    ./backup_faba.py "$FABA_DIR" --output "$BACKUP_DIR" --fast
else
    echo "Faba non collegato"
fi
```

### Backup su NAS/Server Remoto

```bash
# Backup locale + copia su NAS
./backup_faba.py /mnt/faba/MKI01 --output ~/backups

# Copia su NAS (via rsync)
rsync -av ~/backups/faba_backup_*.zip user@nas:/volume1/backups/faba/
```

## 💡 Best Practices

### 1. **Strategia 3-2-1**
- **3** copie dei dati (originale + 2 backup)
- **2** tipi di media diversi (locale + cloud)
- **1** copia off-site (Google Drive, NAS remoto)

Esempio:
```bash
# Backup locale
./backup_faba.py /mnt/faba/MKI01

# Backup su disco esterno
./backup_faba.py /mnt/faba/MKI01 --output /media/external/backups

# Backup su cloud
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive
```

### 2. **Frequenza Backup**
- ✅ **Prima di ogni modifica**: Sempre
- ✅ **Dopo aggiunte importanti**: Dopo aver aggiunto nuove figure
- ✅ **Periodicamente**: Ogni 1-2 mesi anche se non modifichi

### 3. **Conservazione Backup**
- **Backup recenti** (ultimi 3): Mantieni sempre
- **Backup settimanali**: Mantieni ultimo mese
- **Backup mensili**: Mantieni ultimo anno
- **Spazio insufficiente?** Carica su cloud e rimuovi vecchi locali

### 4. **Verifica Backup**

```bash
# Verifica subito dopo creazione
./backup_faba.py --verify backups/faba_backup_LATEST.zip

# Verifica periodica (ogni 3 mesi)
for backup in backups/*.zip; do
    echo "Verifico $backup..."
    ./backup_faba.py --verify "$backup"
done
```

### 5. **Nomenclatura**

I backup usano timestamp: `faba_backup_YYYYMMDD_HHMMSS.zip`

Per backup speciali, rinomina dopo creazione:
```bash
# Backup prima di una modifica importante
mv backups/faba_backup_20260210_143022.zip \
   backups/faba_before_remove_ads.zip

# Backup versione "golden master"
mv backups/faba_backup_20260210_143022.zip \
   backups/faba_golden_master_2026.zip
```

## ❓ FAQ

### Q: Quanto spazio occupano i backup?
**A:** Dipende dal contenuto:
- **Con compressione massima**: ~30-40% della dimensione originale
- **Con compressione veloce**: ~50-60% della dimensione originale
- **Esempio**: 150MB originali → 45-50MB compressi (massima) o 75-90MB (veloce)

### Q: Quanto tempo richiede un backup?
**A:** Dipende da:
- **Compressione massima**: 2-5 minuti per 150MB
- **Compressione veloce**: 30-90 secondi per 150MB
- **Upload Drive**: +2-10 minuti (dipende da connessione)

### Q: Posso interrompere un backup?
**A:** Sì, premi `Ctrl+C`. Il file parziale verrà creato ma non sarà valido. Usa `--verify` per controllare.

### Q: I backup sono compatibili con Windows/Mac?
**A:** Sì, sono file ZIP standard. Puoi estrarli con qualsiasi tool:
- **Windows**: Click destro → Estrai
- **Mac**: Doppio click
- **Linux**: `unzip backup.zip`

### Q: Posso fare backup incrementali?
**A:** No, ogni backup è completo. Per backup incrementali considera:
- `rsync` con hard links
- Sistemi dedicati come `restic` o `borg`

### Q: Come gestisco backup molto grandi (>500MB)?
**A:** Considera:
1. **Split ZIP**: Dividi in più file
   ```bash
   zip -s 100m backup.zip /mnt/faba/*
   ```
2. **Backup selettivo**: Fai backup solo di alcune figure
3. **Archiviazione cloud**: Usa Google Drive per storage illimitato

### Q: Il checksum garantisce integrità?
**A:** Sì, SHA256 è sicuro. Se il checksum corrisponde, il backup è identico all'originale.

### Q: Posso automatizzare i backup?
**A:** Sì, vedi sezione "Backup Periodici Automatici" sopra. Puoi usare:
- Cron job
- udev rules (Linux)
- Automator (Mac)
- Task Scheduler (Windows)

### Q: Cosa fare se il backup fallisce?
**A:**
1. Controlla spazio disco: `df -h`
2. Verifica permessi: `ls -la /mnt/faba`
3. Prova compressione veloce: `--fast`
4. Controlla se il disco Faba è leggibile

### Q: Backup su Google Drive è sicuro?
**A:** Sì:
- Trasferimento criptato (HTTPS)
- I file sono tuoi privati
- Puoi criptare il ZIP prima dell'upload se vuoi extra sicurezza

## 🔐 Sicurezza e Privacy

### Criptazione Backup (Opzionale)

Se vuoi criptare i backup prima di caricarli su cloud:

```bash
# 1. Crea backup normale
./backup_faba.py /mnt/faba/MKI01

# 2. Cripta con GPG
gpg --symmetric --cipher-algo AES256 backups/faba_backup_20260210_143022.zip

# 3. Carica il file .gpg su Drive
rclone copy backups/faba_backup_20260210_143022.zip.gpg gdrive:Faba/backups/

# 4. Per decifrare:
gpg --decrypt backups/faba_backup_20260210_143022.zip.gpg > restored_backup.zip
```

### Permessi File

I backup mantengono la struttura ma non i permessi originali. Dopo ripristino:
```bash
chmod -R 755 /mnt/faba/MKI01/K*
```

## 🚨 Risoluzione Problemi

### Errore: "Permission denied"
```bash
# Esegui con sudo se necessario
sudo ./backup_faba.py /mnt/faba/MKI01
```

### Errore: "No space left on device"
```bash
# Controlla spazio disponibile
df -h

# Usa compressione veloce (file più grande ma più veloce)
./backup_faba.py /mnt/faba/MKI01 --fast

# Oppure specifica destinazione con più spazio
./backup_faba.py /mnt/faba/MKI01 --output /media/external/backups
```

### Backup ZIP corrotto
```bash
# Verifica integrità
./backup_faba.py --verify backups/backup_file.zip

# Se corrotto, elimina e ricrea
rm backups/backup_file.zip
./backup_faba.py /mnt/faba/MKI01
```

### Upload Drive fallito
```bash
# Verifica configurazione rclone
rclone listremotes

# Ri-configura se necessario
./sync_from_drive.py --setup

# Testa connessione
rclone ls gdrive:

# Riprova upload manuale
rclone copy backups/backup_file.zip gdrive:Faba/backups/
```

## 📊 Statistiche e Monitoring

### Script di Report

Crea `backup_report.sh`:
```bash
#!/bin/bash
echo "=== Faba Backup Report ==="
echo "Backup directory: ./backups"
echo ""

# Conta backup
echo "Numero backup: $(ls backups/faba_backup_*.zip 2>/dev/null | wc -l)"

# Spazio occupato
echo "Spazio totale: $(du -sh backups 2>/dev/null | cut -f1)"

# Backup più recente
latest=$(ls -t backups/faba_backup_*.zip 2>/dev/null | head -1)
if [ -n "$latest" ]; then
    echo "Ultimo backup: $(basename $latest)"
    echo "Data: $(stat -f %Sm -t "%Y-%m-%d %H:%M" "$latest" 2>/dev/null || stat -c %y "$latest")"
fi
```

## 🔗 Integrazione con Altri Script

### Auto-backup Prima di Modifiche

Modifica `remove_ads.py` per fare backup automatico:

```python
# All'inizio di remove_ads.py
print("Creazione backup di sicurezza...")
subprocess.run(['./backup_faba.py', str(faba_dir), '--fast'])
```

### Backup Come Hook

Crea hook per operazioni critiche:
```bash
# ~/.claude/hooks/pre-modify-faba.sh
#!/bin/bash
echo "Auto-backup attivato..."
./backup_faba.py /mnt/faba/MKI01 --fast
```

## 📚 Comandi Veloci di Riferimento

```bash
# Backup standard
./backup_faba.py /mnt/faba/MKI01

# Backup veloce
./backup_faba.py /mnt/faba/MKI01 --fast

# Backup + cloud
./backup_faba.py /mnt/faba/MKI01 --upload-to-drive

# Lista backup
./backup_faba.py --list

# Verifica backup
./backup_faba.py --verify backups/backup.zip

# Ripristino completo
unzip backups/backup.zip -d /mnt/faba/MKI01/

# Ripristino singola figura
unzip backups/backup.zip "K0015/*" -d /mnt/faba/MKI01/
```

## 🎉 Conclusione

**Il backup è la tua rete di sicurezza!**

Prima di qualsiasi operazione sul Faba:
1. ✅ Collega il disco
2. ✅ **Crea backup**: `./backup_faba.py /mnt/faba/MKI01`
3. ✅ Esegui modifiche
4. ✅ Testa risultato
5. ✅ Mantieni il backup per almeno 1 settimana

**Tempo investito in backup: 2-5 minuti**
**Tempo per ricostruire tutto da zero: ore/giorni**

La scelta è facile! 💾🛡️
