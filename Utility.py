import random
import time
import hashlib
import socket
import threading

class Utility:

    MY_IPV4='192.168.000.009'
    MY_IPV6='FC00:0000:0000:0000:0000:0000:0007:0001'
    PORT=3000
    PATHDIR='/home/simone/Immagini/'

    # Metodo che genera un numero random nel range [1024, 65535]
    @staticmethod
    def generatePort():
        random.seed(time.process_time())
        return random.randrange(1024, 65535)
    # Questo metodo genera un packet id randomico
    # Chiede di quanti numeri deve essere il valore generato
    @staticmethod
    def generateId(lunghezza):
        random.seed(time.process_time())
        seq = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        val = ''
        for i in range(0, lunghezza):
            val = val + random.choice(seq)
        return val

    # Metodo per generare l'md5 di un file, va passato il percorso assoluto
    @staticmethod
    def generateMd5(path):

        #path="/home/flavio/Scrivania/pippo.txt"
        # Inizializzo le variabili che utilizzerò
        f = open(path, 'rb')
        hash = hashlib.md5()

        # Per una lettura più efficiente suddivido il file in blocchi
        buf = f.read(4096)
        while len(buf) > 0:
            hash.update(buf)
            buf = f.read(4096)

        # Return del digest
        return hash.hexdigest()

        # Ritorna i due ip data la stringa generale
        # Ritorna prima ipv4 e poi ipv6

    @staticmethod
    def getIp(stringa):
        t = stringa.find('|')
        if t != -1:

            ''' Modifico così questa funzione poichè se usiamo una connect di un indirizzo come 127.000.000.001
                purtroppo da errore, così trasformo l'ip sopra in 127.0.0.1'''
            ipv4 = ''
            tmp = stringa[0:t].split('.')
            for grp in tmp:
                if len(grp.lstrip('0')) == 0:
                    ipv4 += '0.'
                else:
                    ipv4 += grp.lstrip('0') + '.'
            ipv4 = ipv4[0:-1]
            #Da vedere se funziona
            ipv6 = stringa[t + 1:]
            return ipv4, ipv6
        else:
            return '', ''

class Sender:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, ip, port):
        # definizione thread del client
        threading.Thread.__init__(self)
        self.messaggio = messaggio
        self.ip = ip
        self.port = port

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
       # try:
            self.sendMessage(self.messaggio, self.ip, self.port)
        #except Exception as e:
           # print("errore: ", e)

    def sendMessage(self, messaggio, ip, porta):
        r = 0  # random.randrange(0, 100)
        ipv4, ipv6 = Utility.getIp(ip)
        if r < 50:
            a = ipv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            a = ipv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        sock.connect((a, int(porta)))
        print('inviato: '+messaggio)
        sock.sendall(messaggio.encode())
        sock.close()

class SenderAll:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, messaggio, listaNear):
        # definizione thread del client
        threading.Thread.__init__(self)
        self.messaggio = messaggio
        self.listaNear = listaNear

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
        #try:
            self.sendAllNear()
        #except Exception as e:
           # print("errore: ", e)

    def sendAllNear(self):
        for i in range(0, len(self.listaNear)):
            self.sendMessage(self.messaggio, self.listaNear[i][0], self.listaNear[i][1])

    def sendMessage(self, messaggio, ip, porta):
        r = 0  # random.randrange(0, 100)
        ipv4, ipv6 = Utility.getIp(ip)
        if r < 50:
            a = ipv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            a = ipv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        sock.connect((a, int(porta)))
        print('inviato: '+messaggio)
        sock.sendall(messaggio.encode())
        sock.close()

class Downloader:
    # Costruttore che inizializza gli attributi del Worker
    def __init__(self, ipp2p, pp2p, md5, name):
        # definizione thread del client
        threading.Thread.__init__(self)
        self.ipp2p = ipp2p
        self.pp2p = pp2p
        self.md5 = md5
        self.name = name

    # Funzione che lancia il worker e controlla la chiusura improvvisa
    def run(self):
        #try:
            self.download(self.ipp2p, self.pp2p, self.md5, self.name)
        #except Exception as e:
            #print("errore: ", e)

    def download(self, ipp2p, pp2p, md5, name):
        r = 0  # random.randrange(0,100)
        ipv4, ipv6 = Utility.getIp(ipp2p)
        if r < 50:
            ind = ipv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            ind = ipv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        print(name)
        sock.connect((ind, int(pp2p)))
        sock.sendall(('RETR' + md5).encode())

        # ricevo i primi 10 Byte che sono "ARET" + n_chunk
        recv_mess = sock.recv(10).decode()
        if recv_mess[:4] == "ARET":
            num_chunk = int(recv_mess[4:])
            count_chunk = 0

            # apro il file per la scrittura
            f = open(Utility.PATHDIR+name.rstrip(' '), "wb")  # Apro il file rimuovendo gli spazi finali dal nome
            buffer = bytes()

            # Finchè i chunk non sono completi
            while count_chunk < num_chunk:
                tmp = sock.recv(5).decode(errors='ignore')
                #if tmp.isnumeric() and len(tmp) == 5:
                print(tmp)
                chunklen = int(tmp) #leggo la lunghezza del chunk
                buffer = sock.recv(chunklen)  # Leggo il contenuto del chunk
                f.write(buffer)  # Scrivo il contenuto del chunk nel file
                count_chunk += 1  # Aggiorno il contatore
            f.close()