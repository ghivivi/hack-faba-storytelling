# 🎵 Faba Track Manager - ADD_TRACKS.md

Script per aggiungere nuovi file MP3 al dispositivo Faba con gestione automatica di:
- ID autoincrementali personalizzati
- Cifratura .MKI
- Tag ID3 nel formato corretto
- Rinumerazione automatica delle tracce

## 🔧 Requisiti

```bash
pip install mutagen
```

## 🚀 Utilizzo

### 1. Creare una Nuova Figura

#### Opzione A: ID Autoincrementale (Consigliato)

Lo script scansiona il disco, trova l'ID più alto nel range custom (default: 9xxx) e incrementa di 1:

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure track1.mp3 track2.mp3 track3.mp3
```

**Risultato:**
- Scansiona tutte le cartelle K* esistenti
- Trova l'ID più alto nel range 9xxx (es. K9005)
- Crea la nuova figura con ID 9006
- Processa i file:
  - `track1.mp3` → `K9006/CP01.MKI` (tag ID3: "K9006CP01")
  - `track2.mp3` → `K9006/CP02.MKI` (tag ID3: "K9006CP02")
  - `track3.mp3` → `K9006/CP03.MKI` (tag ID3: "K9006CP03")

#### Opzione B: ID Specifico

Se vuoi usare un ID specifico:

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3 --custom-id 9100
```

**Risultato:**
- Crea la cartella `K9100` con i file specificati

#### Opzione C: Prefisso Personalizzato

Per usare un range diverso (es. 8xxx invece di 9xxx):

```bash
./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3 --custom-prefix 8
```

**Risultato:**
- Scansiona solo gli ID che iniziano con 8 (8000-8999)
- Usa il prossimo ID disponibile in quel range

### 2. Aggiungere Tracce a Figura Esistente

#### Opzione A: Append (Aggiungi alla Fine)

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 newtrack.mp3
```

**Esempio:**

Prima:
```
K0015/
  ├── CP01.MKI (tag: "K0015CP01")
  ├── CP02.MKI (tag: "K0015CP02")
  └── CP03.MKI (tag: "K0015CP03")
```

Dopo:
```
K0015/
  ├── CP01.MKI (tag: "K0015CP01")
  ├── CP02.MKI (tag: "K0015CP02")
  ├── CP03.MKI (tag: "K0015CP03")
  └── CP04.MKI (tag: "K0015CP04") ← nuovo
```

#### Opzione B: Inserimento con Rinumerazione

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 intro.mp3 --position 2
```

**Esempio:**

Prima:
```
K0015/
  ├── CP01.MKI (prologo)
  ├── CP02.MKI (capitolo 1)
  ├── CP03.MKI (capitolo 2)
  └── CP04.MKI (epilogo)
```

Comando: Inserisci `intro.mp3` alla posizione 2

Dopo:
```
K0015/
  ├── CP01.MKI (prologo)          ← invariato
  ├── CP02.MKI (intro.mp3)         ← nuovo file inserito
  ├── CP03.MKI (ex CP02)           ← rinumerato, tag aggiornato
  ├── CP04.MKI (ex CP03)           ← rinumerato, tag aggiornato
  └── CP05.MKI (ex CP04)           ← rinumerato, tag aggiornato
```

**Cosa succede:**
1. Lo script decifra tutti i file dalla posizione 2 in poi
2. Aggiorna i loro tag ID3 con i nuovi numeri
3. Ricifra i file con i nuovi nomi
4. Inserisce il nuovo file nella posizione 2

### 3. Aggiungere Più File in una Volta

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 track1.mp3 track2.mp3 --position 3
```

**Risultato:**
- Inserisce `track1.mp3` e `track2.mp3` a partire dalla posizione 3
- Rinumera tutti i file successivi di 2 posizioni

## 📝 Esempi Pratici

### Esempio 1: Creare una Storia Personalizzata

Hai registrato 5 tracce audio per una storia personalizzata:

```bash
cd /home/user/my-story/
ls -1
intro.mp3
capitolo1.mp3
capitolo2.mp3
capitolo3.mp3
epilogo.mp3

# Crea nuova figura
./add_tracks.py /mnt/faba/MKI01 --new-figure intro.mp3 capitolo1.mp3 capitolo2.mp3 capitolo3.mp3 epilogo.mp3
```

Output:
```
═══════════════════════════════════════════════
  CREAZIONE NUOVA FIGURA
═══════════════════════════════════════════════

📁 Cartella: K9001
   ID figura: 9001
   Tracce: 5

   CP01: intro.mp3
   CP02: capitolo1.mp3
   CP03: capitolo2.mp3
   CP04: capitolo3.mp3
   CP05: epilogo.mp3

Confermi la creazione? (yes/no): yes

✓ Cartella K9001 creata
✓ CP01.MKI creato da intro.mp3
✓ CP02.MKI creato da capitolo1.mp3
✓ CP03.MKI creato da capitolo2.mp3
✓ CP04.MKI creato da capitolo3.mp3
✓ CP05.MKI creato da epilogo.mp3

✓ Figura K9001 creata con successo!
  Tracce: 5
```

### Esempio 2: Aggiungere un Capitolo Mancante

Ti accorgi di aver dimenticato un capitolo tra il capitolo 1 e 2:

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K9001 capitolo1-bis.mp3 --position 3
```

Output:
```
═══════════════════════════════════════════════
  AGGIUNTA TRACCE A FIGURA ESISTENTE
═══════════════════════════════════════════════

📁 Cartella: K9001
   Tracce esistenti: 5
   Nuove tracce: 1
   Posizione inserimento: 3

Nuove tracce da aggiungere:
   CP03: capitolo1-bis.mp3

⚠️  Le tracce dalla posizione 3 in poi verranno rinumerate:
   CP03.MKI → CP04.MKI
   CP04.MKI → CP05.MKI
   CP05.MKI → CP06.MKI

Confermi l'operazione? (yes/no): yes

📝 Rinumerazione tracce esistenti...
  ✓ CP05.MKI → CP06.MKI
  ✓ CP04.MKI → CP05.MKI
  ✓ CP03.MKI → CP04.MKI

➕ Aggiunta nuove tracce...
  ✓ CP03.MKI creato da capitolo1-bis.mp3

✓ Tracce aggiunte con successo a K9001!
  Totale tracce: 6
```

### Esempio 3: Estendere una Figura Esistente

Aggiungi nuovi episodi a una figura già esistente:

```bash
./add_tracks.py /mnt/faba/MKI01 --add-to K0015 episodio-extra.mp3
```

## ❓ FAQ

### Q: Quale range di ID dovrei usare per i miei contenuti custom?
**A:** Consigliamo il range **9000-9999** per contenuti personalizzati, per evitare conflitti con figure originali Faba (range 0000-8999).

### Q: Posso usare qualsiasi ID?
**A:** Sì, ma è meglio seguire una convenzione:
- **0000-8999**: Riservato a figure Faba originali
- **9000-9999**: Consigliato per contenuti custom
- Lo script usa 9xxx come default per evitare conflitti

### Q: Cosa succede ai tag ID3 esistenti nei miei MP3?
**A:** Lo script **sovrascrive** tutti i tag ID3 con il formato richiesto dal Faba (`KxxxxCPyy`). Altri tag come artista, album, etc. vengono rimossi.

### Q: Posso usare file MP3 di qualsiasi qualità?
**A:** Sì, ma considera:
- Il Faba ha uno speaker mono di qualità limitata
- File a 128kbps sono più che sufficienti
- File più grandi occupano più spazio sulla microSD

### Q: Come verifico che i file siano stati creati correttamente?
**A:** Puoi decifrare un file per controllare:
```bash
java MKIDecipher K9001/CP01.MKI test.mp3
ffprobe test.mp3  # Verifica il file
```

### Q: Posso rinumerare file esistenti senza aggiungerne di nuovi?
**A:** Non direttamente con questo script. Usa `remove_ads.py --renumber` per rinumerare dopo aver rimosso file, oppure esegui una rinumerazione manuale.

### Q: Cosa succede se inserisco una traccia alla posizione 1?
**A:** Tutti i file esistenti vengono rinumerati (+1), e il nuovo file diventa CP01.MKI.

### Q: Lo script preserva i file originali?
**A:** Sì:
- I file MP3 originali **non vengono modificati**
- Vengono create **copie cifrate** come .MKI
- Puoi conservare i tuoi MP3 originali per backup

### Q: Posso annullare un'operazione?
**A:** Lo script chiede sempre conferma prima di procedere. Se rispondi "no", l'operazione viene annullata senza modifiche.

### Q: Come organizzo i miei contenuti personalizzati?
**A:** Suggerimenti:
```
9000-9099: Audiolibri
9100-9199: Musica personalizzata
9200-9299: Storie registrate da te
9300-9399: Podcast per bambini
9400-9999: Altri contenuti
```

## 🛡️ Sicurezza

- ✅ **Conferma richiesta**: Lo script chiede sempre conferma prima di modificare file
- ✅ **Validazione ID**: Controlla che l'ID non esista già
- ✅ **Gestione errori**: In caso di errore durante la creazione di una nuova figura, la cartella viene rimossa
- ✅ **Backup consigliato**: Fai sempre un backup completo della microSD prima di operazioni massive

## 🔍 Log e Debug

Lo script mostra dettagli in tempo reale:
- Cartelle create/modificate
- File processati
- Eventuali errori con messaggi chiari

## 🚨 Risoluzione Problemi

### Errore: "Il modulo 'mutagen' è richiesto"
```bash
pip install mutagen
```

### Errore: "Cartella K9001 esiste già"
Hai già una figura con quell'ID. Usa:
- `--custom-id` con un ID diverso
- Lascia che lo script scelga automaticamente il prossimo ID disponibile

### Errore: "File non è un MP3"
Solo file `.mp3` sono supportati. Se hai file in altri formati (FLAC, WAV, etc.), convertili prima:
```bash
ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
```

### File troppo grandi
Se i file MP3 sono molto grandi (>10MB), considera di ridurre la qualità:
```bash
ffmpeg -i input.mp3 -codec:a libmp3lame -b:a 128k output.mp3
```

## 💡 Best Practices

1. **Usa sempre l'autoincrementale** per evitare conflitti di ID
2. **Testa con una figura prima** di processare molti file
3. **Fai backup della microSD** prima di operazioni massive
4. **Nomina i file MP3 in ordine** (es. `01-intro.mp3`, `02-capitolo1.mp3`) per facilitare l'elaborazione
5. **Mantieni una documentazione** di quali ID hai usato per quali contenuti

## 📚 Workflow Completo: Dalla Registrazione al Faba

### 1. Registrazione/Preparazione Audio
```bash
# Registra o converti i tuoi file in MP3
ffmpeg -i recording.wav -codec:a libmp3lame -qscale:a 2 track.mp3
```

### 2. Organizzazione File
```bash
# Organizza i file nella sequenza desiderata
mkdir my-story
cd my-story
cp ~/recordings/intro.mp3 01-intro.mp3
cp ~/recordings/part1.mp3 02-capitolo1.mp3
cp ~/recordings/part2.mp3 03-capitolo2.mp3
```

### 3. Creazione Figura
```bash
# Crea la figura sul Faba
./add_tracks.py /mnt/faba/MKI01 --new-figure *.mp3
```

### 4. Programmazione NFC Tag
```bash
# Programma il tag NFC con l'ID della figura (es. K9001)
# Usa un'app NFC come "NFC Tools" su Android/iOS
# Scrivi record: Text/Plain → "K9001"
```

### 5. Test
- Posiziona il tag NFC programmato sul Faba
- Verifica che la riproduzione funzioni correttamente
- Controlla l'ordine delle tracce

## 🔗 Comandi Correlati

- `remove_ads.py` - Rimuove pubblicità e rinumera tracce
- `createFigure.sh` - Script bash alternativo (più manuale)
- `MKICipher.java` - Cifra file MP3 singoli
- `MKIDecipher.java` - Decifra file .MKI per debug

## 📄 Licenza

Questo script fa parte del progetto MyFaba/Faba+ Story Telling Box.
