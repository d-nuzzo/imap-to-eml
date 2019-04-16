
#!/usr/bin/env python
#-*- coding:utf-8 -*-

import getpass, imaplib, os, sys, re, argparse, logging

# Informazioni sul programma:
name = "imap_to_eml.py"
version = "1.1"
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
        return dir_path + '\\emails'
    else:
        return dir_path + '/emails'

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
    parser.add_argument("-t", "--test", action="store_true", help="test only, don't save eml files!")
    parser.add_argument("-a", "--ask", action="store_true", help="ask every mailbox (folder) for confirmation")
    parser.add_argument('-s', dest='hostname', help="IMAP server, like: imap.gmail.com", required=True)
    parser.add_argument('-u', dest='username', help="IMAP username, like: mario.rossi@gmail.com", required=True)
    parser.add_argument('--pwd', dest='password', help="IMAP password", default="")
    parser.add_argument('-p', dest='port', help="IMAP port, default: 993", type=int, default=993)
    parser.add_argument('--log', dest='log_level', help="log level", choices=['debug', 'info', 'warning', 'error'], default="info")
    parser.add_argument('-d', dest='destination', help="local folder where to save .eml files, default: ./emails", default=default_destination())
    args = parser.parse_args()

    # Visualizza le informazioni sul programma:
    print_header()

    # Imposta Server Imap, Porta, Nome Utente e Livello di Log:
    hostname = args.hostname
    username = args.username
    port = args.port
    loglevel = args.log_level

    # Inizializza il modulo di log su file:
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(filename='imap_to_eml.log', format='%(levelname)s: %(message)s', level=numeric_level)
    logging.info('STARTING %s versione %s' %(name, version))

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
            logging.error("Exception: {0}".format(e))
            print(e)
            exit(1)

    # Visualizza la configuraione:
    if args.verbose:
        print('Server IMAP: ', hostname)
        print('Porta: ', str(port))
        print('Nome utente: ', username)
        print('Destinazione: ', local_folder)
    
    logging.info('Server IMAP: %s'%(hostname))
    logging.info('Porta: %d'%(port))
    logging.info('Nome utente: %s'%(username))
    logging.info('Destinazione: %s'%(local_folder))

    # Effettua il login, se si verifica un errore esce dal programma:
    m = imaplib.IMAP4_SSL(hostname,port=port)
    try:
         m.login(username, password)
         logging.info('LOGIN OK')
    except:
        msg = 'Errore durante il login!'
        logging.error(msg)
        print(msg)
        exit(1)
   
    try:
        if args.verbose:
            print('Capacità:', m.capabilities)
        logging.debug('Capacità: %s'%(''.join(m.capabilities)))

        # Estrae la lista delle mailboxes (cartelle di posta sul Server):
        status, data = m.list()

        if args.verbose:
            print('Stato: ', repr(status))
            print('Elenco mailboxes:')
        logging.debug('Stato: %s' %(repr(status)))

        for line in data:
            
            # Estrae i dati della casella eseguendo il parsing della linea relativa alla mailbox:
            flags, delimiter, mailbox = split_line_response(line)
            logging.debug('Flags: %s' %(flags))
            logging.debug('Delimiter: %s' %(delimiter))
            logging.debug('Mailbox: %s' %(mailbox))

            # Visualizza le informazioni:
            # Numero totale messaggi, Numero nuovi messaggi, UID prossimo messaggio (i server qui spesso restituiscono 
            # erroneamente un contatore non univoco), ultimo UID valido, numero messaggi non letti)
            if args.verbose:
                print(flags, m.status(mailbox, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)'))
            logging.info('Status: %s' %(m.status(mailbox, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')[1][0].decode('utf-8')))

            if args.ask:
                res = input('Download emails for mailbox %s ? (Y/n): ' %(mailbox))
                if not res.upper()=='Y':
                    logging.warning('SKIPPING MAILBOX %s'%(mailbox))
                    continue

            try:

                # Seleziona la mailbox in sola lettura:
                m.select(mailbox, readonly=True)
                # Effettua una ricerca di tutti i messaggi:
                typ, msg_ids = m.search(None, 'ALL')
                
                # Visualizza gli ID (non univoci) delle mail trovate:
                if args.verbose:
                    print(mailbox, typ, msg_ids)
                
                # Elabora in un ciclo i singoli messaggi (ognuno con il proprio id):
                for num in msg_ids[0].split():
                    
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
                        # Assegna al file eml un nome univoco: <account>_<mailbox>_<id>.eml  
                        eml_filename = '%s/%s_%s_%s.eml' %(local_folder,hostname,mailbox_ok,num.decode('utf-8')) 
                        if not args.test:
                            f = open(eml_filename, 'wb')
                            f.write(msg_data[0][1])
                            f.close()
                        logging.info('FILE SAVED: %s' %(eml_filename))    
                    else:
                        print(typ,num)

                m.close()
            except Exception as e:
                logging.error("Exception: {0}".format(e))
                print(e) 
    finally:
        m.logout()

    logging.info('FINISHED')    

if __name__ == '__main__':
    main()