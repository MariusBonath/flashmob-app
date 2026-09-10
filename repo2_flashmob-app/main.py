# =============================================================================
# main.py – Einstiegspunkt der FlashMobApp
# =============================================================================
#
# Dieses Modul startet die grafische Anwendung.
# Es verbindet alle Teile der App: Konfiguration, Daten, Fenster und Menü.
#
# Architektur der App (3-Schichten-Modell):
#
#   main.py (FlashMobApp)          ← Anwendungsklasse, verbindet alles
#      ├── library/configMod.py    ← liest Konfigurationsdateien
#      ├── library/listclassMod.py ← verwaltet die Bücherdaten (Logik)
#      ├── menuMod.py (MenuModule) ← baut die linke Sidebar (UI-Komponente)
#      └── menuActions.py          ← Aktionen hinter den Menüpunkten (UI-Logik)
#
# Konzepte in dieser Datei:
#   - tkinter                   (Python-Standardbibliothek für GUIs)
#   - Klasse erbt von tk.Tk     (Vererbung / Inheritance)
#   - super().__init__()        (Konstruktor der Elternklasse aufrufen)
#   - Instanzvariablen (self.)
#   - Private Methoden (_build_ui, _wire_actions)
#   - Dictionary (mapping: Menüname → Funktion)
#   - if __name__ == "__main__": (Direktausführungs-Schutz)
# =============================================================================


# -----------------------------------------------------------------------------
# Importe
# -----------------------------------------------------------------------------
# tkinter ist Pythons eingebaute Bibliothek für grafische Benutzeroberflächen.
# "tk" ist der übliche Kurzname.

import tkinter as tk
from tkinter import messagebox

# Aus dem library-Package importieren
from library import configMod as cfg            # Einstellungen laden
from library.listclassMod import Listclass      # Datenklasse

# Aus den Modulen im Hauptordner importieren
from menuMod     import MenuModule              # Sidebar-Widget
from menuActions import MenuActions             # Aktionen hinter den Menüpunkten
from theme       import (FARBE_HINTERGRUND,     # zentrale Farb-Konstanten
                         FARBE_CONTENT_BG, FARBE_TEXT_DUNKEL)


# =============================================================================
# Hauptklasse: FlashMobApp
# =============================================================================

class FlashMobApp(tk.Tk):
    """
    Die Hauptfenster-Klasse der Anwendung.

    Vererbung (Inheritance):
        FlashMobApp erbt von tk.Tk – dem Hauptfenster von tkinter.
        Das bedeutet: FlashMobApp IST ein tkinter-Fenster und bekommt
        automatisch alle Fensterfunktionen (Titel, Größe, Ereignisschleife …).

        Vergleich:
            Statt:  fenster = tk.Tk()  (Fenster als externe Variable)
            Hier:   class FlashMobApp(tk.Tk)  (Fenster = die Klasse selbst)
        → Vorteil: Alle App-Daten (lco, header, …) sind direkt am Fenster.
    """

    def __init__(self) -> None:
        """
        Konstruktor: Wird einmal beim Start aufgerufen.
        Richtet das Fenster ein, lädt Konfiguration und Daten, baut die UI.
        """

        # super().__init__() ruft den Konstruktor von tk.Tk auf.
        # Das initialisiert das tkinter-Fenster – ohne diesen Aufruf
        # würde die App nicht funktionieren.
        super().__init__()

        # ── Fenstereigenschaften ──────────────────────────────────────────────
        self.title("FlashMob – Bücherverwaltung")
        self.geometry("1000x640")       # Startgröße: 1000 × 640 Pixel
        self.minsize(700, 450)              # kleinste erlaubte Fenstergröße
        self.configure(bg=FARBE_TEXT_DUNKEL) # Hintergrundfarbe (dunkles Blau-Schwarz)

        # ── Konfiguration laden ───────────────────────────────────────────────
        # configMod liest FlashMob.ini (Pfade) und books.json (Einstellungen).
        # Die geladenen Werte werden als Instanzvariablen gespeichert,
        # damit sie später in _wire_actions() an MenuActions übergeben werden können.

        pfad_json          = cfg.get_fpath_json()
        self.prompts       = cfg.get_prompts(pfad_json)        # Eingabeaufforderungen
        self.format_specs  = cfg.get_format_specs(pfad_json)   # Validierungsregeln
        self.col_widths    = cfg.get_col_widths(pfad_json)     # Spaltenbreiten
        self.header        = cfg.get_header(pfad_json)         # Spaltenüberschriften
        fpath              = cfg.get_fpath()                   # Pfad zur Pickle-Datei
        self.fpath_csv     = cfg.get_fpath_csv()               # Pfad für CSV-Export

        # ── Datenobjekt anlegen ───────────────────────────────────────────────
        # Listclass lädt beim Erstellen automatisch vorhandene Daten aus der
        # Pickle-Datei. Gibt es noch keine Datei, startet sie mit einer leeren Liste.
        self.lco = Listclass(fpath)

        # ── Benutzeroberfläche aufbauen ───────────────────────────────────────
        self._build_ui()       # Widgets erstellen und anordnen
        self._wire_actions()   # Menüpunkte mit Aktionen verknüpfen

        # Klick auf das "X" des Fensters läuft über dieselbe Abfrage wie
        # der "Beenden"-Knopf (Nachfrage bei ungespeicherten Änderungen).
        self.protocol("WM_DELETE_WINDOW", self._on_quit)


    def _build_ui(self) -> None:
        """
        Erstellt die zwei Hauptbereiche des Fensters:
            - Sidebar (links, feste Breite 200 px)
            - Content-Bereich (rechts, wächst mit dem Fenster)

        Layout-Konzept (pack):
            tk.Frame-Widgets werden mit .pack() angeordnet.
            side=tk.LEFT    → nebeneinander (links nach rechts)
            fill=tk.Y       → Sidebar füllt die gesamte Fensterhöhe
            fill=tk.BOTH    → Content füllt Breite und Höhe
            expand=True     → Content-Bereich darf wachsen wenn Fenster größer wird
        """

        # Linke Sidebar: schmaler, dunkler Bereich mit dem Menü
        self.sidebar_frame = tk.Frame(self, bg=FARBE_HINTERGRUND, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        # pack_propagate(False): Frame behält seine feste Breite (200 px)
        # auch wenn die Inhalte kleiner sind
        self.sidebar_frame.pack_propagate(False)

        # Rechter Content-Bereich: heller Bereich, zeigt den jeweiligen Inhalt
        self.content_frame = tk.Frame(self, bg=FARBE_CONTENT_BG)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Menü-Einträge definieren (Reihenfolge = Anzeigereihenfolge)
        menu_items = ["Edit", "Show", "Save", "Sort",
                      "Export CSV", "Import CSV", "Insert", "Delete"]

        # MenuModule erstellt alle Sidebar-Widgets (Logo, Labels, Quit-Button)
        self.menu_module = MenuModule(self.sidebar_frame, menu_items)


    def _wire_actions(self) -> None:
        """
        Verknüpft jeden Menüpunkt mit der zugehörigen Aktion.

        Ablauf:
            1. MenuActions-Objekt erstellen (kennt alle Aktionsmethoden)
            2. Dictionary (mapping) aufbauen: Menüname → Methode
            3. MenuModule.bind_actions(mapping) aufrufen
               → jedes Label in der Sidebar wird mit seinem Callback verknüpft

        Was ist ein Callback?
            Ein Callback ist eine Funktion, die erst später aufgerufen wird –
            nämlich wenn der Nutzer auf den Menüpunkt klickt.
            Hier: self.actions.action_show ist eine Referenz auf die Methode,
            KEIN sofortiger Aufruf (kein Klammerpaare action_show()).
        """

        # MenuActions bekommt alle nötigen Daten übergeben
        self.actions = MenuActions(
            content_frame = self.content_frame,
            lco           = self.lco,
            header        = self.header,
            col_widths    = self.col_widths,
            prompts       = self.prompts,
            format_specs  = self.format_specs,
            fpath_csv     = self.fpath_csv,
        )

        # Zuordnung: Menüname (String) → Methode (Callback)
        # Die Methoden werden als Referenzen übergeben (ohne Klammern!).
        # tkinter ruft die Methode auf, sobald der Nutzer klickt.
        mapping = {
            "Edit":       self.actions.action_edit,
            "Show":       self.actions.action_show,
            "Save":       self.actions.action_save,
            "Sort":       self.actions.action_sort,
            "Export CSV": self.actions.action_export_csv,
            "Import CSV": self.actions.action_import_csv,
            "Insert":     self.actions.action_insert,
            "Delete":     self.actions.action_delete,
        }

        # Labels mit Callbacks verknüpfen.
        # home_callback: Logo-Klick zeigt die Bücherliste.
        # quit_callback: "Beenden" fragt vorher nach ungespeicherten Änderungen.
        self.menu_module.bind_actions(
            mapping,
            home_callback=self.actions.action_show,
            quit_callback=self._on_quit,
        )


    def _on_quit(self) -> None:
        """
        Beendet die App. Gibt es ungespeicherte Änderungen (lco.is_modified),
        wird zuerst gefragt, ob gespeichert werden soll.

        messagebox.askyesnocancel() gibt drei mögliche Werte zurück:
            True  → Ja      (speichern und beenden)
            False → Nein    (ohne speichern beenden)
            None  → Abbruch (nicht beenden)
        """
        if self.lco.is_modified:
            antwort = messagebox.askyesnocancel(
                "FlashMob beenden",
                "Es gibt ungespeicherte Änderungen.\nVor dem Beenden speichern?",
            )
            if antwort is None:
                return   # Abbruch – Fenster bleibt offen
            if antwort:
                try:
                    self.lco.save_list()
                except OSError as e:
                    messagebox.showerror(
                        "Fehler beim Speichern",
                        f"Die Daten konnten nicht gespeichert werden:\n{e}",
                    )
                    return   # nicht beenden, damit nichts verloren geht

        self.destroy()


# =============================================================================
# Direktausführungs-Schutz
# =============================================================================
#
# __name__ ist eine automatische Python-Variable.
# Wenn diese Datei direkt gestartet wird (python main.py),
#   → __name__ == "__main__"  → App starten
# Wenn sie von einer anderen Datei importiert wird,
#   → __name__ == "main"      → App NICHT automatisch starten

if __name__ == "__main__":
    app = FlashMobApp()   # Objekt erstellen → __init__ wird aufgerufen
    app.mainloop()        # tkinter-Ereignisschleife starten
    # mainloop() hält das Fenster offen und reagiert auf Mausklicks,
    # Tastendrücke usw. – läuft bis das Fenster geschlossen wird.
