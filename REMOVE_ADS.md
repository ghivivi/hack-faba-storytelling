# Guida: Rimozione Pubblicità Faba

## 📋 Panoramica

Lo script `remove_ads.py` identifica e rimuove in modo sicuro i file CP01.MKI pubblicitari dalle cartelle del tuo dispositivo Faba.

## 🔍 Come Funziona

Lo script identifica le pubblicità basandosi sulla **dimensione del file**:
- **Pubblicità**: CP01.MKI tra 440-470KB (~448KB)
- **Contenuto vero**: CP01.MKI con dimensioni diverse

### Cartelle Identificate (esempio)

✅ **Pubblicità** (verranno rimosse):
- K0010/CP01.MKI (448.5KB)
- K0011/CP01.MKI (448.5KB)
- K0012/CP01.MKI (448.5KB)
- K0013/CP01.MKI (448.5KB)

✅ **Contenuto da Preservare** (NON verranno toccate):
- K0014/CP01.MKI (106.0KB) - Dimensione diversa
- K0015/CP01.MKI (1.5MB) - Contenuto vero
- Altre cartelle con CP01 di dimensioni diverse

## 🚀 Utilizzo

### 1. Modalità Dry-Run (Sicura - Consigliata prima)

Mostra cosa verrebbe rimosso **senza modificare nulla**:

```bash
./remove_ads.py /mnt/faba/MKI01 --dry-run
```

oppure

```bash
python3 remove_ads.py /mnt/faba/MKI01 --dry-run
```

### 2. Modalità Backup (Consigliata)

Sposta le pubblicità in una cartella di backup invece di cancellarle:

```bash
./remove_ads.py /mnt/faba/MKI01 --backup
```

**Risultato:**
- Crea una cartella `faba_ads_backup_YYYYMMDD_HHMMSS/`
- Sposta tutti i CP01 pubblicitari nella cartella backup
- Mantiene la struttura delle cartelle (K0010/, K0011/, etc.)
- Puoi ripristinarli se necessario

### 3. Modalità Delete (Attenzione!)

Cancella **definitivamente** le pubblicità:

```bash
./remove_ads.py /mnt/faba/MKI01 --delete
```

⚠️ **ATTENZIONE:** Questa operazione è irreversibile!
- Ti verrà chiesto di digitare "DELETE" per confermare
- I file verranno cancellati permanentemente

## 📊 Output e Log

Lo script crea un file di log dettagliato:
- `remove_ads_log_YYYYMMDD_HHMMSS.txt`
- Contiene l'elenco di tutte le operazioni eseguite
- Utile per tracciare cosa è stato fatto

## 🛡️ Sicurezza

Lo script è progettato per essere **estremamente sicuro**:

1. ✅ **Analisi preliminare**: Mostra sempre cosa verrà fatto prima di procedere
2. ✅ **Conferma richiesta**: In modalità --backup e --delete chiede conferma
3. ✅ **Protezione contenuti**: NON tocca file CP01 con dimensioni diverse dalle pubblicità
4. ✅ **Log dettagliato**: Registra tutte le operazioni per tracciabilità
5. ✅ **Modalità dry-run default**: Se non specifichi modalità, fa solo simulazione

## 📝 Esempi Pratici

### Caso 1: Primo utilizzo (esplorativo)

```bash
# 1. Analizza cosa c'è (nessuna modifica)
./remove_ads.py /mnt/faba/MKI01 --dry-run

# 2. Se sei soddisfatto, fai backup
./remove_ads.py /mnt/faba/MKI01 --backup
```

### Caso 2: Disco esterno Faba

```bash
# Supponendo che il Faba sia montato in /media/usb/FABA
./remove_ads.py /media/usb/FABA/MKI01 --backup
```

### Caso 3: Ripristino dal backup

Se hai fatto --backup e vuoi ripristinare:

```bash
# Copia i file dal backup alla posizione originale
cp -r faba_ads_backup_20260210_134215/K0010/CP01.MKI /mnt/faba/MKI01/K0010/
cp -r faba_ads_backup_20260210_134215/K0011/CP01.MKI /mnt/faba/MKI01/K0011/
# ... etc
```

## ❓ FAQ

### Q: È sicuro usare questo script?
**A:** Sì! Lo script è progettato per essere molto conservativo e protegge i contenuti veri. Usa prima `--dry-run` per vedere cosa verrebbe fatto.

### Q: E se cancello qualcosa per errore?
**A:** Usa sempre la modalità `--backup` invece di `--delete`. In questo modo i file vengono spostati, non cancellati, e puoi ripristinarli.

### Q: Come faccio a sapere quali sono pubblicità?
**A:** Lo script identifica automaticamente i file CP01 con dimensione ~448KB (440-470KB). I contenuti veri hanno di solito dimensioni molto diverse.

### Q: Funziona su tutto il disco?
**A:** Sì! Lo script cerca ricorsivamente in tutte le cartelle K* all'interno della directory che specifichi.

### Q: Cosa succede se non ci sono pubblicità?
**A:** Lo script ti avviserà che non ci sono pubblicità da rimuovere e uscirà senza fare nulla.

### Q: Posso usarlo su Faba+?
**A:** Lo script è progettato per Faba originale (red cube). Per Faba+ potrebbe essere necessario verificare il formato dei file.

## 🔧 Requisiti

- Python 3.6 o superiore
- Accesso in lettura/scrittura alla directory del Faba

## 📄 Note Tecniche

### Criterio di Identificazione

Il criterio principale è la **dimensione del file**:
- I file CP01 pubblicitari hanno tipicamente dimensione costante (~449KB)
- I contenuti veri hanno dimensioni variabili (da pochi KB a diversi MB)

### Struttura Directory

Lo script si aspetta una struttura come:
```
MKI01/
├── K0010/
│   ├── CP01.MKI
│   ├── CP02.MKI
│   └── ...
├── K0011/
│   ├── CP01.MKI
│   ├── CP02.MKI
│   └── ...
...
```

## 🤝 Supporto

Se hai problemi o domande:
1. Controlla il file di log `remove_ads_log_*.txt`
2. Usa prima `--dry-run` per vedere cosa succederà
3. Apri un issue su GitHub per assistenza

## ⚠️ Disclaimer

Questo script modifica i file sul tuo dispositivo Faba. Anche se è progettato per essere sicuro:
- Fai sempre un backup completo del tuo dispositivo prima di procedere
- Testa prima con `--dry-run`
- Usa `--backup` invece di `--delete` quando possibile
- L'autore non è responsabile per eventuali perdite di dati

---

**Buon ascolto senza pubblicità! 🎵**
