# FlashMob – Bücherverwaltung (Desktop-App)

Eine grafische Desktop-Anwendung zur Bücherverwaltung, entwickelt mit Python und tkinter.  
Erstellt im Rahmen meiner **Umschulung zum Fachinformatiker Anwendungsentwicklung (IHK)** am CBW Hamburg.

> **Weiterentwicklung des [Book Manager](https://github.com/MariusBonath/book-manager-python)**  
> Dieselbe Kern-Architektur (Listclass, configMod, ioMod, editMod) –  
> aber mit einer vollständigen grafischen Benutzeroberfläche statt Terminal-Menü.

---

## Inhalt

- [Funktionen](#funktionen)
- [Screenshots / Aufbau](#aufbau-der-oberfläche)
- [Projektstruktur](#projektstruktur)
- [Schnellstart](#schnellstart)
- [Konfiguration](#konfiguration)
- [Technische Konzepte](#technische-konzepte)
- [Lambda-Transfer aus der Klausur](#lambda-transfer-aus-der-klausur)

---

## Funktionen

| Menüpunkt | Beschreibung |
|-----------|--------------|
| **Show** | Alle Bücher als formatierte Tabelle (Treeview) |
| **Edit** | Eintrag auswählen und in einem Dialogfenster bearbeiten (mit Eingabeprüfung, automatischer Änderungs-Zeitstempel) |
| **Save** | Daten dauerhaft als Pickle-Datei speichern |
| **Sort** | Nach beliebiger Spalte sortieren **oder** nach Anfangsbuchstaben filtern (A–Z Buttons) |
| **Export CSV** | Alle Einträge über einen nativen Speichern-Dialog als CSV exportieren |
| **Import CSV** | CSV-Datei über einen nativen Öffnen-Dialog importieren (mit Spaltenprüfung) |
| **Insert** | Neuen Eintrag in einem Formular-Dialog erfassen (mit Eingabeprüfung) |
| **Delete** | Eintrag auswählen und nach Bestätigung löschen |

Beim Beenden fragt die App nach, wenn es ungespeicherte Änderungen gibt.

---

## Aufbau der Oberfläche

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo]            │  FlashMob – Bücherliste      5 Einträge│
│  ─────────────     │  ─────────────────────────────────────  │
│  Edit              │  No  │ Title           │ Genre │ ...    │
│  Show  ←aktiv      │  001 │ Dracula         │ 007   │ ...    │
│  Save              │  002 │ Pippi L.        │ 005   │ ...    │
│  Sort              │  ...                                    │
│  Export CSV        │                                         │
│  Import CSV        │                                         │
│  Insert            │                                         │
│  Delete            │                                         │
│                    │                                         │
│  ⏻ Beenden         │                                         │
└─────────────────────────────────────────────────────────────┘
  Sidebar (200 px)    Content-Bereich (wächst mit Fenster)
```

---

## Projektstruktur

```
flashmob-app/
│
├── main.py            # Einstiegspunkt: App-Klasse (erbt von tk.Tk)
├── menuMod.py         # Sidebar-Widget: Logo, Menü-Labels, Quit-Button
├── menuActions.py     # Aktionen hinter den Menüpunkten (Treeview, Dialoge)
├── theme.py           # zentrale Farb- und Schrift-Konstanten
├── logo.png           # App-Logo (optional, Canvas-Fallback wenn nicht gefunden)
│
├── library/           # Python-Package mit der Kern-Logik
│   ├── __init__.py    # Package-Marker (macht library/ zum importierbaren Package)
│   ├── configMod.py   # Konfiguration aus .ini und .json laden
│   ├── listclassMod.py# Listclass: Daten, Sortieren, Filtern, Pickle, CSV
│   ├── editMod.py     # Eingabe-Validierung (DIGIT, ALPHA, FLOAT, ...)
│   └── ioMod.py       # Sicheres Öffnen von Dateien
│
├── config/
│   ├── FlashMob.ini   # Dateipfade
│   └── books.json     # Spalten, Prompts, Validierungsregeln
│
└── data/
    ├── booklist.dat   # Pickle-Datei (beim ersten Speichern erzeugt)
    └── booklist.csv   # Beispieldaten (5 Bücher)
```

### Architektur (Schichten)

```
main.py  (FlashMobApp : tk.Tk)
   │
   ├── theme.py        → Farben & Schriften (von menuMod + menuActions genutzt)
   │
   ├── menuMod.py      → Sidebar aufbauen, Klicks weiterleiten
   │
   ├── menuActions.py  → Content-Bereich steuern, Dialoge öffnen
   │      ├── library/listclassMod.py  → Datenoperationen
   │      └── library/editMod.py       → Eingabe-Validierung der Formulare
   │
   └── library/
          ├── configMod.py   → Konfiguration laden
          ├── listclassMod.py→ Listclass (Kern-Datenklasse)
          ├── editMod.py     → Validierung (check_item)
          └── ioMod.py       → Datei-I/O
```

---

## Schnellstart

**Voraussetzung:** Python 3.10 oder neuer, keine externen Pakete nötig.  
*(Optional: `pip install Pillow` für das PNG-Logo in der Sidebar)*

```bash
# Repository klonen
git clone https://github.com/MariusBonath/flashmob-app.git
cd flashmob-app

# Starten
python main.py
```

### Erste Schritte

1. **Import CSV** klicken → Datei `data/booklist.csv` auswählen → 5 Beispielbücher laden
2. **Show** klicken → Bücherliste anzeigen
3. **Save** klicken → Daten dauerhaft speichern

---

## Konfiguration

Das Programm ist ohne Code-Änderungen anpassbar.

### `config/FlashMob.ini` – Dateipfade

```ini
[Paths]
fpath      = data/booklist.dat     ; Pickle-Speicherdatei
fpath_csv  = data/booklist.csv     ; Standard-CSV-Pfad
fpath_json = config/books.json     ; JSON-Konfiguration
```

### `config/books.json` – Spalten und Validierung

```json
{
  "header":      ["no", "title", "genre", "author", "price", "date"],
  "col_widths":  [6, 25, 6, 25, 10, 8],
  "prompts":     ["Bitte Nr. eingeben: ", "Bitte Titel eingeben: ", ...],
  "format_specs": [
    ["DIGIT"], ["ALL"], ["ALNUM", "-"],
    ["ALPHA", " ", "-", "&", ".", "'"],
    ["FLOAT"], ["DIGIT"]
  ]
}
```

---

## Technische Konzepte

### Grafische Benutzeroberfläche (tkinter)

| Konzept | Wo | Erklärung |
|---|---|---|
| `tk.Tk` als Basisklasse | `main.py` | `FlashMobApp` erbt vom Hauptfenster |
| `tk.Frame` | überall | Unsichtbarer Container zum Anordnen von Widgets |
| `tk.Label` | `menuMod.py` | Text oder Bild anzeigen |
| `tk.Button` | `menuActions.py` | Klickbarer Button |
| `tk.Entry` | `menuActions.py` | Einzeiliges Texteingabefeld |
| `ttk.Treeview` | `menuActions.py` | Mehrspaltige Tabelle mit Scrollbar |
| `ttk.Combobox` | `menuActions.py` | Dropdown-Auswahlfeld |
| `tk.Toplevel` | `menuActions.py` | Modales Dialogfenster |
| `messagebox` | `menuActions.py` | Systemeigener Ja/Nein-Dialog |
| `filedialog` | `menuActions.py` | Systemeigener Datei-Dialog |
| `pack` / `grid` | überall | Layout-Manager zum Anordnen von Widgets |
| `.bind()` | überall | Ereignisse an Widgets binden |

### Objektorientierung

- **Vererbung:** `FlashMobApp(tk.Tk)` – die App-Klasse erbt alle Fensterfunktionen
- **Kapselung:** Private Methoden (`_build_ui`, `_clear_work`) trennen interne Logik
- **`@property` / `@setter`:** kontrollierter Zugriff auf `is_modified`
- **Decorator:** `@timestamp_decorator` auf `Listclass.edit_list()` – hängt beim
  Bearbeiten automatisch einen Zeitstempel an den Datensatz an (Spalte „Geändert“)

### Callbacks und Events

```
Nutzer klickt "Show"
    → MenuModule._on_click()
        → mapping["Show"]()
            → MenuActions.action_show()
                → Treeview befüllen
```

Callbacks sind Funktionsreferenzen (ohne Klammern), die erst beim Klick aufgerufen werden.

### Late-Binding-Problem und Lösung

```python
# FALSCH – alle Buttons verwenden am Ende denselben Wert von ch
for ch in "ABC":
    btn.configure(command=lambda: on_letter(ch))

# RICHTIG – Default-Argument speichert den aktuellen Wert
for ch in "ABC":
    btn.configure(command=lambda c=ch: on_letter(c))
```

---

## Lambda-Transfer aus der Klausur

In der Klausur (Python 1) wurde Lambda für Sortierung und Filterung eingeführt.  
Diese App demonstriert die direkte Übertragung in ein laufendes Projekt.

### Sortieren nach Titel

```python
# Klausur (mylst_2d mit [Nummer, Name, Alter]):
sorted(mylst_2d, key=lambda row: row[1])   # row[1] = Name

# FlashMob (self._list mit [No., Titel, Genre, Autor, Preis, Jahr]):
sorted(self._list, key=lambda zeile: zeile[1])   # zeile[1] = Titel
```

Das Lambda `lambda zeile: zeile[1]` ist **strukturell identisch** – nur der Kontext ändert sich.

### Filtern nach Anfangsbuchstabe

```python
# Klausur (Alter < 50):
filter(lambda row: row[2] < 50, mylst_2d)

# FlashMob (Titel beginnt mit Buchstabe):
filter(lambda zeile: zeile[1][0].upper() == buchstabe, self._list)
#                           ↑   ↑
#                       Titel  erster Buchstabe
```

Dokumentiert in `library/listclassMod.py`, Methoden `sort_by_title()` und `filter_by_title_letter()`.

---

## Autor

**Marius Bonath**  
Umschulung: Fachinformatiker Anwendungsentwicklung (IHK) · CBW Hamburg · 2025–2027  
GitHub: [github.com/MariusBonath](https://github.com/MariusBonath)
