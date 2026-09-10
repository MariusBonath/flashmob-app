# =============================================================================
# library/configMod.py – Konfigurationsmodul
# =============================================================================
#
# Dieses Modul liest alle Programmeinstellungen aus zwei Dateien:
#
#   config/FlashMob.ini   → Dateipfade (wo liegen die Daten?)
#   config/books.json     → Spaltenköpfe, Eingabeaufforderungen, Validierung
#
# Besonderheit gegenüber dem Book Manager (CLI-Version):
#   Der Pfad wird hier relativ zur Position DIESER Datei berechnet
#   (os.path.abspath(__file__)). Das stellt sicher, dass das Programm
#   aus JEDEM Verzeichnis heraus gestartet werden kann – nicht nur aus
#   dem Projektordner selbst.
#
# Konzepte in dieser Datei:
#   - import json, os, configparser (Standardbibliotheken)
#   - os.path.abspath(__file__)   (absoluter Pfad dieser Datei)
#   - os.path.dirname()           (Verzeichnis extrahieren)
#   - os.path.join()              (Pfade plattformunabhängig zusammenbauen)
#   - ConfigParser                (.ini-Dateien lesen)
#   - with open() as f:           (Datei sicher öffnen und schließen)
#   - json.load()                 (JSON-Datei in Python-Dictionary umwandeln)
#   - Private Hilfsfunktion (_lade_json)
# =============================================================================

import json
import os
from configparser import ConfigParser


# =============================================================================
# Projektwurzel berechnen
# =============================================================================
#
# __file__  →  absoluter Pfad DIESER Datei
#              z. B. "C:/Projekte/flashmob-app/library/configMod.py"
#
# os.path.abspath(__file__)
#          →  vollständiger, aufgelöster Pfad (keine relativen ".." usw.)
#
# os.path.dirname(...)
#          →  einen Ordner nach oben
#              1× dirname: "C:/Projekte/flashmob-app/library"   (= library-Ordner)
#              2× dirname: "C:/Projekte/flashmob-app"           (= Projektwurzel)
#
# Ergebnis: _PROJEKTWURZEL zeigt immer auf den Hauptordner des Projekts,
#           egal von wo aus Python gestartet wurde.

_PROJEKTWURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pfad zur .ini-Datei zusammensetzen
# os.path.join() verwendet den richtigen Schrägstrich für Windows / Linux / Mac
_INI_PFAD = os.path.join(_PROJEKTWURZEL, "config", "FlashMob.ini")


# =============================================================================
# .ini-Datei einlesen
# =============================================================================
# ConfigParser liest Dateien im Format:
#
#   [Abschnitt]
#   schluessel = wert
#
# Beispiel aus FlashMob.ini:
#   [Paths]
#   fpath = data/booklist.dat
#
# Zugriff: _config["Paths"]["fpath"]  →  "data/booklist.dat"

_config = ConfigParser()
_config.read(_INI_PFAD)


# =============================================================================
# Private Hilfsfunktion
# =============================================================================

# Zwischenspeicher (Cache): Jede JSON-Datei wird nur EINMAL von der Festplatte
# gelesen. Ohne diesen Cache würde jede der get_*()-Funktionen die Datei erneut
# öffnen und neu parsen (6× pro Programmstart).
_json_cache: dict[str, dict] = {}


def _lade_json(pfad_json: str) -> dict:
    """
    Öffnet eine JSON-Datei und gibt ihren Inhalt als Python-Dictionary zurück.

    Das Ergebnis wird zwischengespeichert – ein zweiter Aufruf mit demselben
    Pfad liest die Datei nicht erneut, sondern gibt den gemerkten Wert zurück.

    JSON sieht so aus:
        {
            "header": ["no", "title", "author"],
            "col_widths": [6, 25, 25]
        }

    Python wandelt das automatisch in ein Dictionary (dict) um.

    Args:
        pfad_json: Vollständiger Pfad zur JSON-Datei.

    Returns:
        Ein Python-Dictionary mit allen Einstellungen.
    """
    if pfad_json not in _json_cache:
        with open(pfad_json, encoding="utf-8") as f:
            _json_cache[pfad_json] = json.load(f)
    return _json_cache[pfad_json]


# =============================================================================
# Öffentliche Funktionen – Dateipfade
# =============================================================================
# os.path.join(_PROJEKTWURZEL, ...) baut einen vollständigen absoluten Pfad.
# Dadurch funktioniert das Programm unabhängig vom Startverzeichnis.

def get_fpath() -> str:
    """
    Gibt den vollständigen Pfad zur Pickle-Datei (.dat) zurück.
    Dort werden die Bücherdaten dauerhaft gespeichert.
    """
    return os.path.join(_PROJEKTWURZEL, _config["Paths"]["fpath"])


def get_fpath_csv() -> str:
    """
    Gibt den Standard-Exportpfad für CSV-Dateien zurück.
    """
    return os.path.join(_PROJEKTWURZEL, _config["Paths"]["fpath_csv"])


def get_fpath_json() -> str:
    """
    Gibt den vollständigen Pfad zur JSON-Konfigurationsdatei zurück.
    """
    return os.path.join(_PROJEKTWURZEL, _config["Paths"]["fpath_json"])


# =============================================================================
# Öffentliche Funktionen – Einstellungen aus der JSON-Datei
# =============================================================================

def get_prompts(pfad_json: str) -> list:
    """
    Gibt die Eingabeaufforderungen für jedes Feld zurück.
    Beispiel: ["Bitte Nr. eingeben: ", "Bitte Titel eingeben: ", ...]
    """
    return _lade_json(pfad_json)["prompts"]


def get_header(pfad_json: str) -> list:
    """
    Gibt die Spaltenüberschriften zurück.
    Beispiel: ["no", "title", "genre", "author", "price", "date"]
    """
    return _lade_json(pfad_json)["header"]


def get_col_widths(pfad_json: str) -> list:
    """
    Gibt die Spaltenbreiten für die Tabellenanzeige zurück.
    Beispiel: [6, 25, 6, 25, 10, 8]
    """
    return _lade_json(pfad_json)["col_widths"]


def get_format_specs(pfad_json: str) -> list:
    """
    Gibt die Validierungsregeln für die Texteingabe zurück.
    Beispiel: [["DIGIT"], ["ALL"], ["ALNUM", "-"], ["FLOAT"], ["DIGIT"]]

    Schlüsselwörter:
        "DIGIT" → nur Ziffern (0–9)
        "ALPHA" → nur Buchstaben + Sonderzeichen aus der Liste
        "ALNUM" → Buchstaben und Ziffern + Sonderzeichen
        "FLOAT" → gültige Dezimalzahl (z. B. "12.99")
        "ALL"   → beliebige Eingabe erlaubt
    """
    return _lade_json(pfad_json)["format_specs"]
