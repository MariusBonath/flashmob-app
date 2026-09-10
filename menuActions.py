# =============================================================================
# menuActions.py – Aktionen hinter den Menüpunkten
# =============================================================================
#
# Dieses Modul enthält die Klasse "MenuActions".
# Sie steuert den rechten Content-Bereich der App:
# Jeder Menüklick in der Sidebar ruft eine action_*()-Methode auf,
# die den Arbeitsbereich neu aufbaut und befüllt.
#
# Konzepte in dieser Datei:
#   - Klasse mit Konstruktor und Instanzvariablen
#   - ttk.Treeview          (Tabellen-Widget mit Spalten und Scrollbar)
#   - ttk.Style             (Aussehen von ttk-Widgets anpassen)
#   - ttk.Combobox          (Auswahlfeld / Dropdown)
#   - tk.Toplevel           (modales Dialogfenster)
#   - tk.Entry              (einzeiliges Texteingabefeld)
#   - messagebox            (Ja/Nein-Dialoge)
#   - filedialog            (nativer Datei-Öffnen/Speichern-Dialog)
#   - Verschachtelte Funktionen (on_edit, save, on_delete innerhalb der Methoden)
#   - Lambda mit Default-Argument (Late-Binding-Lösung)
#   - zip()                 (zwei Listen parallel durchlaufen)
#   - enumerate()           (Index + Wert gleichzeitig)
#   - any()                 (True wenn mindestens eine Bedingung erfüllt)
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from library import editMod as em

# Alle Farben und Schriften kommen zentral aus theme.py
# (früher waren sie doppelt in menuMod.py und menuActions.py definiert).
from theme import (
    FARBE_CONTENT_BG, FARBE_HEADER_BG, FARBE_AKZENT, FARBE_TEXT_DUNKEL,
    FARBE_STATUS_OK, FARBE_STATUS_ERR, FARBE_WEISS,
    FARBE_BTN_INAKTIV, FARBE_BTN_NEUTRAL, FARBE_TRENNLINIE_HELL,
    SCHRIFT_TITEL, SCHRIFT_TEXT, SCHRIFT_MONO,
)


# =============================================================================
# Klasse: MenuActions
# =============================================================================

class MenuActions:
    """
    Steuert den rechten Content-Bereich der FlashMobApp.

    Jede öffentliche action_*()-Methode entspricht einem Menüpunkt
    in der Sidebar. Sie räumt den Arbeitsbereich auf und befüllt
    ihn mit neuen Widgets.

    Wird in main.py als Abhängigkeit erstellt und an MenuModule übergeben.
    """

    def __init__(self, content_frame: tk.Frame, lco,
                 header: list, col_widths: list,
                 prompts: list, format_specs: list,
                 fpath_csv: str) -> None:
        """
        Konstruktor: Speichert alle Abhängigkeiten und baut das Basis-Layout.

        Args:
            content_frame: Der rechte Frame aus main.py (Arbeitsbereich).
            lco:           Listclass-Objekt (Daten und Datenoperationen).
            header:        Spaltenüberschriften.
            col_widths:    Spaltenbreiten.
            prompts:       Eingabeaufforderungen.
            format_specs:  Validierungsregeln.
            fpath_csv:     Standard-CSV-Pfad.
        """
        self.content_frame = content_frame
        self.lco           = lco
        self.header        = header
        self.col_widths    = col_widths
        self.prompts       = prompts
        self.format_specs  = format_specs
        self.fpath_csv     = fpath_csv

        self._build_basis_layout()


    # =========================================================================
    # Basis-Layout (dauerhafter Rahmen)
    # =========================================================================

    def _build_basis_layout(self) -> None:
        """
        Erstellt den dauerhaften Rahmen des Content-Bereichs:
            - Titelzeile (oben, bleibt immer sichtbar)
            - Statustext (rechts in der Titelzeile)
            - Trennlinie
            - Arbeitsbereich (wird bei jeder Aktion geleert und neu befüllt)

        Dieser Rahmen wird nur einmal gebaut – nicht bei jedem Menüklick.
        Nur der Arbeitsbereich (_arbeitsbereich) wird regelmäßig geleert.
        """
        # Titelzeile (feste Höhe 52 px)
        self._titelzeile = tk.Frame(self.content_frame, bg=FARBE_HEADER_BG, height=52)
        self._titelzeile.pack(fill=tk.X)
        self._titelzeile.pack_propagate(False)

        # Titel-Label (links in der Titelzeile)
        self._titel_lbl = tk.Label(self._titelzeile, text="FlashMob",
                                   font=SCHRIFT_TITEL, bg=FARBE_HEADER_BG,
                                   fg=FARBE_TEXT_DUNKEL)
        self._titel_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Status-Label (rechts in der Titelzeile, zeigt Rückmeldungen)
        self._status_lbl = tk.Label(self._titelzeile, text="",
                                    font=SCHRIFT_TEXT, bg=FARBE_HEADER_BG,
                                    fg=FARBE_STATUS_OK)
        self._status_lbl.pack(side=tk.RIGHT, padx=20)

        # Farbige Trennlinie unter der Titelzeile
        tk.Frame(self.content_frame, bg=FARBE_AKZENT, height=2).pack(fill=tk.X)

        # Arbeitsbereich: wird bei jeder Aktion geleert (_clear_work)
        self._arbeitsbereich = tk.Frame(self.content_frame, bg=FARBE_CONTENT_BG)
        self._arbeitsbereich.pack(fill=tk.BOTH, expand=True)


    def _set_titel(self, text: str) -> None:
        """Ändert den Titel in der Titelzeile."""
        self._titel_lbl.configure(text=text)

    def _set_status(self, text: str, ok: bool = True) -> None:
        """
        Zeigt einen Statustext rechts in der Titelzeile.
        ok=True → grün, ok=False → rot.
        """
        farbe = FARBE_STATUS_OK if ok else FARBE_STATUS_ERR
        self._status_lbl.configure(text=text, fg=farbe)

    def _clear_work(self) -> None:
        """
        Löscht alle Widgets im Arbeitsbereich.
        Wird am Anfang jeder action_*()-Methode aufgerufen.

        winfo_children() gibt alle direkten Kind-Widgets zurück.
        destroy() entfernt das Widget und alle seine Kinder aus dem Speicher.
        """
        for widget in self._arbeitsbereich.winfo_children():
            widget.destroy()


    # =========================================================================
    # Hilfsmethode: Treeview (Tabellen-Widget)
    # =========================================================================

    def _build_treeview(self, parent: tk.Frame) -> ttk.Treeview:
        """
        Erstellt ein formatiertes Tabellen-Widget (ttk.Treeview) mit Scrollbar.

        ttk.Treeview vs. tk.Listbox:
            Treeview unterstützt mehrere Spalten, anklickbare Zeilen,
            Spaltenüberschriften und Custom-Styling.

        Styling mit ttk.Style:
            ttk-Widgets haben ein eigenes Style-System.
            style.configure("FM.Treeview", ...) definiert einen eigenen Stil
            mit dem Namen "FM.Treeview" (FM = FlashMob).

        Scrollbar verknüpfen:
            tree.configure(yscrollcommand=sb.set)
            sb = ttk.Scrollbar(..., command=tree.yview)
            → Scrollbar und Treeview steuern sich gegenseitig.

        Args:
            parent: Frame, in dem der Treeview platziert wird.

        Returns:
            Das fertige Treeview-Widget.
        """
        # Stil definieren
        stil = ttk.Style()
        stil.theme_use("clam")   # "clam" ist ein einfaches, anpassbares Theme
        stil.configure("FM.Treeview",
                       background=FARBE_WEISS,
                       fieldbackground=FARBE_WEISS,
                       foreground=FARBE_TEXT_DUNKEL,
                       rowheight=26,
                       font=SCHRIFT_MONO)
        stil.configure("FM.Treeview.Heading",
                       background=FARBE_HEADER_BG,
                       foreground=FARBE_TEXT_DUNKEL,
                       font=("Segoe UI", 10, "bold"))
        # style.map: definiert Farben für bestimmte Zustände (z. B. "selected")
        stil.map("FM.Treeview",
                 background=[("selected", FARBE_AKZENT)],
                 foreground=[("selected", FARBE_WEISS)])

        # Spalten = header-Spalten + "timestamp" (Zeitstempel)
        spalten = self.header + ["timestamp"]
        tree = ttk.Treeview(parent, columns=spalten, show="headings",
                            style="FM.Treeview")

        # Spaltenköpfe und -breiten setzen
        # zip() läuft header und col_widths gleichzeitig durch:
        # zip(["no","title",...], [6, 25, ...]) → ("no",6), ("title",25), ...
        for spalte, breite in zip(self.header, self.col_widths):
            tree.heading(spalte, text=spalte.capitalize())
            tree.column(spalte, width=max(breite * 9, 60), anchor="w")

        tree.heading("timestamp", text="Geändert")
        tree.column("timestamp", width=140, anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Treeview links, Scrollbar direkt daneben
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0), pady=12)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=12, padx=(0, 8))

        return tree


    def _befuelle_treeview(self, tree: ttk.Treeview, daten: list = None) -> None:
        """
        Füllt den Treeview mit Datensätzen.

        Args:
            tree:  Das zu befüllende Treeview-Widget.
            daten: Die anzuzeigenden Zeilen. None → self.lco._list
                   (z. B. sortierte oder gefilterte Listen aus action_sort).

        tree.delete(*tree.get_children()):
            → Löscht alle vorhandenen Zeilen (für Aktualisierung nach Änderungen)
            → * entpackt die Liste: delete(kind1, kind2, ...) statt delete([...])

        Auffüllen mit Leerzeichen:
            Manche Einträge haben keinen Zeitstempel (noch nie bearbeitet).
            len(self.header) + 1 = Anzahl Spalten inkl. "timestamp"
            Mit + [""] * (n - len(sublist)) wird die Zeile aufgefüllt.
        """
        if daten is None:
            daten = self.lco._list

        anzahl_spalten = len(self.header) + 1   # +1 für timestamp
        tree.delete(*tree.get_children())
        for sublist in daten:
            zeile = list(sublist) + [""] * (anzahl_spalten - len(sublist))
            tree.insert("", tk.END, values=zeile)
            # tk.END → am Ende einfügen
            # values=zeile → Werte für alle Spalten


    # =========================================================================
    # Hilfsmethode: Eingabe-Validierung
    # =========================================================================

    def _validiere(self, werte: list) -> tuple[bool, str]:
        """
        Prüft jeden eingegebenen Wert gegen die Regel aus self.format_specs
        (geladen aus config/books.json).

        Beispiel-Regeln:
            ["DIGIT"]  → nur Ziffern (Nr., Jahr)
            ["FLOAT"]  → Dezimalzahl (Preis)
            ["ALL"]    → beliebig (Titel)

        Args:
            werte: Liste der eingegebenen Strings (eine pro Spalte).

        Returns:
            (True, "")            wenn alles gültig
            (False, fehlermeldung) beim ersten ungültigen Feld
        """
        for i, wert in enumerate(werte):
            spec = self.format_specs[i] if i < len(self.format_specs) else ["ALL"]
            if not em.check_item(wert, spec):
                spalte = self.header[i] if i < len(self.header) else f"Feld {i + 1}"
                return False, f"Feld '{spalte}' ungültig – erwartet: {spec[0]}."
        return True, ""


    # =========================================================================
    # Hilfsmethode: Datensatz-Dialog (für "Insert" und "Edit")
    # =========================================================================

    def _build_datensatz_dialog(self, titel: str, werte: list,
                                on_save, nr_readonly: bool = False,
                                speichern_text: str = "Speichern") -> tk.Toplevel:
        """
        Baut ein modales Dialogfenster mit je einem Eingabefeld pro Spalte.

        Früher gab es diesen Code fast identisch zweimal (in _open_edit_dialog
        und in action_insert). Jetzt an einer Stelle.

        Args:
            titel:          Fenstertitel.
            werte:          Startwerte pro Spalte (gleiche Reihenfolge wie
                            self.header). Kürzere Liste → restliche Felder leer.
            on_save:        Callback, wird mit (neue_werte: list, fenster) aufgerufen.
                            Schließt das Fenster selbst, wenn das Speichern klappt.
            nr_readonly:    True → erstes Feld (Nummer) ist gesperrt.
            speichern_text: Beschriftung des Speichern-Buttons.

        Returns:
            Das erstellte Toplevel-Fenster.
        """
        fenster = tk.Toplevel(self.content_frame)
        fenster.title(titel)
        fenster.configure(bg=FARBE_CONTENT_BG)
        fenster.resizable(False, False)
        # transient + grab_set → der Dialog liegt über dem Hauptfenster und
        # blockiert es, bis er geschlossen wird (modaler Dialog).
        fenster.transient(self.content_frame.winfo_toplevel())
        fenster.grab_set()

        felder = []
        for i, spalte in enumerate(self.header):
            tk.Label(fenster, text=spalte.capitalize() + ":",
                     font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                     fg=FARBE_TEXT_DUNKEL).grid(row=i, column=0,
                                                padx=16, pady=6, sticky="e")
            eingabe = tk.Entry(fenster, font=SCHRIFT_MONO, width=32)
            if i < len(werte):
                eingabe.insert(0, str(werte[i]))
            if i == 0 and nr_readonly:
                eingabe.configure(state="readonly")   # Nummer nicht editierbar
            eingabe.grid(row=i, column=1, padx=12, pady=6)
            felder.append(eingabe)

        def speichern() -> None:
            # .get() funktioniert auch bei state="readonly"
            neue_werte = [e.get().strip() for e in felder]
            on_save(neue_werte, fenster)

        tk.Button(fenster, text=speichern_text, command=speichern,
                  bg=FARBE_AKZENT, fg="white", font=SCHRIFT_TEXT,
                  relief=tk.FLAT, padx=14, pady=6).grid(
                      row=len(self.header), column=0, columnspan=2, pady=12)

        return fenster


    # =========================================================================
    # Aktion: Show – Liste anzeigen
    # =========================================================================

    def action_show(self) -> None:
        """
        Zeigt alle Bücher als Treeview-Tabelle im Arbeitsbereich an.
        """
        self._set_titel("Bücherliste")
        self._clear_work()

        if not self.lco._list:
            # Leere Liste → Hinweistext statt Tabelle
            tk.Label(self._arbeitsbereich, text="Keine Einträge vorhanden.",
                     font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                     fg=FARBE_TEXT_DUNKEL).pack(pady=40)
            self._set_status("Liste ist leer.", ok=False)
            return

        tree = self._build_treeview(self._arbeitsbereich)
        self._befuelle_treeview(tree)
        self._set_status(f"{len(self.lco._list)} Einträge")


    # =========================================================================
    # Aktion: Edit – Eintrag bearbeiten
    # =========================================================================

    def action_edit(self) -> None:
        """
        Zeigt die Bücherliste und einen "Bearbeiten"-Button.
        Der Nutzer wählt einen Eintrag aus → Dialogfenster öffnet sich.
        """
        self._set_titel("Eintrag bearbeiten")
        self._clear_work()

        # Obere Zeile: Button + Hinweistext
        obere_zeile = tk.Frame(self._arbeitsbereich, bg=FARBE_CONTENT_BG)
        obere_zeile.pack(fill=tk.X, padx=16, pady=(12, 4))

        edit_btn = tk.Button(obere_zeile, text="✏  Bearbeiten",
                             bg=FARBE_AKZENT, fg="white", font=SCHRIFT_TEXT,
                             relief=tk.FLAT, padx=14, pady=6, cursor="hand2")
        edit_btn.pack(side=tk.LEFT)

        tk.Label(obere_zeile, text="  Eintrag auswählen und bearbeiten.",
                 font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                 fg=FARBE_TEXT_DUNKEL).pack(side=tk.LEFT, padx=8)

        # Treeview darunter
        tree = self._build_treeview(self._arbeitsbereich)
        self._befuelle_treeview(tree)

        def on_edit() -> None:
            """
            Verschachtelte Funktion: wird aufgerufen wenn "Bearbeiten" geklickt.

            WICHTIG – warum tree.index() statt tree.item()["values"]?
                tkinter wandelt zahlartige Werte im Treeview automatisch in
                int um: "007" wird zu 7, "001" zu 1. Würde man den Dialog aus
                diesen Werten befüllen, gingen führende Nullen verloren und
                landeten so beim Speichern in den Daten.
                Deshalb: nur die POSITION der Zeile aus dem Treeview holen und
                den echten Datensatz aus self.lco._list lesen.
            """
            auswahl = tree.selection()
            if not auswahl:
                self._set_status("Kein Eintrag ausgewählt.", ok=False)
                return

            # tree.index(item) → Position der Zeile (0, 1, 2, …).
            # Der Treeview wurde mit _befuelle_treeview in genau der Reihenfolge
            # von self.lco._list gefüllt → die Position ist der Listen-Index.
            index = tree.index(auswahl[0])
            datensatz = self.lco._list[index]

            def speichern(neue_werte: list, fenster) -> None:
                ok, meldung = self._validiere(neue_werte)
                if not ok:
                    self._set_status(meldung, ok=False)
                    return
                # edit_list() gibt die Werte + automatischen Zeitstempel zurück
                self.lco._list[index] = self.lco.edit_list(neue_werte)
                self.lco.is_modified = True
                self._befuelle_treeview(tree)
                self._set_status(f"Eintrag {neue_werte[0]} aktualisiert.")
                fenster.destroy()

            # Dialog mit den ECHTEN Werten aus der Liste befüllen (erste
            # len(header) Felder; ein evtl. vorhandener Zeitstempel bleibt außen vor)
            self._build_datensatz_dialog("Eintrag bearbeiten", datensatz, speichern)

        edit_btn.configure(command=on_edit)
        self._set_status("Eintrag auswählen und bearbeiten.")


    # =========================================================================
    # Aktion: Save – Speichern
    # =========================================================================

    def action_save(self) -> None:
        """
        Speichert die Bücherliste und zeigt eine Rückmeldung.
        Fehler werden abgefangen und als Fehlermeldung angezeigt.
        """
        self._set_titel("Speichern")
        self._clear_work()

        try:
            self.lco.save_list()
            meldung = "Liste erfolgreich gespeichert."
            ok = True
        except Exception as e:
            meldung = f"Fehler beim Speichern: {e}"
            ok = False

        symbol = "✔" if ok else "✖"
        farbe  = FARBE_STATUS_OK if ok else FARBE_STATUS_ERR

        tk.Label(self._arbeitsbereich, text=f"{symbol}  {meldung}",
                 font=("Segoe UI", 13), bg=FARBE_CONTENT_BG,
                 fg=farbe).pack(pady=60)
        self._set_status(meldung, ok=ok)


    # =========================================================================
    # Aktion: Sort – Sortieren und Buchstabenfilter
    # =========================================================================

    def action_sort(self) -> None:
        """
        Zeigt die Bücherliste sortiert und ermöglicht das Filtern
        nach dem Anfangsbuchstaben des Titels.

        Diese Methode ist nur noch der "Bauleiter". Die drei Teilbereiche
        werden von eigenen Hilfsmethoden erstellt:
            _build_spalten_sortierung()  → Dropdown + Sortieren-Button
            _build_buchstabenfilter()    → 26 A–Z-Buttons + "Alle anzeigen"
        Der Treeview wird zuerst gebaut, weil die Callbacks der beiden
        Teilbereiche eine Referenz darauf brauchen.
        """
        self._set_titel("Liste sortieren")
        self._clear_work()

        # Drei Zonen von oben nach unten (pack folgt der Aufrufreihenfolge)
        zone_oben  = tk.Frame(self._arbeitsbereich, bg=FARBE_CONTENT_BG)
        zone_oben.pack(fill=tk.X)
        zone_mitte = tk.Frame(self._arbeitsbereich, bg=FARBE_CONTENT_BG)
        zone_mitte.pack(fill=tk.X)
        zone_unten = tk.Frame(self._arbeitsbereich, bg=FARBE_CONTENT_BG)
        zone_unten.pack(fill=tk.BOTH, expand=True)

        tree = self._build_treeview(zone_unten)
        self._build_spalten_sortierung(zone_oben, tree)
        self._build_buchstabenfilter(zone_mitte, tree)

        # Startzustand: alle Titel alphabetisch
        # (Lambda-Transfer: sorted(..., key=lambda zeile: zeile[1]))
        self._befuelle_treeview(tree, self.lco.sort_by_title())
        self._set_status("Buchstabe wählen oder Spalte sortieren.")


    def _build_spalten_sortierung(self, parent: tk.Frame, tree: ttk.Treeview) -> None:
        """
        Baut die obere Zeile: Dropdown mit allen Spalten + "Sortieren"-Button.
        Ein Klick sortiert self.lco._list dauerhaft nach der gewählten Spalte.
        """
        zeile = tk.Frame(parent, bg=FARBE_CONTENT_BG)
        zeile.pack(padx=16, pady=(12, 4), anchor="w")

        tk.Label(zeile, text="Sortieren nach Spalte:",
                 font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                 fg=FARBE_TEXT_DUNKEL).pack(side=tk.LEFT, padx=(0, 8))

        # tk.StringVar verknüpft den ausgewählten Wert mit einer Variable
        spalten_var = tk.StringVar(
            value=self.header[1] if len(self.header) > 1 else self.header[0])
        ttk.Combobox(zeile, textvariable=spalten_var, values=self.header,
                     state="readonly", width=14).pack(side=tk.LEFT)

        def sortieren() -> None:
            index = self.header.index(spalten_var.get())
            self.lco._list = self.lco.sort_list(index)   # dauerhaft sortieren
            self.lco.is_modified = True                  # zählt als Änderung
            self._befuelle_treeview(tree)
            self._set_status(f"Sortiert nach: {spalten_var.get()}")

        tk.Button(zeile, text="↕  Sortieren", command=sortieren,
                  bg=FARBE_AKZENT, fg="white", font=SCHRIFT_TEXT,
                  relief=tk.FLAT, padx=12, pady=4, cursor="hand2").pack(
                      side=tk.LEFT, padx=8)

        # dünne Trennlinie unter der Zeile
        tk.Frame(parent, bg=FARBE_TRENNLINIE_HELL, height=1).pack(
            fill=tk.X, padx=16, pady=(4, 6))


    def _build_buchstabenfilter(self, parent: tk.Frame, tree: ttk.Treeview) -> None:
        """
        Baut den A–Z-Filter: 26 Buttons in zwei Reihen + "Alle anzeigen".

        Ein Klick auf einen Buchstaben zeigt nur Titel mit diesem
        Anfangsbuchstaben (self.lco._list bleibt unverändert – nur die
        Anzeige wird gefiltert). Zweiter Klick auf denselben Buchstaben
        hebt den Filter wieder auf.

        Late-Binding-Lösung bei den Buttons:
            b.configure(command=lambda c=ch, btn=b: on_letter(c, btn))
            c=ch / btn=b speichern den aktuellen Wert – ohne sie würden alle
            26 Buttons denselben (letzten) Buchstaben verwenden.
        """
        tk.Label(parent, text="Titelsuche nach Anfangsbuchstabe:",
                 font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                 fg=FARBE_TEXT_DUNKEL).pack(padx=16, anchor="w")

        # Merkt sich, welcher Buchstaben-Button gerade aktiv ist
        aktiver_btn = {"ref": None, "buchstabe": ""}

        def markierung_loeschen() -> None:
            if aktiver_btn["ref"] is not None:
                aktiver_btn["ref"].configure(bg=FARBE_BTN_INAKTIV,
                                             fg=FARBE_TEXT_DUNKEL)
            aktiver_btn["ref"] = None
            aktiver_btn["buchstabe"] = ""

        def alle_anzeigen() -> None:
            markierung_loeschen()
            self._befuelle_treeview(tree, self.lco.filter_by_title_letter(""))
            self._set_status("Alle Titel (A → Z)")

        def on_letter(buchstabe: str, btn: tk.Button) -> None:
            if aktiver_btn["buchstabe"] == buchstabe:
                # Zweiter Klick auf denselben Buchstaben → Filter aus
                alle_anzeigen()
                return

            markierung_loeschen()
            aktiver_btn["ref"] = btn
            aktiver_btn["buchstabe"] = buchstabe
            btn.configure(bg=FARBE_AKZENT, fg="white")

            ergebnis = self.lco.filter_by_title_letter(buchstabe)
            self._befuelle_treeview(tree, ergebnis)
            treffer = len(ergebnis)
            self._set_status(
                f"Titel mit '{buchstabe}': {treffer} Treffer" if treffer
                else f"Kein Titel beginnt mit '{buchstabe}'")

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for reihe_buchstaben in (alphabet[:13], alphabet[13:]):
            reihen_frame = tk.Frame(parent, bg=FARBE_CONTENT_BG)
            reihen_frame.pack(padx=16, pady=1, anchor="w")
            for ch in reihe_buchstaben:
                b = tk.Button(reihen_frame, text=ch, width=3,
                              bg=FARBE_BTN_INAKTIV, fg=FARBE_TEXT_DUNKEL,
                              font=("Consolas", 9, "bold"),
                              relief=tk.FLAT, cursor="hand2")
                b.configure(command=lambda c=ch, btn=b: on_letter(c, btn))
                b.pack(side=tk.LEFT, padx=1, pady=1)

        tk.Button(parent, text="✕  Alle anzeigen", command=alle_anzeigen,
                  bg=FARBE_BTN_NEUTRAL, fg="white", font=SCHRIFT_TEXT,
                  relief=tk.FLAT, padx=10, pady=3, cursor="hand2").pack(
                      padx=16, pady=(2, 6), anchor="w")


    # =========================================================================
    # Aktion: Export CSV
    # =========================================================================

    def action_export_csv(self) -> None:
        """
        Öffnet einen nativen Speichern-Dialog und exportiert die Daten als CSV.

        filedialog.asksaveasfilename():
            → Öffnet den System-Dateidialog "Speichern unter"
            → Gibt den gewählten Dateipfad zurück, oder "" wenn abgebrochen
        """
        self._set_titel("Export CSV")
        self._clear_work()

        pfad = filedialog.asksaveasfilename(
            title="CSV speichern unter",
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")],
            initialfile="booklist.csv",
        )

        if not pfad:
            # Nutzer hat abgebrochen
            self._set_status("Export abgebrochen.", ok=False)
            tk.Label(self._arbeitsbereich, text="Export abgebrochen.",
                     font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                     fg=FARBE_STATUS_ERR).pack(pady=40)
            return

        try:
            self.lco.export2csv(pfad, self.header)
            meldung = f"✔  Exportiert nach:\n{pfad}"
            ok = True
        except Exception as e:
            meldung = f"✖  Fehler: {e}"
            ok = False

        tk.Label(self._arbeitsbereich, text=meldung,
                 font=("Segoe UI", 11), bg=FARBE_CONTENT_BG,
                 fg=FARBE_STATUS_OK if ok else FARBE_STATUS_ERR,
                 justify="left").pack(pady=40, padx=20, anchor="w")
        self._set_status("CSV exportiert." if ok else "Fehler beim Export.", ok=ok)


    # =========================================================================
    # Aktion: Import CSV
    # =========================================================================

    def action_import_csv(self) -> None:
        """
        Öffnet einen nativen Öffnen-Dialog und importiert Daten aus einer CSV.

        filedialog.askopenfilename():
            → Öffnet den System-Dateidialog "Datei öffnen"
            → Gibt den gewählten Dateipfad zurück, oder "" wenn abgebrochen
        """
        self._set_titel("Import CSV")
        self._clear_work()

        pfad = filedialog.askopenfilename(
            title="CSV-Datei öffnen",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")],
        )

        if not pfad:
            self._set_status("Import abgebrochen.", ok=False)
            tk.Label(self._arbeitsbereich, text="Import abgebrochen.",
                     font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                     fg=FARBE_STATUS_ERR).pack(pady=40)
            return

        try:
            self.lco.import_csv(pfad)
            meldung = f"✔  {len(self.lco._list)} Zeilen importiert aus:\n{pfad}"
            ok = True
        except Exception as e:
            meldung = f"✖  Fehler: {e}"
            ok = False

        tk.Label(self._arbeitsbereich, text=meldung,
                 font=("Segoe UI", 11), bg=FARBE_CONTENT_BG,
                 fg=FARBE_STATUS_OK if ok else FARBE_STATUS_ERR,
                 justify="left").pack(pady=40, padx=20, anchor="w")
        self._set_status("CSV importiert." if ok else "Fehler beim Import.", ok=ok)


    # =========================================================================
    # Aktion: Insert – Neuen Eintrag einfügen
    # =========================================================================

    def action_insert(self) -> None:
        """
        Öffnet ein Dialogfenster mit Eingabefeldern für einen neuen Datensatz.

        Position und Nummer bestimmt self.lco.next_free():
            - lückenlose Liste 001..005  → am Ende anhängen, Nummer 006
            - Lücke 001, 002, 004        → an der Lücke einfügen, Nummer 003

        Die Nummern-Spalte wird automatisch befüllt und gesperrt (readonly),
        alle Felder werden vor dem Einfügen gegen self.format_specs geprüft.
        """
        self._set_titel("Eintrag einfügen")
        self._clear_work()

        # Position + Nummer EINMAL festlegen, damit Anzeige und Speichern
        # garantiert denselben Wert verwenden.
        ziel_index, ziel_nummer = self.lco.next_free()

        startwerte = [""] * len(self.header)
        startwerte[0] = ziel_nummer

        def speichern(neue_werte: list, fenster) -> None:
            ok, meldung = self._validiere(neue_werte)
            if not ok:
                self._set_status(meldung, ok=False)
                return

            self.lco.insert_sublist(ziel_index, neue_werte)
            self.lco.is_modified = True
            fenster.destroy()

            titel = neue_werte[1] if len(neue_werte) > 1 else neue_werte[0]
            self._set_status(f"Eintrag '{titel}' eingefügt.")
            self.action_show()   # direkt zur Liste wechseln

        self._build_datensatz_dialog("Neuer Eintrag", startwerte, speichern,
                                     nr_readonly=True, speichern_text="➕  Einfügen")

        tk.Label(self._arbeitsbereich,
                 text="Fülle das Formular im Dialogfenster aus.",
                 font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                 fg=FARBE_TEXT_DUNKEL).pack(pady=40)
        self._set_status("Neuen Eintrag eingeben.")


    # =========================================================================
    # Aktion: Delete – Eintrag löschen
    # =========================================================================

    def action_delete(self) -> None:
        """
        Zeigt die Liste und ermöglicht das Löschen eines ausgewählten Eintrags.

        messagebox.askyesno():
            → Öffnet einen nativen Bestätigungs-Dialog mit "Ja" / "Nein"
            → Gibt True (Ja) oder False (Nein) zurück
        """
        self._set_titel("Eintrag löschen")
        self._clear_work()

        tk.Label(self._arbeitsbereich,
                 text="Eintrag auswählen und auf 'Löschen' klicken.",
                 font=SCHRIFT_TEXT, bg=FARBE_CONTENT_BG,
                 fg=FARBE_TEXT_DUNKEL).pack(padx=16, pady=(12, 4), anchor="w")

        tree = self._build_treeview(self._arbeitsbereich)
        self._befuelle_treeview(tree)

        btn_frame = tk.Frame(self._arbeitsbereich, bg=FARBE_CONTENT_BG)
        btn_frame.pack(fill=tk.X, padx=16, pady=8)

        def on_delete() -> None:
            """Bestimmt die ausgewählte Zeile über ihre Position und löscht sie."""
            auswahl = tree.selection()
            if not auswahl:
                self._set_status("Kein Eintrag ausgewählt.", ok=False)
                return

            # Position im Treeview = Index in self.lco._list (siehe on_edit).
            # So umgehen wir die int-Umwandlung von tkinter und brauchen keine
            # fehleranfällige Nummern-Suche.
            index = tree.index(auswahl[0])
            datensatz = self.lco._list[index]
            nummer = str(datensatz[0])
            titel  = str(datensatz[1]) if len(datensatz) > 1 else nummer

            if messagebox.askyesno(
                "Löschen bestätigen",
                f"Eintrag '{nummer} – {titel}' wirklich löschen?",
            ):
                self.lco.delete_sublist(index)
                self.lco.is_modified = True
                self._befuelle_treeview(tree)    # Treeview aktualisieren
                self._set_status(f"Eintrag {nummer} gelöscht.")

        tk.Button(btn_frame, text="🗑  Löschen", command=on_delete,
                  bg=FARBE_STATUS_ERR, fg="white", font=SCHRIFT_TEXT,
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2").pack(side=tk.LEFT)
        self._set_status("Eintrag auswählen und löschen.")
