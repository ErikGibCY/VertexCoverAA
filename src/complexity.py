"""
src/complexity.py
-----------------
Módulo formal de análisis de complejidad temporal, espacial y caracterización
de operaciones dominantes para el problema de Cobertura de Vértices (Vertex Cover).
Cumple con los requisitos del Avance 6 y Entrega 2.
"""

from __future__ import annotations

from typing import Dict, Any


COMPLEXITY_DATA: Dict[str, Dict[str, Any]] = {
    "Graph (Listas de Adyacencia)": {
        "tiempo_peor": "O(V + E)",
        "tiempo_promedio": "O(V + E)",
        "costo_amortizado": "O(1) por inserción en set",
        "espacio": "O(V + E)",
        "operacion_dominante": "Inserción / Consulta de vecinos en dict de conjuntos",
        "detalle": "Representación dispersa mediante tabla hash de conjuntos para grados rápidos.",
    },
    "Greedy por Grado (Básico)": {
        "tiempo_peor": "O(V * E)",
        "tiempo_promedio": "O(V * E)",
        "costo_amortizado": "N/A",
        "espacio": "O(V + E)",
        "operacion_dominante": "Recálculo iterativo de grados residuales escaneando aristas",
        "detalle": "En cada iteración busca el vértice de mayor grado entre aristas descubiertas.",
    },
    "Greedy (Cola de Prioridad - Heap)": {
        "tiempo_peor": "O((V + E) log V)",
        "tiempo_promedio": "O((V + E) log V)",
        "costo_amortizado": "O(log V) por extracción/actualización perezosa",
        "espacio": "O(V + E)",
        "operacion_dominante": "Extracción de max-heap con lazy updates y decremento de grados",
        "detalle": "Optimización avanzada con heapq; cada arista se procesa O(1) veces.",
    },
    "Matching Maximal (2-aprox)": {
        "tiempo_peor": "O(V + E)",
        "tiempo_promedio": "O(V + E)",
        "costo_amortizado": "O(1) por arista evaluada",
        "espacio": "O(V + E)",
        "operacion_dominante": "Filtrado lineal de aristas disjuntas e inserción de ambos extremos",
        "detalle": "Garantía formal de aproximación rho <= 2.0x demostrada por emparejamiento maximal.",
    },
    "Fuerza Bruta (Exacto Exhaustivo)": {
        "tiempo_peor": "O(C(V, k*) * E)",
        "tiempo_promedio": "O(2^V * E)",
        "costo_amortizado": "N/A",
        "espacio": "O(V)",
        "operacion_dominante": "Generación combinatoria y verificación exhaustiva de aristas",
        "detalle": "Crecimiento exponencial severo; límite computacional práctico en V <= 18.",
    },
    "ILP Exacto (PuLP / Branch & Cut)": {
        "tiempo_peor": "O(2^V) [NP-difícil]",
        "tiempo_promedio": "Sub-segundo para V <= 100",
        "costo_amortizado": "N/A",
        "espacio": "O(V + E)",
        "operacion_dominante": "Relajación lineal (Simplex) + Ramificación y Poda (Branch and Cut)",
        "detalle": "Modelo de Programación Lineal Entera resuelto con solver CBC escalable.",
    },
}


def get_complexity_table_str() -> str:
    """Retorna una cadena con la tabla comparativa de complejidad formateada."""
    lines = []
    header_sep = "=" * 105
    lines.append(header_sep)
    lines.append(" ANÁLISIS DE COMPLEJIDAD TEÓRICA Y OPERACIONES DOMINANTES (AVANCE 6 / ENTREGA 2)")
    lines.append(header_sep)
    lines.append(
        f"{'Componente / Algoritmo':<34} | {'Peor Caso':<18} | {'Espacial':<10} | {'Operación Dominante'}"
    )
    lines.append("-" * 105)

    for nombre, datos in COMPLEXITY_DATA.items():
        lines.append(
            f"{nombre:<34} | {datos['tiempo_peor']:<18} | {datos['espacio']:<10} | {datos['operacion_dominante']}"
        )

    lines.append(header_sep)
    return "\n".join(lines)


def print_complexity_table() -> None:
    """Imprime en stdout la tabla formal de complejidad."""
    print(get_complexity_table_str())
