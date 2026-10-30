import networkx as nx
from database.DAO import DAO
from itertools import combinations

class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        self._idMap = {}
        self._partenza = None
    # ==================== PUNTO 1 ====================

    def getGeneri(self):
        return DAO.getGeneri()

    def buildGraph(self, genere,minimo):
        self._grafo.clear()
        self._idMap = {}

        # nodi: album con almeno un brano del genere
        nodi = DAO.getNodi(genere)
        self._idMap = {a.id: a for a in nodi}
        self._grafo.add_nodes_from(nodi)
        for idA, idC in DAO.getCoppie(genere):
            if idA in self._idMap:
                self._idMap[idA].clienti.add(idC)
        for a, b in combinations(nodi, 2):
            comuni = a.clienti & b.clienti
            if len(comuni) >= minimo:
                self._grafo.add_edge(a, b, weight=len(comuni))



    def getNumNodi(self):
        return self._grafo.number_of_nodes()

    def getNumArchi(self):
        return self._grafo.number_of_edges()

    def getNodiOrdinati(self):
        return sorted(self._grafo.nodes, key=lambda a: a.title)

    def getPiuBrani(self):
        best = max(self._grafo.nodes, key= lambda x: x.numeroBrani)
        return best, best.numeroBrani

    def getPiuDurata(self):
        best = max(self._grafo.nodes, key= lambda x: x.durataTotale)
        return best, best.durataTotale

    # c) album con più clienti (anche a pari merito)
    def getPiuClienti(self):
        maxClienti = max(len(a.clienti) for a in self._grafo.nodes)
        migliori = [a for a in self._grafo.nodes if len(a.clienti) == maxClienti]
        migliori.sort(key=lambda a: a.title)
        return migliori, maxClienti

    # d) album con grado maggiore (anche a pari merito)
    def getGradoMaggiore(self):
        maxGrado = max(self._grafo.degree(a) for a in self._grafo.nodes)
        migliori = [a for a in self._grafo.nodes if self._grafo.degree(a) == maxGrado]
        migliori.sort(key=lambda a: a.title)
        return migliori, maxGrado

    # e) 5 archi di peso maggiore
    def getTop5Archi(self):
        archi = []
        for u, v, dati in self._grafo.edges(data=True):
            titoli = sorted([u.title, v.title])  # prima il titolo minore
            archi.append((titoli[0], titoli[1], dati["weight"]))
        archi.sort(key=lambda x: (-x[2], x[0], x[1]))
        return archi[:5]

    # f) componenti connesse
    def getInfoComponenti(self):
        componenti = list(nx.connected_components(self._grafo))
        piuGrande = max(componenti, key=len)
        isolati = 0
        for comp in componenti:
            if len(comp) == 1:
                isolati += 1
        return len(componenti), len(piuGrande), isolati

    # g) top 5 per grado nella componente più grande
    def getTop5Componente(self):
        componenti = list(nx.connected_components(self._grafo))
        piuGrande = max(componenti, key=len)
        album = sorted(piuGrande, key=lambda a: (-self._grafo.degree(a), a.title))
        return [(a, self._grafo.degree(a)) for a in album[:5]]

    def getGruppo(self, partenza, k):
        # 1. a ogni album assegno il numero della sua componente
        self._comp = {}
        for indice, componente in enumerate(nx.connected_components(self._grafo)):
            for nodo in componente:
                self._comp[nodo] = indice

        # 2. candidati ordinati dal più lungo al più corto
        self._candidati = sorted(self._grafo.nodes, key=lambda x: -x.durataTotale)
        self._partenza = partenza

        # 3. soluzione migliore vuota
        self._solBest = []
        self._durata = None
        self._braniBest = -1

        # 4. il primo (il più lungo) va dalla partenza verso gli album più lunghi
        iP = self._candidati.index(partenza)
        for i in range(iP, -1, -1):
            primo = self._candidati[i]
            # se il primo è già troppo più lungo della partenza, mi fermo
            if self._durata is not None and primo.durataTotale - partenza.durataTotale > self._durata:
                break
            # stessa componente della partenza (ma non la partenza) -> salto
            if primo != partenza and self._comp[primo] == self._comp[partenza]:
                continue
            self._ricorsione([primo], i, k)

        return self._solBest, self._durata, self._braniBest

    def _ricorsione(self, parziale, ultimoIndice, k):
        # caso finale: ho K album
        if len(parziale) == k:
            if self._partenza not in parziale:
                return
            differenza = parziale[0].durataTotale - parziale[-1].durataTotale
            brani = sum(a.numeroBrani for a in parziale)
            if (self._durata is None or differenza < self._durata or
                    (differenza == self._durata and brani > self._braniBest)):
                self._solBest = list(parziale)
                self._durata = differenza
                self._braniBest = brani
            return

        # provo ad aggiungere un album più corto dell'ultimo scelto
        for j in range(ultimoIndice + 1, len(self._candidati)):
            candidato = self._candidati[j]

            # potatura: già troppo lontano dal primo -> anche i successivi lo sono
            if self._durata is not None:
                if parziale[0].durataTotale - candidato.durataTotale > self._durata:
                    break

            # componente già usata? salto
            trovato = False
            for p in parziale:
                if self._comp[p] == self._comp[candidato]:
                    trovato = True
            if trovato:
                continue

            parziale.append(candidato)
            self._ricorsione(parziale, j, k)
            parziale.pop()

    def getNumComponenti(self):
        return nx.number_connected_components(self._grafo)

    def getAlbum(self, idA):
        return self._idMap.get(idA)