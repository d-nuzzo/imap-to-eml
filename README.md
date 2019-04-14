# imap-to-eml

Scarica le mail da un account IMAP in SSL e le memorizza su una cartella locale in singoli files eml.

## usage

`imap_to_eml.py [-h] [-v] -s HOSTNAME -u USERNAME [-p PASSWORD] [-d DESTINATION]`

## description

Dump a IMAP account into .eml files

## arguments
```
optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   increase output verbosity
  -s HOSTNAME     IMAP server, like: imap.gmail.com
  -u USERNAME     IMAP username, like: mario.rossi@gmail.com
  -p PASSWORD     IMAP password
  -d DESTINATION  Local folder where to save .eml files
  ```
  
