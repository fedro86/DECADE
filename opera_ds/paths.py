"""Cartelle di lavoro condivise da script e notebook.

DATA_DIR    : dati scaricati (default <repo>/data, oppure $OPERA_DATA_DIR)
RESULTS_DIR : output di validazione ed esperimenti (default <repo>/results, oppure $OPERA_RESULTS_DIR)
Entrambe sono escluse da git.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("OPERA_DATA_DIR", REPO_DIR / "data"))
RESULTS_DIR = Path(os.environ.get("OPERA_RESULTS_DIR", REPO_DIR / "results"))
