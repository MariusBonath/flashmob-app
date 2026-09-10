# =============================================================================
# library/__init__.py – Package-Markierungsdatei
# =============================================================================
#
# Diese Datei macht den Ordner "library/" zu einem Python-Package.
#
# Was ist ein Package?
#   Ein Package ist ein Ordner, der mehrere zusammengehörige Module enthält.
#   Damit Python den Ordner als Package erkennt, MUSS diese Datei existieren.
#   Sie darf leer sein – der Inhalt ist optional.
#
# Warum "library"?
#   Die vier Module configMod, editMod, ioMod und listclassMod sind
#   Hilfsbibliotheken ("library"), die sowohl von main.py als auch von
#   menuActions.py verwendet werden.
#   Sie in einem Unterordner zu bündeln hält das Projekt aufgeräumt.
#
# Import-Syntax mit Package:
#   from library import configMod as cfg
#   from library import ioMod as io
#   from library.listclassMod import Listclass
# =============================================================================
