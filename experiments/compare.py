"""
experiments/compare.py
------------------------
Script de compatibilidad para ejecutar el benchmark comparativo experimental.
Redirige la ejecución a la suite integral `experiments.benchmark`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from experiments.benchmark import run_benchmark, print_complexity_table


def print_theoretical_complexity():
    """Imprime el cuadro de complejidad teórica (compatibilidad hacia atrás)."""
    print_complexity_table()


def run_experiment():
    """Ejecuta el protocolo experimental completo."""
    return run_benchmark()


if __name__ == "__main__":
    run_experiment()
