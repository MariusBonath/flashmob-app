# =============================================================================
# theme.py – zentrale Farb- und Schrift-Konstanten
# =============================================================================
#
# Warum eine eigene Datei?
#   Farben und Schriften wurden früher in menuMod.py UND menuActions.py
#   getrennt definiert – mit teils identischen Werten (z. B. FARBE_AKZENT).
#   Das führt schnell dazu, dass die Werte auseinanderlaufen.
#
#   Jetzt gibt es genau EINE Quelle der Wahrheit. Beide Module importieren
#   ihre Konstanten von hier:
#
#       from theme import FARBE_AKZENT, SCHRIFT_TEXT, ...
#
# Farbformat: "#RRGGBB" (Hexadezimal, je 2 Stellen für Rot, Grün, Blau)
# =============================================================================


# -----------------------------------------------------------------------------
# Sidebar (menuMod.py)
# -----------------------------------------------------------------------------
FARBE_HINTERGRUND   = "#13131f"   # Sidebar-Hintergrund (sehr dunkles Blau)
FARBE_LOGO_BG       = "#0d0d18"   # Logo-Bereich (noch dunkler)
FARBE_EINTRAG       = "#13131f"   # normaler Menüeintrag
FARBE_HOVER         = "#2a2a40"   # Menüeintrag bei Maus-drüber
FARBE_AKTIV         = "#3a3a5c"   # aktiver (zuletzt geklickter) Menüeintrag
FARBE_TEXT          = "#c8c8e8"   # normaler Text (helles Blaugrau)
FARBE_TEXT_AKTIV    = "#ffffff"   # aktiver Text (Weiß)
FARBE_AKZENT        = "#7c6af7"   # Akzentfarbe (Lila, für Trennlinien)

FARBE_QUIT_TEXT     = "#f87171"   # "Beenden" (Rot)
FARBE_QUIT_HOVER    = "#2a1a1a"   # "Beenden" bei Maus-drüber (dunkles Rotbraun)

FARBE_LOGO_BUCH     = "#5a4fcf"   # zweites Rechteck des Canvas-Logos
FARBE_LOGO_LINIEN   = "#9d94f5"   # "Seiten"-Linien im Canvas-Logo


# -----------------------------------------------------------------------------
# Content-Bereich (menuActions.py)
# -----------------------------------------------------------------------------
FARBE_CONTENT_BG    = "#f4f4f8"   # Hintergrund des Content-Bereichs
FARBE_HEADER_BG     = "#e8e8f0"   # Titelzeilen-Hintergrund
FARBE_TEXT_DUNKEL   = "#1e1e2e"   # dunkler Text
FARBE_STATUS_OK     = "#2d7a4f"   # Statustext: Erfolg (Grün)
FARBE_STATUS_ERR    = "#c0392b"   # Statustext: Fehler (Rot)
FARBE_WEISS         = "#ffffff"   # Tabellen-Hintergrund

FARBE_BTN_INAKTIV   = "#e0e0ee"   # Buchstaben-Button (nicht ausgewählt)
FARBE_BTN_NEUTRAL   = "#aaaaaa"   # neutraler Button ("Alle anzeigen")
FARBE_TRENNLINIE_HELL = "#ccccdd" # dünne Trennlinie im Content-Bereich


# -----------------------------------------------------------------------------
# Schriften – als Tupel: (Schriftart, Größe) oder (Schriftart, Größe, "bold")
# -----------------------------------------------------------------------------
SCHRIFT_TITEL = ("Segoe UI", 16, "bold")
SCHRIFT_TEXT  = ("Segoe UI", 10)
SCHRIFT_MONO  = ("Consolas", 10)     # Monospace für Tabellendaten
