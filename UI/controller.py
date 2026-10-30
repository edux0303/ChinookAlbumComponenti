import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------- PUNTO 1 ----------

    def fillDDGeneri(self):
        for idG, nome in self._model.getGeneri():
            self._view._ddGenere.options.append(ft.dropdown.Option(key=str(idG), text=nome))

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        # 1. leggo il genere
        if self._view._ddGenere.value is None:
            self._view._txt_result.controls.append(ft.Text("Seleziona un genere!", color="red"))
            self._view.update_page()
            return
        idGenere = int(self._view._ddGenere.value)

        # 2. leggo la soglia S
        try:
            soglia = int(self._view._txtInS.value)
        except (ValueError, TypeError):
            self._view._txt_result.controls.append(ft.Text("S deve essere un numero intero!", color="red"))
            self._view.update_page()
            return
        if soglia < 1:
            self._view._txt_result.controls.append(ft.Text("S deve essere almeno 1!", color="red"))
            self._view.update_page()
            return

        # 3. costruisco il grafo
        self._model.buildGraph(idGenere, soglia)

        if self._model.getNumNodi() == 0:
            self._view._txt_result.controls.append(ft.Text("Nessun album trovato per questo genere."))
            self._view.update_page()
            return

        # 4. stampo nodi e archi
        self._view._txt_result.controls.append(ft.Text("Grafo creato correttamente!", color="green"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodi()}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumArchi()}"))

        # 5. riempio il dropdown degli album
        self.fillDDAlbum()

        self._view.update_page()

    def fillDDAlbum(self):
        self._view._ddAlbum.options.clear()
        self._view._ddAlbum.value = None
        for a in self._model.getNodiOrdinati():
            self._view._ddAlbum.options.append(ft.dropdown.Option(key=str(a.id), text=a.title))

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._view._txt_result.controls.append(ft.Text("Crea prima il grafo!", color="red"))
            self._view.update_page()
            return

        # a) album con più brani
        album, n = self._model.getPiuBrani()
        self._view._txt_result.controls.append(ft.Text(f"a) Album con più brani: {album} ({n} brani)"))

        # b) album più lungo
        album, durata = self._model.getPiuDurata()
        self._view._txt_result.controls.append(ft.Text(f"b) Album più lungo: {album} ({durata:.2f} minuti)"))

        # c) album con più clienti
        lista, n = self._model.getPiuClienti()
        self._view._txt_result.controls.append(ft.Text(f"c) Album con più clienti ({n}):"))
        for a in lista:
            self._view._txt_result.controls.append(ft.Text(f"     {a}"))

        # d) album con grado maggiore
        lista, grado = self._model.getGradoMaggiore()
        self._view._txt_result.controls.append(ft.Text(f"d) Album con grado maggiore ({grado}):"))
        for a in lista:
            self._view._txt_result.controls.append(ft.Text(f"     {a}"))

        # e) 5 archi di peso maggiore
        self._view._txt_result.controls.append(ft.Text("e) I 5 archi di peso maggiore:"))
        for t1, t2, p in self._model.getTop5Archi():
            self._view._txt_result.controls.append(ft.Text(f"     {t1} – {t2}: {p}"))

        # f) componenti connesse
        nComp, dimMax, isolati = self._model.getInfoComponenti()
        self._view._txt_result.controls.append(ft.Text(f"f) Componenti connesse: {nComp}"))
        self._view._txt_result.controls.append(ft.Text(f"     Dimensione della più grande: {dimMax}"))
        self._view._txt_result.controls.append(ft.Text(f"     Album isolati: {isolati}"))

        # g) top 5 della componente più grande
        self._view._txt_result.controls.append(ft.Text("g) Top 5 album della componente più grande:"))
        for a, grado in self._model.getTop5Componente():
            self._view._txt_result.controls.append(ft.Text(f"     {a}: grado {grado}"))

        self._view.update_page()

    # ---------- PUNTO 2 ----------

    def handleRaccolta(self, e):
        self._view._txt_result.controls.clear()

        # 1. grafo creato?
        if self._model.getNumNodi() == 0:
            self._view._txt_result.controls.append(ft.Text("Crea prima il grafo!", color="red"))
            self._view.update_page()
            return

        # 2. album di partenza
        if self._view._ddAlbum.value is None:
            self._view._txt_result.controls.append(ft.Text("Seleziona un album di partenza!", color="red"))
            self._view.update_page()
            return
        partenza = self._model.getAlbum(int(self._view._ddAlbum.value))
        if partenza is None:
            self._view._txt_result.controls.append(ft.Text("Album non presente nel grafo!", color="red"))
            self._view.update_page()
            return

        # 3. leggo K
        try:
            k = int(self._view._txtInK.value)
        except (ValueError, TypeError):
            self._view._txt_result.controls.append(ft.Text("K deve essere un numero intero!", color="red"))
            self._view.update_page()
            return

        nComp = self._model.getNumComponenti()
        if k < 2 or k > nComp:
            self._view._txt_result.controls.append(
                ft.Text(f"K deve essere compreso tra 2 e {nComp} (numero di componenti)!", color="red"))
            self._view.update_page()
            return

        # 4. ricorsione
        sol, durata, brani = self._model.getGruppo(partenza, k)

        if len(sol) == 0:
            self._view._txt_result.controls.append(ft.Text("Nessuna raccolta trovata."))
            self._view.update_page()
            return

        # 5. stampo
        self._view._txt_result.controls.append(
            ft.Text(f"Raccolta di {k} album a partire da {partenza}:", color="green"))
        for a in sorted(sol, key=lambda x: x.title):
            self._view._txt_result.controls.append(
                ft.Text(f"     {a} – {a.durataTotale :.2f} min – {a.numeroBrani} brani"))
        self._view._txt_result.controls.append(ft.Text(f"Differenza di durata: {durata :.2f} minuti"))
        self._view._txt_result.controls.append(ft.Text(f"Totale brani: {brani}"))

        self._view.update_page()