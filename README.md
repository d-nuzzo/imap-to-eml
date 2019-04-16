# imap-to-eml

Scarica le mail da un account IMAP in SSL e le memorizza su una cartella locale in singoli files eml.

## Sintassi:

```
imap_to_eml.py [-h] [-v] [-t] [-a] -s HOSTNAME -u USERNAME
               [--pwd PASSWORD] [-p PORT]
               [--log {debug,info,warning,error}] [-d DESTINATION]
```

## Argomenti:
```
  -h, --help      visualizza la guida sintetica ed esce
  -v, --verbose   visualizza informazioni più dettagliate
  -t, --test      solo test, non salva i file eml!
  -a, --ask       chiede conferma per ogni singola mailbox (cartella)
  -s HOSTNAME     IMAP server, esempio: imap.gmail.com
  -u USERNAME     IMAP username, esempio: mario.rossi@gmail.com
  --pwd PASSWORD  IMAP password
  -p PORT         porta IMAP, default: 993
  --log {debug,info,warning,error}
                  log level
  -d DESTINATION  Cartella locale dove salvare i file .eml, di default crea una sottocartella emails
```

## Note:
L'help del programma è volutamente in inglese.


  
