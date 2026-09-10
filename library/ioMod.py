# =============================================================================
# library/ioMod.py – Datei-Ein-/Ausgabe-Hilfsmodul
# =============================================================================
#
# Dieses Modul enthält eine einzige Funktion: fopen().
# Sie öffnet eine Datei sicher – auch wenn das Zielverzeichnis
# noch nicht existiert.
#
# Warum ein eigenes Modul?
#   Alle anderen Module (listclassMod, configMod) rufen io.fopen() auf.
#   Fehlerbehandlung beim Öffnen von Dateien ist damit zentral geregelt
#   und muss nicht in jeder Datei neu geschrieben werden.
#
# Konzepte in dieser Datei:
#   - import os        (Betriebssystem-Funktionen)
#   - try / except     (Fehlerbehandlung)
#   - Spezifische Ausnahmen: FileNotFoundError, OSError
#   - os.path-Funktionen (dirname, isdir)
#   - os.makedirs()    (Verzeichnis anlegen)
#   - Bedingte Ausdrücke (Ternary: ... if ... else ...)
# =============================================================================

import os


def fopen(fpath: str, mode: str, newline=None):
    """
    Öffnet eine Datei sicher und gibt das Datei-Objekt zurück.

    Falls das Verzeichnis noch nicht existiert, wird es automatisch angelegt.
    Bei einem nicht behebbaren Fehler wird None zurückgegeben.

    Dateimodi (mode):
        "rb"  → Lesen,     binär  (Pickle laden)
        "wb"  → Schreiben, binär  (Pickle speichern)
        "rt"  → Lesen,     Text   (CSV lesen)
        "w"   → Schreiben, Text   (CSV schreiben)

    Args:
        fpath:   Dateipfad als String, z. B. "data/booklist.dat"
        mode:    Öffnungsmodus als String
        newline: Nur im Textmodus relevant. Das csv-Modul verlangt
                 newline="" – sonst entstehen unter Windows leere Zeilen
                 zwischen den Datensätzen. Im Binärmodus wird der Wert
                 ignoriert (dort ist newline nicht erlaubt).

    Returns:
        Ein geöffnetes Datei-Objekt, oder None bei einem Fehler.
    """

    # os.path.dirname() extrahiert den Ordner-Teil aus einem Dateipfad.
    # Beispiel: "data/booklist.dat"  →  "data"
    dirname = os.path.dirname(fpath)

    # Im Binärmodus darf newline nicht an open() übergeben werden.
    text_newline = newline if "b" not in mode else None

    # -------------------------------------------------------------------------
    # Erster Öffnungsversuch – Normalfall: Datei existiert bereits
    # -------------------------------------------------------------------------
    # "b" not in mode prüft, ob Textmodus vorliegt.
    # Bei Textmodus (rt, w) → encoding="utf-8" für korrekte Umlaute (ä, ö, ü).
    # Bei Binärmodus (rb, wb) → encoding darf NICHT angegeben werden.
    try:
        return open(fpath, mode,
                    encoding="utf-8" if "b" not in mode else None,
                    newline=text_newline)

    except FileNotFoundError:
        # ---------------------------------------------------------------------
        # Datei oder Verzeichnis nicht gefunden
        # ---------------------------------------------------------------------
        # Beim LESEN ist eine fehlende Datei ein Normalfall (z. B. der erste
        # Programmstart, bevor je gespeichert wurde). Kein Fehlertext –
        # einfach None zurückgeben, der Aufrufer startet dann mit leerer Liste.
        if "r" in mode:
            return None

        # Beim SCHREIBEN: fehlendes Verzeichnis anlegen und nochmal versuchen.
        if dirname and not os.path.isdir(dirname):
            # os.makedirs legt alle fehlenden Unterordner auf einmal an.
            # exist_ok=True → kein Fehler, wenn der Ordner doch schon existiert
            os.makedirs(dirname, exist_ok=True)
            print(f"Verzeichnis angelegt: {dirname}")

        # Zweiter Versuch nach dem Anlegen des Verzeichnisses
        try:
            return open(fpath, mode,
                    encoding="utf-8" if "b" not in mode else None,
                    newline=text_newline)
        except OSError as e:
            # OSError deckt weitere Fehler ab (z. B. keine Schreibrechte)
            print(f"Fehler beim Öffnen von '{fpath}': {e}")
            return None

    except OSError as e:
        # Anderer Betriebssystemfehler beim ersten Versuch
        print(f"Fehler beim Öffnen von '{fpath}': {e}")
        return None
