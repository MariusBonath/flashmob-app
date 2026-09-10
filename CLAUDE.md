# CLAUDE.md – FlashMob App

## Projekt-Überblick

Desktop-GUI-Anwendung zur Bücherverwaltung in Python mit tkinter.
Weiterentwicklung des Book Manager (CLI) — gleiche Kern-Architektur, aber mit vollständiger grafischer Oberfläche.
Entwickelt im Rahmen einer Umschulung zum Fachinformatiker Anwendungsentwicklung (IHK) am CBW Hamburg.

## Technisches Setup

- **Sprache:** Python 3.10+
- **Externe Pakete:** `Pillow` optional (für PNG-Logo in der Sidebar, Fallback auf Canvas-Logo)
- **Starten:** `python main.py`
- **Testdaten laden:** Import CSV → `data/booklist.csv`

## Projektstruktur

```
main.py           → App-Klasse FlashMobApp (erbt von tk.Tk), verbindet alles;
                    _on_quit() fragt bei ungespeicherten Änderungen nach
menuMod.py        → Sidebar: Logo, Menü-Labels, Hover/Klick-Effekte, Quit
menuActions.py    → Content-Bereich: alle action_*()-Methoden, Treeview, Dialoge,
                    Eingabe-Validierung, _build_datensatz_dialog (Insert + Edit)
theme.py          → zentrale Farb-/Schrift-Konstanten (FARBE_*, SCHRIFT_*)

library/
  __init__.py     → Package-Marker
  configMod.py    → Konfiguration (os.path.abspath(__file__) für portable Pfade),
                    JSON wird gecacht
  listclassMod.py → Klasse Listclass: Daten, Pickle, CSV, sort, filter,
                    edit_list (@timestamp_decorator), next_free
  editMod.py      → Eingabe-Validierung (DIGIT, ALPHA, ALNUM, FLOAT, ALL);
                    check_item() wird von menuActions.py aufgerufen
  ioMod.py        → Sicheres Öffnen von Dateien (mit newline-Parameter für CSV)

config/
  FlashMob.ini    → Dateipfade ([Paths])
  books.json      → Spalten, Prompts, Validierungsregeln (format_specs)

data/
  booklist.dat    → Pickle-Speicherdatei (wird beim ersten Speichern erzeugt)
  booklist.csv    → Beispieldaten (5 Bücher)

logo.png          → App-Logo (optional, Canvas-Fallback wenn nicht vorhanden)
```

## Architektur

### Drei-Schichten-Modell
```
main.py (FlashMobApp : tk.Tk)
   ├── menuMod.py      → Sidebar aufbauen, Klicks an Callbacks weiterleiten
   └── menuActions.py  → Content-Bereich steuern, Dialoge öffnen
          └── library/ → Datenlogik (unabhängig von der GUI)
```

### Datenhaltung
- `self._list` in `Listclass` — 2D-Liste, jede innere Liste = ein Datensatz
- Persistenz: Python `pickle` (binär), CSV für Import/Export
- Konfiguration: `FlashMob.ini` für Pfade, `books.json` für Einstellungen

### GUI-Aufbau
- Sidebar (links, 200 px fest): `MenuModule` in `menuMod.py`
- Content-Bereich (rechts, wächst): `MenuActions` in `menuActions.py`
- Titelzeile + Statusanzeige bleiben dauerhaft — nur `_arbeitsbereich` wird geleert

## Wichtige Konzepte im Projekt

- **Vererbung:** `FlashMobApp(tk.Tk)` — App-Klasse erbt das Hauptfenster
- **Callbacks:** Funktionsreferenzen (ohne Klammern) an Menüpunkte binden
- **Late-Binding-Lösung:** `lambda c=ch, btn=b: ...` in Schleifen (26 Buchstaben-Buttons)
- **@property / @setter:** `is_modified` in `Listclass`
- **@timestamp_decorator:** automatischer Zeitstempel bei `Listclass.edit_list()`,
  aufgerufen aus der GUI-Aktion "Edit"
- **Lambda-Transfer:** `sort_by_title()` und `filter_by_title_letter()` direkt aus Klausur übertragen
- **Pfad-Portabilität:** `os.path.dirname(os.path.abspath(__file__))` in `configMod.py`

## Kommentierungsstil

Alle Dateien sind **anfänger- und unterrichtsfreundlich** auf Deutsch kommentiert.
Jedes Python-Konzept (tkinter-Widgets, Callbacks, Lambda, Decorator, Property …)
wird an der Stelle erklärt, wo es verwendet wird.
Kommentare bei neuen Funktionen im gleichen Stil weiterführen.

## Benutzer-Kontext

- **Name:** Marius Bonath
- **GitHub:** github.com/MariusBonath
- **Zweck:** Portfolio-Projekt für Praktikumsbewerbung als Fachinformatiker AE
- **Niveau:** Umschüler, ca. 1 Jahr Python-Erfahrung
- **Sprache:** Deutsch bevorzugt (Code-Kommentare, Erklärungen, Commit-Messages)

## Konventionen

- Variablennamen auf Deutsch (z.B. `eingabe`, `spalten_var`, `aktiver_btn`)
- Farb-Konstanten in GROSSBUCHSTABEN mit Präfix `FARBE_`
- Schrift-Konstanten mit Präfix `SCHRIFT_`
- Docstrings auf Deutsch mit Args / Returns
- Keine Übertreibungen bei Kompetenzen — realistisch und ehrlich bleiben
- Neue Features nur wenn sie dem aktuellen Ausbildungsstand entsprechen

## Bekannte Einschränkungen

- `self.lco._list` wird von `menuActions.py` direkt zugegriffen (Kapselungsbruch)
  → bewusst so gelassen, da eine Getter-Methode den Lernaufwand erhöhen würde
- `Listclass.check_number()` wird von der GUI nicht mehr benutzt (Edit/Delete
  arbeiten über `tree.index()`), bleibt aber als eigenständige Suchmethode erhalten
- Sortieren nach `price` sortiert die Werte als Text ("100" < "15"), nicht numerisch
  → für den aktuellen Ausbildungsstand ok, ließe sich mit einer Typ-Konvertierung
    im Sortier-Lambda lösen
- CSV-Import/-Export verwenden die Kopfzeile aus `books.json` (Kleinbuchstaben);
  eine importierte Datei mit anderer Schreibweise wird trotzdem akzeptiert
