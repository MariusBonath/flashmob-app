# =============================================================================
# library/editMod.py – Eingabe und Validierung
# =============================================================================
#
# Dieses Modul prüft Nutzereingaben anhand konfigurierbarer Regeln.
#
# In der GUI-Version (FlashMobApp) werden die Eingaben über Textfelder
# (tk.Entry) erfasst, nicht über das Terminal. Deshalb:
#   - check_item() wird von menuActions.py aufgerufen, um die Formulare
#     "Insert" und "Edit" zu validieren (Preis = Zahl, Nr. = Ziffern, ...).
#   - edit_item() ist die Terminal-Variante (fragt so lange nach, bis die
#     Eingabe gültig ist) und wird von der GUI NICHT benötigt. Sie bleibt
#     erhalten, falls Teile des Programms im Terminal laufen sollen.
#
# Konzepte in dieser Datei:
#   - Funktionen mit Rückgabewert
#   - try / except ValueError    (Fehlerbehandlung bei Konvertierung)
#   - String-Methoden: .isdigit(), .isalpha(), .isalnum(), .upper(), .strip()
#   - for-Schleifen (zeichenweise Prüfung)
#   - Typ-Annotationen (str, list, bool)
# =============================================================================


def _ist_dezimalzahl(wert: str) -> bool:
    """
    Prüft, ob ein String als Dezimalzahl (float) interpretiert werden kann.

    Beispiele:
        "12.99"  → True    "abc"   → False
        "100"    → True    "12,99" → False  (Komma statt Punkt)

    Args:
        wert: Der zu prüfende String.

    Returns:
        True wenn konvertierbar, sonst False.
    """
    try:
        float(wert)
        return True
    except ValueError:
        # ValueError: float() konnte den String nicht umwandeln
        return False


def check_item(eingabe: str, format_spec: list) -> bool:
    """
    Prüft, ob eine Eingabe der angegebenen Validierungsregel entspricht.

    Aufbau von format_spec:
        Erstes Element  = Schlüsselwort (Regel)
        Weitere Elemente = zusätzlich erlaubte Sonderzeichen

    Beispiele:
        ["DIGIT"]             → nur Ziffern
        ["ALPHA", " ", "-"]   → Buchstaben + Leerzeichen + Bindestrich
        ["FLOAT"]             → muss Dezimalzahl sein
        ["ALL"]               → alles erlaubt

    Args:
        eingabe:     Der eingegebene String.
        format_spec: Validierungsregel als Liste.

    Returns:
        True wenn gültig, False wenn nicht.
    """
    if not eingabe:
        return False

    regel  = format_spec[0]     # z. B. "ALPHA"
    extras = format_spec[1:]    # z. B. [" ", "-", "&"]

    # FLOAT: wird auf den ganzen String geprüft, nicht zeichenweise
    if regel == "FLOAT":
        return _ist_dezimalzahl(eingabe)

    # Zeichenweise Prüfung für alle anderen Regeln
    for zeichen in eingabe:
        if regel == "ALL":
            continue   # alles erlaubt → nächstes Zeichen

        elif regel == "DIGIT" and zeichen.isdigit():
            continue   # isdigit() → True für "0"–"9"

        elif regel == "ALPHA" and (zeichen.isalpha() or zeichen in extras):
            continue   # isalpha() → True für Buchstaben

        elif regel == "ALNUM" and (zeichen.isalnum() or zeichen in extras):
            continue   # isalnum() → True für Buchstaben und Ziffern

        elif zeichen in extras:
            continue   # explizit erlaubtes Sonderzeichen

        else:
            return False   # ungültiges Zeichen gefunden

    return True


def edit_item(prompt: str, format_spec: list) -> str:
    """
    Fordert den Nutzer zur Texteingabe auf (Terminal) und wiederholt
    die Abfrage, bis die Eingabe gültig ist.

    Hinweis: In der GUI-Version wird diese Funktion nicht verwendet –
    dort übernehmen tk.Entry-Felder die Eingabe.
    Sie bleibt für den Fall, dass Teile des Programms im Terminal laufen.

    Sonderfall: "quit()" bricht die Eingabe sofort ab.

    Args:
        prompt:      Anzeigetext (Eingabeaufforderung).
        format_spec: Validierungsregel (siehe check_item).

    Returns:
        Die gültige Eingabe als String, oder "quit()" bei Abbruch.
    """
    while True:
        eingabe = input(prompt).strip()
        if eingabe == "quit()":
            return eingabe
        if check_item(eingabe, format_spec):
            return eingabe
        print(f"  Ungültige Eingabe. Erlaubtes Format: {format_spec}")
