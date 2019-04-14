
#!/usr/bin/env python
#-*- coding:utf-8 -*-

import getpass, imaplib, os, sys, re, argparse

# Informazioni sul programma:
name = "imap_to_eml.py"
version = "1.0"
description = "Dump a IMAP account into .eml files"
author = "Daniele Nuzzo"

# Funzione che pulisce lo schermo:
def clearscreen():
    
    if os.name=='nt':
        os.system('cls')
    else:
        os.system('clear')

# Funzione che stampa l'intestazione con i dati del programma:
def print_header():

    clearscreen()
    print("*"*42)
    print("* NOME:      ", name)
    print("* VERSIONE:  ", version)
    print("* AUTORE:    ", author)
    print("* LICENZA:    BSD Semplificata")
    print("*")
    print("*", description)
    print("*"*42)
    print()

# Funzione usata per impostare la directory locale di destinazione dei file eml alla sottocartella 
# email della directory del programma:
def default_destination():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    if os.name=='nt':
        return dir_path + '\\email'
    else:
        return dir_path + '/email'

# Funzione che estrae da una linea restituita da list() i valori flags, delimiter e mailbox_name
def split_line_response(line):

    # Utilizza una re per scomporre i 3 valori di ogni singola linea
    # es: b'(\\HasNoChildren) "/" INBOX' diventa ('\\HasNoChildren', '/', 'INBOX')
    re_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
    # Prima di usare la re bisogna effettuare la decodifica in utf-8:    
    flags, delimiter, mailbox_name = re_pattern.match(line.decode('utf-8')).groups()
    # Bisogna eliminare i doppi apici nei nomi delle mailboxes
    # perchè nel caso ci siano spazi, vengono aggiunti dal server:
    mailbox_name = mailbox_name.strip('"')
    return (flags, delimiter, mailbox_name)

def main():

    # Gestione parametri da linea di comando:
    parser = argparse.ArgumentParser(description="Dump a IMAP account into .eml files")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument('-s', dest='hostname', help="IMAP server, like: imap.gmail.com", required=True)
    parser.add_argument('-u', dest='username', help="IMAP username, like: mario.rossi@gmail.com", required=True)
    parser.add_argument('-p', dest='password', help="IMAP password", default="")
    parser.add_argument('-d', dest='destination', help="Local folder where to save .eml files, default: ./emails", default=default_destination())
    args = parser.parse_args()

    # Visualizza le informazioni sul programma:
    print_header()

    # Imposta Server Imap e Nome Utente:
    hostname = args.hostname
    username = args.username

    # Chiede la password se non fornita tramite parametro, senza visualizzarla durante la digitazione:
    if args.password=="":
        password = getpass.getpass()
    else:
        password = args.password

    # Imposta la cartella locale per il salvataggio dei files eml e la crea se non esiste:
    local_folder = args.destination
    if not os.path.exists(local_folder):
        try:
            os.makedirs(local_folder)
        except Exception as e:
            print(e)
            exit(1)

    # Visualizza la configuraione se in modalità verbose:
    if args.verbose:
        print('Server IMAP: ', hostname)
        print('Nome utente: ', username)
        print('Destinazione: ', local_folder)

    # Effettua il login, se si verifica un errore esce dal programma:
    m = imaplib.IMAP4_SSL(hostname)
    try:
         m.login(username, password)
    except:
        print('Errore durante il login!')
        exit(1)
   
    try:
        # Visualizza le capacità del Server se in modalità verbose:
        if args.verbose:
            print('Capacità:', m.capabilities)
        
        # Estrae la lista delle mailboxes:
        status, data = m.list()

        # Visualizza lo status del Server se in modalità verbose:
        if args.verbose:
            print('Stato: ', repr(status))
            print('Elenco mailboxes:')

        # Elabora in un ciclo le singole mailboxes (cartelle di posta sul Server):
        for line in data:
            
            # Estrae i dati della casella eseguendo il parsing della linea relativa alla mailbox:
            flags, delimiter, mailbox = split_line_response(line)
            
            # Visualizza le informazioni se in modalità verbose:
            # Numero totale messaggi, Numero nuovi messaggi, UID prossimo messaggio (i server qui spesso restituiscono 
            # erroneamente un contatore non univoco), ultimo UID valido, numero messaggi non letti)
            if args.verbose:
                print(flags, m.status(mailbox, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)'))
            
            try:

                # Seleziona la mailbox in sola lettura:
                m.select(mailbox, readonly=True)
                # Effettua una ricerca di tutti i messaggi:
                typ, msg_ids = m.search(None, 'ALL')
                
                # Visualizza gli ID (non univoci) delle mail trovate se in modalità verbose:
                if args.verbose:
                    print(mailbox, typ, msg_ids)
                
                # Elabora in un ciclo i singoli messaggi (ognuno con il proprio id):
                for num in msg_ids[0].split():
                    
                    # Limita nei test a poche mailbox:
                    # Commentare nella release finale!
                    #if (int(num)>4):
                    #    break

                    # Estrae il message-id univoco del server:
                    # (la risposta necessita di parsing per ottenere il dato e presentarlo in formato standard)
                    # Non molto utile in realtà e soggetto a errori: non usato, commentare!
                    #typ, messageid = m.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
                    #rfc822_message_id = '<' + messageid[0][1].decode('utf-8').strip().split("<")[1].rstrip(">") + '>'
                    #print(rfc822_message_id)
                    
                    # Estrae il messaggio in formato rcf822 (testo con codifica US-ASCII a 7 bit) e lo salva su un file eml:
                    typ, msg_data = m.fetch(num, '(RFC822)')

                    if (typ=='OK'):
                        # Elimina dal nome della casella i caratteri '/' e '\'
                        mailbox_ok = str(mailbox).replace('/','_').replace('\\','_')
                        # Apre il file eml assegnandogli un nome univoco, concatenando nome account, cartella e id relativo: 
                        f = open('%s/%s_%s_%s.eml' %(local_folder,hostname,mailbox_ok,num.decode('utf-8')), 'wb')
                        f.write(msg_data[0][1])
                        f.close()
                    else:
                        print(typ,num)

                m.close()
            except Exception as e:
                print(e) 
    finally:
        # Effettua il logout:
        m.logout()

if __name__ == '__main__':
    main()