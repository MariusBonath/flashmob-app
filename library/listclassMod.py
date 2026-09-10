# =============================================================================
# library/listclassMod.py – Kerndaten-Modul (Listclass)
# =============================================================================
#
# Dieses Modul enthält die Klasse "Listclass" – das Herzstück der App.
# Sie verwaltet die Bücherliste im Arbeitsspeicher und stellt alle
# Operationen bereit: Laden, Speichern, Sortieren, Filtern, CSV-Import/Export.
#
# Besonderheiten gegenüber dem Book Manager (CLI-Version):
#   - @property / @setter für is_modified (Änderungsstatus)
#   - @timestamp_decorator (automatischer Zeitstempel)
#   - sort_by_title()          → Lambda-Transfer aus der Klausur
#   - filter_by_title_letter() → filter() + Lambda, ebenfalls aus Klausur
#
# Interne Datenstruktur (2D-Liste):
#   self._list = [
#       ["001", "Dracula",           "007", "Bram Stocker",    "222",  "1897"],
#       ["002", "Pippi Langstrumpf", "005", "Astrid Lindgren", "100",  "1949"],
#   ]
#   Jede innere Liste = ein Buch (Datensatz)
#   Index:               0        1               2              3        4      5
#                       Nr.    Titel          Genre           Autor   Preis  Jahr
#
# Konzepte in dieser Datei:
#   - Klassen, Konstruktor, Instanzvariablen
#   - @property und @setter     (kontrollierter Zugriff auf Attribute)
#   - Decorator-Funktion        (@timestamp_decorator)
#   - pickle                    (binäres Speichern von Python-Objekten)
#   - csv-Modul                 (CSV lesen und schreiben)
#   - datetime                  (aktuelles Datum und Uhrzeit)
#   - Lambda-Ausdruck           (anonyme Funktion für Sortierung)
#   - filter()                  (Liste nach Bedingung filtern)
#   - sorted()                  (sortierte Kopie einer Liste)
#   - enumerate()               (Index + Wert gleichzeitig)
#   - list.pop(), list.insert() (Elemente entfernen / einfügen)
# =============================================================================

import csv
import datetime
import pickle

from library import ioMod as io


# =============================================================================
# Decorator: timestamp_decorator
# =============================================================================
#
# Ein Decorator ist eine Funktion, die eine andere Funktion "verpackt"
# und ihr zusätzliches Verhalten gibt – ohne den Originalcode zu ändern.
#
# Syntax: @timestamp_decorator  über der zu dekorierenden Funktion
#
# Was dieser Decorator tut:
#   Ruft die originale Funktion auf, nimmt ihr Ergebnis (eine Liste),
#   hängt den aktuellen Zeitstempel an und gibt die ergänzte Liste zurück.
#
# Ablauf:
#   edit_list() → gibt sublist zurück
#   Decorator   → hängt "2026-02-27 09:15:00" an sublist an
#   Aufrufer    → erhält sublist + Zeitstempel
#
# Schreibweise:
#   def timestamp_decorator(func):   ← nimmt eine Funktion als Parameter
#       def wrapper(*args, **kwargs): ← neue Funktion, die func umhüllt
#           result = func(*args)      ← originale Funktion aufrufen
#           ts = ...                  ← Zeitstempel erzeugen
#           result.append(ts)         ← an Ergebnis anhängen
#           return result             ← erweitertes Ergebnis zurückgeben
#       return wrapper                ← wrapper als neue Funktion zurückgeben

def timestamp_decorator(func):
    """
    Decorator: Hängt nach dem Aufruf der dekorierten Funktion
    automatisch den aktuellen Zeitstempel an das Ergebnis (Liste) an.
    """
    def wrapper(*args, **kwargs):
        # *args    → beliebig viele Positionsargumente (z. B. self, prompts, ...)
        # **kwargs → beliebig viele Schlüsselwort-Argumente
        ergebnis = func(*args, **kwargs)

        # datetime.datetime.now() → aktuelles Datum und Uhrzeit
        # .strftime(...)          → in einen lesbaren String umwandeln
        zeitstempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ergebnis.append(zeitstempel)
        return ergebnis

    return wrapper


# =============================================================================
# Klasse: Listclass
# =============================================================================

class Listclass:
    """
    Verwaltet die Bücherliste und alle Operationen darauf.

    Instanzvariablen:
        self.fpath        → Pfad zur Pickle-Speicherdatei
        self._list        → die eigentliche Bücherliste (2D-Liste)
        self._is_modified → True, wenn ungespeicherte Änderungen vorliegen
    """

    # =========================================================================
    # Konstruktor
    # =========================================================================

    def __init__(self, fpath: str, _list: list = None) -> None:
        """
        Erstellt ein Listclass-Objekt und lädt vorhandene Daten.

        Der optionale Parameter _list erlaubt, eine vorhandene Liste
        direkt zu übergeben (z. B. für Tests) – statt aus der Datei zu laden.

        Args:
            fpath: Pfad zur Pickle-Datei.
            _list: Optionale Startliste. Wenn None → aus Datei laden.
        """
        self.fpath = fpath
        self.is_modified = False   # noch keine Änderungen

        if _list is not None:
            # Liste wurde direkt übergeben → übernehmen
            self._list = _list
        else:
            # Aus Datei laden
            self._list = self.load_list()


    # =========================================================================
    # Property: is_modified
    # =========================================================================
    #
    # @property macht ein Attribut zu einer "verwalteten Eigenschaft".
    # Statt self.is_modified = True direkt zu setzen, läuft der Zugriff
    # durch Getter und Setter – wie in Java mit get/set-Methoden.
    #
    # Warum?
    #   Später könnte man hier z. B. automatisch einen Speichern-Dialog
    #   auslösen, wenn is_modified auf True gesetzt wird.
    #
    # Lesen:   wert = self.is_modified      → ruft @property auf
    # Setzen:  self.is_modified = True      → ruft @is_modified.setter auf

    @property
    def is_modified(self) -> bool:
        """Gibt zurück, ob es ungespeicherte Änderungen gibt."""
        return self._is_modified

    @is_modified.setter
    def is_modified(self, neuer_wert: bool) -> None:
        """Setzt den Änderungsstatus."""
        self._is_modified = neuer_wert


    # =========================================================================
    # Laden
    # =========================================================================

    def load_list(self) -> list:
        """
        Lädt die Bücherliste aus der Pickle-Datei.

        Pickle speichert Python-Objekte als Binärdaten auf der Festplatte.
        pickle.load() stellt das Objekt exakt wieder her.

        SICHERHEITSHINWEIS:
            pickle.load() führt beim Einlesen beliebigen Python-Code aus,
            der in der Datei steckt. Eine .dat-Datei aus einer fremden Quelle
            darf deshalb NIE geladen werden. In diesem Projekt schreibt und
            liest nur das Programm selbst die Datei – für ein echtes Produkt
            wäre ein Textformat wie JSON die sicherere Wahl.

        Fehlerfälle (Datei fehlt, ist leer oder beschädigt) werden abgefangen,
        damit die App auch dann startet.

        Returns:
            Die geladene Liste, oder [] wenn keine gültigen Daten vorliegen.
        """
        datei = io.fopen(self.fpath, "rb")   # "rb" = read binary
        if datei is None:
            return []

        try:
            with datei:
                daten = pickle.load(datei)
        except (pickle.UnpicklingError, EOFError, ValueError, TypeError) as e:
            print(f"Warnung: '{self.fpath}' konnte nicht gelesen werden ({e}). "
                  f"Starte mit leerer Liste.")
            return []

        # Sicherstellen, dass wirklich eine Liste zurückkommt
        return daten if isinstance(daten, list) else []


    # =========================================================================
    # Speichern
    # =========================================================================

    def save_list(self) -> None:
        """
        Speichert die gesamte Bücherliste als Pickle-Datei.

        pickle.dump() serialisiert self._list in Binärdaten.
        Beim nächsten Programmstart kann load_list() die Daten
        exakt wiederherstellen.
        """
        datei = io.fopen(self.fpath, "wb")   # "wb" = write binary
        if datei is None:
            raise OSError(f"Datei '{self.fpath}' konnte nicht zum Speichern geöffnet werden.")
        # "with" schließt die Datei automatisch – auch wenn beim Schreiben
        # ein Fehler auftritt.
        with datei:
            pickle.dump(self._list, datei)
        self.is_modified = False   # Änderungen sind jetzt gesichert


    # =========================================================================
    # Bearbeiten – mit automatischem Zeitstempel (@timestamp_decorator)
    # =========================================================================

    @timestamp_decorator
    def edit_list(self, sublist: list) -> list:
        """
        Nimmt einen bearbeiteten Datensatz entgegen und gibt ihn als neue
        Liste zurück. Der @timestamp_decorator hängt an das Ergebnis
        automatisch den aktuellen Zeitstempel als letztes Feld an.

        Verwendung in der GUI (menuActions.py, Aktion "Edit"):
            self.lco._list[index] = self.lco.edit_list(neue_werte)
            → self._list[index] enthält danach:
              [Nr., Titel, Genre, Autor, Preis, Jahr, "2026-09-10 14:03:11"]

        Args:
            sublist: Der bearbeitete Datensatz (Werte pro Spalte).

        Returns:
            Eine neue Liste mit den Werten – der Zeitstempel kommt vom Decorator.
        """
        # list(...) erzeugt eine Kopie, damit der Decorator nicht versehentlich
        # in die übergebene Liste des Aufrufers schreibt.
        return list(sublist)


    # =========================================================================
    # Sortieren – allgemein
    # =========================================================================

    def sort_list(self, col: int) -> list:
        """
        Sortiert die Liste nach einer beliebigen Spalte und gibt
        eine neue sortierte Kopie zurück. Die Original-Liste bleibt unverändert.

        Wie sorted() mit Lambda funktioniert:
            sorted(liste, key=lambda zeile: zeile[col])
            → lambda ist eine anonyme Funktion:
              nimmt eine Zeile und gibt das Feld an Position col zurück.
            → sorted() verwendet diesen Wert als Sortierkriterium.

        Args:
            col: Spaltenindex (0 = Nr., 1 = Titel, 2 = Genre, …)

        Returns:
            Die sortierte Liste als neue Liste.
        """
        return sorted(self._list, key=lambda zeile: zeile[col])


    # =========================================================================
    # Sortieren nach Titel – Lambda-Transfer aus der Klausur
    # =========================================================================
    #
    # HINTERGRUND:
    #   In der Klausur (Py1) wurde Lambda so verwendet:
    #       IDX_NAME = 1
    #       sorted(mylst_2d, key=lambda row: row[IDX_NAME])
    #
    #   Die Bücherliste hat dieselbe Struktur:
    #       self._list = [ [Nr., Titel, Genre, Autor, Preis, Jahr], ...]
    #                        0     1      2      3      4      5
    #   → Titel steht an Index 1, genau wie "Name" in der Klausur.
    #
    #   Das Lambda ist deshalb strukturell identisch:
    #       Klausur:   lambda row: row[1]   (row[1] = Name)
    #       FlashMob:  lambda row: row[1]   (row[1] = Titel)

    def sort_by_title(self) -> list:
        """
        Gibt die Bücherliste alphabetisch nach Titel (A → Z) sortiert zurück.
        Verändert self._list NICHT – gibt eine neue sortierte Kopie zurück.

        Lambda-Erklärung:
            key=lambda zeile: zeile[1]
                 ↑             ↑
            anonyme Funktion   Titel-Feld (Index 1)

        Returns:
            Neue, alphabetisch nach Titel sortierte Liste.
        """
        #      ↓↓↓  LAMBDA – direkt aus der Klausur übertragen  ↓↓↓
        return sorted(self._list, key=lambda zeile: zeile[1])


    # =========================================================================
    # Filtern nach Anfangsbuchstabe – filter() + Lambda
    # =========================================================================
    #
    # HINTERGRUND:
    #   In der Klausur (Teil 2c) wurde filter() so verwendet:
    #       filter(lambda row: row[2] < 50, mylst_2d)
    #
    #   Hier wird filter() analog eingesetzt, aber mit einer anderen Bedingung:
    #       filter(lambda zeile: zeile[1][0].upper() == buchstabe, self._list)
    #                                  ↑   ↑
    #                              Titel  erster Buchstabe des Titels
    #
    # Schritt für Schritt:
    #   zeile[1]        → Titel-String, z. B. "Dracula"
    #   zeile[1][0]     → erster Buchstabe, z. B. "D"
    #   .upper()        → in Großbuchstaben, damit Groß/Klein egal ist
    #   == buchstabe    → Vergleich mit dem gesuchten Buchstaben (z. B. "D")

    def filter_by_title_letter(self, buchstabe: str) -> list:
        """
        Filtert die Bücherliste nach dem Anfangsbuchstaben des Titels.
        Gibt eine neue (gefilterte + alphabetisch sortierte) Liste zurück.

        Bei buchstabe="" → keine Filterung, alle Bücher alphabetisch sortiert.

        Args:
            buchstabe: Gesuchter Anfangsbuchstabe (Großbuchstabe), z. B. "D".
                       Leer-String "" → alle Bücher anzeigen.

        Returns:
            Neue gefilterte und sortierte Liste.
        """
        if buchstabe == "":
            # Kein Filter → alle Bücher, aber alphabetisch
            return sorted(self._list, key=lambda zeile: zeile[1])

        #      ↓↓↓  FILTER + LAMBDA  ↓↓↓
        #  filter() gibt einen Iterator zurück → list() wandelt ihn in eine Liste um
        gefiltert = list(
            filter(
                lambda zeile: zeile[1][0].upper() == buchstabe,
                self._list
            )
        )

        # Gefilterte Treffer noch alphabetisch sortieren
        return sorted(gefiltert, key=lambda zeile: zeile[1])


    # =========================================================================
    # CSV-Export
    # =========================================================================

    def export2csv(self, fpath_csv: str, kopfzeile: list) -> None:
        """
        Exportiert alle Bücher in eine CSV-Datei.

        csv.writer übernimmt das korrekte Escaping (z. B. bei Feldern
        mit Kommas oder Anführungszeichen).

        Args:
            fpath_csv: Pfad zur Zieldatei.
            kopfzeile: Spaltenüberschriften für die erste Zeile.
        """
        # newline="" ist beim csv-Modul Pflicht – sonst entstehen unter Windows
        # leere Zeilen zwischen den Datensätzen.
        datei = io.fopen(fpath_csv, "w", newline="")
        if datei is None:
            raise OSError(f"CSV-Datei '{fpath_csv}' konnte nicht geöffnet werden.")

        with datei:
            writer = csv.writer(datei)
            writer.writerow(kopfzeile)       # erste Zeile: Spaltenüberschriften
            writer.writerows(self._list)     # alle Datensätze auf einmal


    # =========================================================================
    # CSV-Import
    # =========================================================================

    def import_csv(self, fpath: str) -> None:
        """
        Importiert Bücher aus einer CSV-Datei.
        Ersetzt die aktuelle Liste vollständig – aber erst, wenn die Datei
        vollständig und fehlerfrei eingelesen wurde. Schlägt der Import fehl,
        bleiben die bisherigen Daten erhalten.

        Ablauf:
            1. Datei öffnen und mit csv.reader komplett einlesen
            2. Erste Zeile = Kopfzeile → bestimmt die erwartete Spaltenzahl
            3. Restliche Zeilen prüfen (richtige Spaltenzahl?) und übernehmen

        Warum csv.reader(datei) statt Zeile-für-Zeile?
            csv.reader kümmert sich selbst um Sonderfälle wie Kommas oder
            Zeilenumbrüche innerhalb von Anführungszeichen.

        Args:
            fpath: Pfad zur CSV-Quelldatei.

        Raises:
            OSError:    Datei kann nicht geöffnet werden.
            ValueError: Datei ist leer oder eine Zeile hat die falsche Spaltenzahl.
        """
        datei = io.fopen(fpath, "rt", newline="")
        if datei is None:
            raise OSError(f"CSV-Datei '{fpath}' konnte nicht geöffnet werden.")

        with datei:
            alle_zeilen = list(csv.reader(datei))

        if not alle_zeilen:
            raise ValueError("Die CSV-Datei ist leer.")

        kopfzeile = alle_zeilen[0]
        spaltenzahl = len(kopfzeile)

        neue_liste = []
        # enumerate(..., start=2): Zeile 1 ist die Kopfzeile, Daten ab Zeile 2
        for zeilennr, zeile in enumerate(alle_zeilen[1:], start=2):
            if not zeile:
                continue   # komplett leere Zeile überspringen
            if len(zeile) != spaltenzahl:
                raise ValueError(
                    f"Zeile {zeilennr}: {len(zeile)} Spalten statt {spaltenzahl}.")
            neue_liste.append(zeile)

        # Erst jetzt – nach erfolgreicher Prüfung – die alte Liste ersetzen
        self._list = neue_liste


    # =========================================================================
    # Hilfsmethoden
    # =========================================================================

    def check_number(self, nummer: str) -> int:
        """
        Sucht einen Datensatz anhand seiner Nummer (erstes Feld).

        enumerate() gibt Index und Wert gleichzeitig:
            for i, zeile in enumerate(self._list):
                i    → aktueller Index (0, 1, 2, …)
                zeile → innere Liste (ein Datensatz)

        Args:
            nummer: Die gesuchte Nummer, z. B. "003".

        Returns:
            Index des gefundenen Datensatzes, oder -1 wenn nicht gefunden.
        """
        for i, zeile in enumerate(self._list):
            if zeile[0] == nummer:
                return i
        return -1


    def delete_sublist(self, index: int) -> list:
        """
        Entfernt den Datensatz an Position index und gibt ihn zurück.

        list.pop(index) entfernt das Element und gibt es zurück – in einem Schritt.

        Args:
            index: Position in der internen Liste (0-basiert).

        Returns:
            Der entfernte Datensatz.
        """
        return self._list.pop(index)


    def next_free(self) -> tuple[int, str]:
        """
        Bestimmt Position UND Nummer für einen neuen Datensatz.

        Regeln:
            - Ist die Nummernfolge aufsteigend sortiert und hat eine Lücke
              (z. B. 001, 002, 004), wird die Lücke gefüllt:
              Rückgabe (2, "003") → an Index 2 einfügen, Nummer 003.
            - Sonst wird am Ende angehängt mit (höchste Nummer + 1):
              Rückgabe (len(liste), "006").
            - Bei leerer Liste: (0, "001").

        Nicht-numerische Nummern (z. B. aus einer fremden CSV) werden
        übersprungen und lösen keinen Absturz aus.

        Returns:
            Ein Tupel (einfuege_index, neue_nummer_als_string).
        """
        nummern: list[int | None] = []
        for zeile in self._list:
            try:
                nummern.append(int(zeile[0]))
            except (ValueError, IndexError):
                nummern.append(None)   # Platzhalter für ungültige Nummer

        gueltige = [n for n in nummern if n is not None]
        naechste_nummer = (max(gueltige) + 1) if gueltige else 1

        # Lücke nur füllen, wenn ALLE Nummern gültig und aufsteigend sortiert sind
        if None not in nummern and nummern == sorted(nummern):
            for i in range(1, len(nummern)):
                if nummern[i] - nummern[i - 1] > 1:
                    return i, f"{nummern[i - 1] + 1:03}"

        return len(self._list), f"{naechste_nummer:03}"


    def insert_sublist(self, index: int, sublist: list) -> None:
        """
        Fügt einen neuen Datensatz an der angegebenen Position ein.

        list.insert(index, element) verschiebt alle Elemente ab index
        um eine Position nach rechts.

        Args:
            index:   Einfügeposition (0-basiert).
            sublist: Der neue Datensatz als Liste.
        """
        self._list.insert(index, sublist)


if __name__ == "__main__":
    pass
