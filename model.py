from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        risultati = []

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()  #richiamo il metodo dell'oggetto distributore
            prezzi_mese = []

            #seleziono i prezzi di un dato mese e li metto in una lista
            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro)

            if len(prezzi_mese) == 0:
                media_prezzi = None
            else:
                media_prezzi = sum(prezzi_mese) / len(prezzi_mese)
                # RICORDA: media va calcolata fuori il ciclo for, altrimenti la calcola per ogni nuovo pezzo

            risultati.append((distributore.nome, media_prezzi))

        return risultati

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO

        # RICORSIONE: provare tutte le possibili scelte di distr. per il giorno corrente
        # Aggiorno la soluzione solo se ho trovato un costo inferiore o è -1 (vedi sopra)
        if giorno == 8:  # se arriviamo al giorno 8, abbiamo effettuato tutte e 7 le scelte
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:

                # salvo il nuovo costo migliore e sequnza di distr. che ha prodotto quel costo
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()  # creo COPIA perchè modificheremo aggiungendo e togliendo distributori
            return # ricorda perchè appena finiti i 7 giorni, salva la soluzione

        for id_distributore in prezzi_settimana:
            prezzo = prezzi_settimana[id_distributore][giorno - 1]

            if prezzo is None:
                continue   # salto la scelta di un giorno senza prezzo!!!

            costo_rifornimento = 100 * prezzo

            # ricorda il primo giorno non esiste un distributore precedente (ultimo_distributore sarà None).
            if ultimo_distributore is not None and id_distributore != ultimo_distributore:
                costo_rifornimento += 5

            nuovo_costo = costo_corrente + costo_rifornimento
            sequenza_parziale.append(id_distributore)  # aggiungo alla sequenza il distributore scelto oggi

            # passo al giorno successivo ricordandomi la scelta ed il costo
            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                nuovo_costo,
                prezzi_settimana
            )

            sequenza_parziale.pop() # canceòòp scelta, altrimenti lista manterrà scelte dei percorsi precedenti

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        prezzi_settimana = {} #DIZIONARIO

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()  # ricorda prima di scorrere i pezzi recupero quelli del distributore corrente
            prezzi_settimana[distributore.id] = [None] * 7   # moltiplico per 7 nell'eventualità che un prezzo non sia segnato

            for prezzo in prezzi:
                if prezzo.data.month == mese and prezzo.data.day <= 7:
                    prezzi_settimana[distributore.id][prezzo.data.day - 1] = prezzo.prezzo_litro
                    # sottraggo 1 perchè i giorni partono da 1 ma gli indici delle liste da 0

        return prezzi_settimana