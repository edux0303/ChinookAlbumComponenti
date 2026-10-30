from database.DB_connect import DBConnect
from model.album import Album


"""
PUNTO 1
1. All’avvio, riempire un menu a tendina con tutti i generi (tabella Genre).
2. L’utente sceglie un genere G e inserisce in un campo di testo un intero S ≥ 1, la soglia minima di clienti in comune. Premendo “Crea Grafo”, l’applicazione costruisce un grafo semplice, non orientato e pesato: a) i nodi sono gli album che contengono almeno un brano del genere G acquistato da qualche cliente. Per ogni album si memorizzino:
    * il numero di brani del genere G dell’album (tutti, anche quelli mai acquistati);
    * la durata totale di quei brani, in minuti;
    * l’insieme dei clienti che hanno acquistato almeno un brano del genere G dell’album; b) due album sono collegati da un arco se hanno almeno S clienti in comune; c) il peso dell’arco è il numero di clienti in comune.
3. Stampare il numero di nodi e di archi. Riempire poi un menu a tendina con gli album del grafo, in ordine alfabetico.
4. Premendo “Stampa Info”, stampare: a) l’album con più brani e il numero; b) l’album più lungo e la durata in minuti, con due decimali; c) l’album (o gli album, se a pari merito) con più clienti e il numero; d) l’album (o gli album) con grado maggiore e il grado; e) i 5 archi di peso maggiore, in ordine decrescente di peso. A parità si ordina alfabeticamente per il titolo del primo album e poi del secondo; f) il numero di componenti connesse, la dimensione della più grande e il numero di album isolati (componenti con un solo album); g) i 5 album con grado maggiore della componente più grande, in ordine di grado decrescente. A parità di grado si ordina alfabeticamente.
PUNTO 2
Si vuole creare una raccolta “omogenea” di album scollegati tra loro. L’utente sceglie un album di partenza e inserisce un intero K, con 2 ≤ K ≤ numero di componenti connesse. Con un algoritmo ricorsivo, trovare un insieme di esattamente K album che:
1. contiene l’album di partenza;
2. ha ogni album in una componente connessa diversa: due album della raccolta non possono stare nella stessa componente;
3. minimizza la differenza tra la durata dell’album più lungo e quella del più corto;
4. a parità di differenza, ha il numero totale di brani maggiore.
Stampare gli album della raccolta in ordine alfabetico, ciascuno con durata e numero di brani, la differenza di durata in minuti (con due decimali) e il totale dei brani.



"""

class DAO():

    @staticmethod
    def getGeneri():
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT g.GenreId, g.Name
                FROM Genre g
                ORDER BY g.Name
                """

        cursor.execute(query)

        for row in cursor:
            results.append((row["GenreId"], row["Name"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getNodi(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                 SELECT ab.AlbumId as id, ab.Title as name, COUNT(*) AS numero, SUM(t.Milliseconds) AS durata
                 FROM album ab, Track t 
                 WHERE ab.AlbumId = t.AlbumId AND t.GenreId = %s AND ab.AlbumId IN (
                 SELECT t2.AlbumId
                 FROM Track t2, InvoiceLine il
                 WHERE t2.TrackId = il.TrackId AND t2.GenreId = %s
                 )
                 GROUP BY ab.AlbumId, ab.Title
                 ORDER BY ab.AlbumId
                """

        cursor.execute(query,(genere,genere))

        for row in cursor:
            ab = Album(row["id"],row["name"],int(row["numero"]),float(row["durata"])/60000)
            results.append(ab)

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCoppie(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT ab.AlbumId AS idA, i.CustomerId AS idC
                FROM album ab, track t, invoiceline il, invoice i
                WHERE ab.AlbumId = t.AlbumId AND t.TrackId = il.TrackId AND il.InvoiceId= i.InvoiceId AND t.GenreId = %s
                """

        cursor.execute(query,(genere,))

        for row in cursor:
            results.append((row["idA"],row["idC"]))
        cursor.close()
        conn.close()
        return results
