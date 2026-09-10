# =============================================================================
# menuMod.py – Sidebar-Modul (MenuModule)
# =============================================================================
#
# Dieses Modul enthält die Klasse "MenuModule".
# Sie baut die linke Sidebar der Anwendung auf und verwaltet:
#   - Logo (Bild oder Canvas-Fallback)
#   - Menü-Labels (klickbare Einträge)
#   - Quit-Button (unten)
#   - Hover- und Klick-Effekte (visuelle Rückmeldung)
#
# Konzepte in dieser Datei:
#   - tkinter-Widgets: tk.Frame, tk.Label, tk.Canvas, ttk.Scrollbar
#   - Ereignis-Binding (.bind) und Ereignisse ("<Button-1>", "<Enter>", "<Leave>")
#   - Lambda in Event-Bindings (mit Default-Argument zur Vermeidung von Late-Binding)
#   - Callbacks (Funktionen als Parameter übergeben)
#   - try / except (Pillow-Import als optionale Abhängigkeit)
#   - Typ-Annotationen: dict, str | None
#   - Farb-Konstanten (HEX-Farbcodes)
# =============================================================================

import tkinter as tk

# Alle Farben kommen zentral aus theme.py – so kann es nicht mehr passieren,
# dass menuMod.py und menuActions.py unterschiedliche Werte für dieselbe
# Farbe verwenden.
from theme import (
    FARBE_HINTERGRUND, FARBE_LOGO_BG, FARBE_EINTRAG, FARBE_HOVER,
    FARBE_AKTIV, FARBE_TEXT, FARBE_TEXT_AKTIV, FARBE_AKZENT,
    FARBE_QUIT_TEXT, FARBE_QUIT_HOVER, FARBE_LOGO_BUCH, FARBE_LOGO_LINIEN,
)


# =============================================================================
# Klasse: MenuModule
# =============================================================================

class MenuModule:
    """
    Erstellt und verwaltet die linke Sidebar der FlashMobApp.

    Die Sidebar enthält (von oben nach unten):
        1. Logo (Bild oder gezeichnetes Fallback-Logo)
        2. Trennlinie
        3. Menü-Labels (ein Label pro Menüpunkt)
        4. Quit-Button (ganz unten)

    Verwendung in main.py:
        menu_module = MenuModule(sidebar_frame, ["Edit", "Show", ...])
        menu_module.bind_actions({"Edit": func, "Show": func, ...})
    """

    def __init__(self, parent: tk.Frame, menu_items: list) -> None:
        """
        Konstruktor: Baut die Sidebar sofort auf.

        Args:
            parent:     Der übergeordnete Frame (sidebar_frame aus main.py).
            menu_items: Liste der Menünamen, z. B. ["Edit", "Show", "Save", ...]
        """
        self.parent     = parent
        self.menu_items = menu_items

        # Dictionary: Menüname → Label-Widget
        # dict[str, tk.Label] = Typ-Annotation (str-Schlüssel, Label-Wert)
        self._labels: dict[str, tk.Label] = {}

        # Aktuell aktiver Menüpunkt (für visuelles Hervorheben)
        # str | None → kann ein String oder None sein
        self._aktiver_eintrag: str | None = None

        # Callbacks (werden später in bind_actions gesetzt)
        self._home_callback = None   # Logo-Klick → Startansicht
        self._quit_callback = None   # "Beenden" → App schließen (mit Speicherabfrage)

        # Sidebar aufbauen (Reihenfolge = Anzeigereihenfolge)
        self._build_logo()
        self._build_trennlinie()
        self._build_menu_labels()
        self._build_quit_button()


    # =========================================================================
    # Logo
    # =========================================================================

    def _build_logo(self) -> None:
        """
        Zeigt das App-Logo oben in der Sidebar.

        Strategie:
            1. Versuche, logo.png mit der Pillow-Bibliothek zu laden.
            2. Wenn Pillow nicht installiert ist oder die Datei fehlt
               → Fallback: Logo auf einem tk.Canvas zeichnen.

        Klick auf das Logo → _on_logo_click() → Dashboard zeigen.
        """

        # Äußerer Frame für den Logo-Bereich
        self._logo_frame = tk.Frame(self.parent, bg=FARBE_LOGO_BG, height=90,
                                    cursor="hand2")   # "hand2" = Handzeiger-Cursor
        self._logo_frame.pack(fill=tk.X)
        self._logo_frame.pack_propagate(False)   # Höhe beibehalten

        # Klick-Ereignis auf den Logo-Frame binden
        # lambda e: ...  → e ist das Ereignis-Objekt (wird nicht benötigt)
        self._logo_frame.bind("<Button-1>", lambda e: self._on_logo_click())

        try:
            # Pillow (PIL) ist eine externe Bibliothek für Bildverarbeitung.
            # "from PIL import ..." schlägt fehl, wenn Pillow nicht installiert ist
            # → dann springt Python in den except-Block.
            from PIL import Image, ImageTk
            import os

            # Pfad zur logo.png relativ zur Position dieser Datei
            logo_pfad = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "logo.png")

            img = Image.open(logo_pfad)

            # Bild proportional auf 180 px Breite skalieren
            ziel_breite  = 180
            faktor       = ziel_breite / img.width
            ziel_hoehe   = int(img.height * faktor)
            img          = img.resize((ziel_breite, ziel_hoehe), Image.LANCZOS)

            # ImageTk.PhotoImage: wandelt PIL-Bild in tkinter-kompatibles Format um
            # WICHTIG: self._logo_img als Instanzvariable speichern!
            # Python's Garbage Collector würde das Bild sonst löschen,
            # weil tkinter keine eigene Referenz darauf hält.
            self._logo_img = ImageTk.PhotoImage(img)

            self._logo_frame.configure(height=ziel_hoehe + 16)

            logo_label = tk.Label(self._logo_frame, image=self._logo_img,
                                  bg=FARBE_LOGO_BG, cursor="hand2")
            logo_label.pack(pady=8)
            logo_label.bind("<Button-1>", lambda e: self._on_logo_click())

        except Exception:
            # Pillow fehlt oder logo.png nicht gefunden → gezeichnetes Fallback-Logo
            self._build_canvas_logo(self._logo_frame)


    def _build_canvas_logo(self, parent: tk.Frame) -> None:
        """
        Zeichnet ein einfaches Logo auf einem tk.Canvas.
        Wird als Fallback verwendet, wenn Pillow nicht verfügbar ist.

        Canvas-Konzept:
            tk.Canvas ist eine Zeichenfläche.
            Man kann darauf Rechtecke, Linien, Texte usw. platzieren,
            jeweils mit absoluten Koordinaten (x1, y1, x2, y2).
        """
        canvas = tk.Canvas(parent, width=160, height=72,
                           bg=FARBE_LOGO_BG, highlightthickness=0,
                           cursor="hand2")
        canvas.pack(pady=8)

        # Zwei überlagerte Rechtecke als "Buch"-Symbol
        canvas.create_rectangle(20, 14, 50, 58, fill=FARBE_AKZENT, outline="")
        canvas.create_rectangle(24, 14, 54, 58, fill=FARBE_LOGO_BUCH, outline="")

        # Waagerechte Linien = "Seiten" des Buches
        for y in (22, 30, 38, 46):
            canvas.create_line(27, y, 51, y, fill=FARBE_LOGO_LINIEN, width=1)

        # App-Name als Text
        canvas.create_text(95, 36, text="FlashMob",
                           font=("Segoe UI", 13, "bold"),
                           fill=FARBE_TEXT_AKTIV, anchor="w")

        canvas.bind("<Button-1>", lambda e: self._on_logo_click())


    def _on_logo_click(self) -> None:
        """
        Reagiert auf einen Klick auf das Logo.
        Setzt den aktiven Menüeintrag zurück und ruft die Startansicht auf
        (in main.py mit action_show verknüpft → zeigt die Bücherliste).
        """
        # Aktiven Eintrag visuell deaktivieren
        if self._aktiver_eintrag and self._aktiver_eintrag in self._labels:
            self._labels[self._aktiver_eintrag].configure(
                bg=FARBE_EINTRAG, fg=FARBE_TEXT)
        self._aktiver_eintrag = None

        # Startansicht-Callback aufrufen (falls gesetzt)
        if self._home_callback:
            self._home_callback()


    # =========================================================================
    # Trennlinie
    # =========================================================================

    def _build_trennlinie(self) -> None:
        """
        Zeichnet eine farbige Trennlinie (2 px Höhe) unter dem Logo.
        Ein sehr schmaler tk.Frame mit Hintergrundfarbe wirkt als Linie.
        """
        tk.Frame(self.parent, bg=FARBE_AKZENT, height=2).pack(
            fill=tk.X, padx=12, pady=(0, 8))


    # =========================================================================
    # Menü-Labels
    # =========================================================================

    def _build_menu_labels(self) -> None:
        """
        Erstellt für jeden Menüpunkt ein klickbares Label in der Sidebar.

        Ereignisse (Events) die gebunden werden:
            "<Enter>"    → Maus betritt das Label → Hover-Effekt an
            "<Leave>"    → Maus verlässt das Label → Hover-Effekt aus
            (Klick wird später in bind_actions() gebunden)

        Lambda mit Default-Argument (Late-Binding-Problem):
            lbl.bind("<Enter>", lambda e, l=lbl: self._on_hover(l, True))
                                                  ↑
                                           l=lbl speichert den aktuellen Wert
                                           von lbl in der Lambda-Variable l.
            Ohne l=lbl würden ALLE Lambda-Funktionen dasselbe (letzte) lbl
            verwenden – ein klassisches Anfänger-Problem mit Schleifen und Lambda.
        """
        for eintrag in self.menu_items:
            lbl = tk.Label(
                self.parent,
                text=f"  {eintrag}",       # zwei Leerzeichen als Einrückung
                font=("Segoe UI", 11),
                bg=FARBE_EINTRAG,
                fg=FARBE_TEXT,
                anchor="w",                # Text linksbündig
                pady=10,
                padx=8,
                cursor="hand2",
            )
            lbl.pack(fill=tk.X, padx=6, pady=2)

            # Label im Dictionary speichern (für späteren Zugriff per Name)
            self._labels[eintrag] = lbl

            # Hover-Effekte binden (l=lbl: Default-Argument gegen Late-Binding)
            lbl.bind("<Enter>", lambda e, l=lbl: self._on_hover(l, True))
            lbl.bind("<Leave>", lambda e, l=lbl: self._on_hover(l, False))


    # =========================================================================
    # Quit-Button
    # =========================================================================

    def _build_quit_button(self) -> None:
        """
        Platziert den Beenden-Button ganz unten in der Sidebar.

        Trick für "unten ausrichten":
            Ein leerer Frame mit expand=True "schiebt" den Quit-Button nach unten.
            Er füllt den gesamten verbleibenden Platz.
        """
        # Leerer Platzhalter-Frame (schiebt alles danach nach unten)
        tk.Frame(self.parent, bg=FARBE_EINTRAG).pack(fill=tk.BOTH, expand=True)

        # Trennlinie über dem Quit-Button
        tk.Frame(self.parent, bg=FARBE_AKZENT, height=2).pack(
            fill=tk.X, padx=12, pady=(0, 4))

        quit_lbl = tk.Label(
            self.parent,
            text="  ⏻  Beenden",
            font=("Segoe UI", 11),
            bg=FARBE_EINTRAG,
            fg=FARBE_QUIT_TEXT,     # Rot für "Beenden"
            anchor="w",
            pady=10,
            padx=8,
            cursor="hand2",
        )
        quit_lbl.pack(fill=tk.X, padx=6, pady=(0, 8))

        # Hover: Hintergrund leicht röten
        quit_lbl.bind("<Enter>", lambda e: quit_lbl.configure(bg=FARBE_QUIT_HOVER))
        quit_lbl.bind("<Leave>", lambda e: quit_lbl.configure(bg=FARBE_EINTRAG))

        # Klick: App beenden – über _on_quit(), damit vorher nach ungespeicherten
        # Änderungen gefragt werden kann (Callback wird in bind_actions gesetzt).
        quit_lbl.bind("<Button-1>", lambda e: self._on_quit())


    # =========================================================================
    # Aktionen binden (public)
    # =========================================================================

    def bind_actions(self, mapping: dict, home_callback=None,
                     quit_callback=None) -> None:
        """
        Verknüpft jeden Menüpunkt mit einer Callback-Funktion.

        Wird von main.py aufgerufen, nachdem MenuActions erstellt wurde.

        Args:
            mapping:       Dictionary {Menüname: Funktion},
                           z. B. {"Edit": actions.action_edit, ...}
            home_callback: Optionale Funktion für Logo-Klick (Startansicht).
            quit_callback: Optionale Funktion für "Beenden". Wenn gesetzt,
                           übernimmt sie das Schließen (inkl. Speicherabfrage).
        """
        self._home_callback = home_callback
        self._quit_callback = quit_callback

        for eintrag, callback in mapping.items():
            if eintrag in self._labels:
                lbl = self._labels[eintrag]

                # Klick-Ereignis binden
                # l=lbl, name=eintrag, cb=callback → Default-Argumente
                # verhindern das Late-Binding-Problem in der Schleife
                lbl.bind(
                    "<Button-1>",
                    lambda e, l=lbl, name=eintrag, cb=callback:
                        self._on_click(l, name, cb)
                )


    def _on_quit(self) -> None:
        """
        Reagiert auf einen Klick auf "Beenden".

        Ist ein quit_callback gesetzt (aus main.py), entscheidet dieser über
        das Schließen – dort wird nach ungespeicherten Änderungen gefragt.
        Ohne Callback wird das Fenster direkt geschlossen.
        """
        if self._quit_callback:
            self._quit_callback()
        else:
            self.parent.winfo_toplevel().destroy()


    # =========================================================================
    # Hover- und Klick-Effekte (private)
    # =========================================================================

    def _on_hover(self, label: tk.Label, betritt: bool) -> None:
        """
        Ändert die Hintergrundfarbe beim Hover (Maus drüber / weg).
        Der aktive Eintrag wird dabei nicht überschrieben.

        Args:
            label:   Das betroffene Label-Widget.
            betritt: True wenn Maus das Label betritt, False wenn sie es verlässt.
        """
        # .cget("text") gibt den aktuellen Text des Labels zurück
        # .strip() entfernt die führenden Leerzeichen
        if label.cget("text").strip() == self._aktiver_eintrag:
            return   # aktiven Eintrag nicht überfärben

        neue_farbe = FARBE_HOVER if betritt else FARBE_EINTRAG
        label.configure(bg=neue_farbe)


    def _on_click(self, label: tk.Label, name: str, callback) -> None:
        """
        Reagiert auf einen Klick auf ein Menü-Label.

        Ablauf:
            1. Vorherigen aktiven Eintrag optisch deaktivieren
            2. Neuen Eintrag als aktiv markieren
            3. Zugehörige Aktion aufrufen (callback)

        Args:
            label:    Das geklickte Label-Widget.
            name:     Der Menüname (z. B. "Show").
            callback: Die auszuführende Aktion.
        """
        # Vorherigen aktiven Eintrag zurücksetzen
        if self._aktiver_eintrag and self._aktiver_eintrag in self._labels:
            self._labels[self._aktiver_eintrag].configure(
                bg=FARBE_EINTRAG, fg=FARBE_TEXT)

        # Neuen Eintrag aktivieren
        self._aktiver_eintrag = name
        label.configure(bg=FARBE_AKTIV, fg=FARBE_TEXT_AKTIV)

        # Aktion ausführen
        callback()
