#!/usr/bin/env python3
"""
demo.py
--------
Prototipo ejecutable e interfaz por consola para la comparación, evaluación y benchmarking
de algoritmos de Cobertura de Vértices (Vertex Cover) aplicados a la ubicación
de sistemas de detección de intrusos (IDS).

Soporta:
  1. Cargar una instancia desde archivo JSON o generar una aleatoria (ER o BA).
  2. Ejecutar de forma unificada:
     - greedy     : Heurística voraz por grado O(V*E)
     - greedy_pq  : Heurística voraz optimizada con cola de prioridad O((V+E)log V)
     - matching   : 2-aproximación por emparejamiento maximal O(V+E)
     - exact      : Exacto por fuerza bruta (para |V| <= 20)
     - ilp        : Exacto escalable por Programación Lineal Entera (PuLP)
     - all        : Ejecuta todos los algoritmos aplicables
  3. Validar automáticamente la cobertura (is_vertex_cover).
  4. Medir tiempo de ejecución (ms) y memoria pico consumida (KiB).
  5. Calcular el ratio de aproximación empírico frente al óptimo (exact / ilp).
  6. Presentar el análisis teórico de complejidad (--complexity).
  7. Ejecutar el protocolo experimental completo con gráficos (--benchmark).
"""

from __future__ import annotations

import argparse
import sys

from src.graph import Graph, InvalidInstanceError
from src.solver import VertexCoverSolver, ALGORITHMS_REGISTRY
from src.verify import approximation_ratio, uncovered_edges
from src.complexity import print_complexity_table


def main():
    parser = argparse.ArgumentParser(
        description="Demo y Benchmarking: Cobertura de Vértices para ubicación de IDS (Avances 1 al 7)"
    )
    parser.add_argument("--instance", type=str, help="Ruta a un archivo JSON de instancia")
    parser.add_argument(
        "--random", nargs=2, type=float, metavar=("N", "P"),
        help="Generar un grafo aleatorio Erdos-Rényi G(n, p)",
    )
    parser.add_argument(
        "--barabasi", nargs=2, type=int, metavar=("N", "M"),
        help="Generar un grafo aleatorio Barabási-Albert (topología backbone)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Semilla para reproducibilidad")
    parser.add_argument(
        "--algorithm",
        choices=["greedy", "greedy_pq", "matching", "exact", "ilp", "all"],
        default="all",
        help="Algoritmo a ejecutar (default: all)",
    )
    parser.add_argument(
        "--complexity", action="store_true", help="Mostrar cuadro formal de análisis de complejidad (Avance 6)"
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Ejecutar protocolo experimental completo y generar gráficos (Avance 6 y 7)"
    )
    args = parser.parse_args()

    # Si se pide mostrar complejidad teórica
    if args.complexity:
        print_complexity_table()
        if not (args.instance or args.random or args.barabasi or args.benchmark):
            return

    # Si se pide ejecutar benchmark completo
    if args.benchmark:
        from experiments.benchmark import run_benchmark
        run_benchmark()
        if not (args.instance or args.random or args.barabasi):
            return

    # Carga o generación de la instancia
    if args.instance:
        try:
            graph = Graph.from_json(args.instance)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except InvalidInstanceError as e:
            print(f"Error de formato en la instancia: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error inesperado al cargar la instancia: {e}", file=sys.stderr)
            sys.exit(1)
        origin = f"instancia '{args.instance}'"
    elif args.random:
        try:
            n, p = int(args.random[0]), float(args.random[1])
            if n < 0 or not (0.0 <= p <= 1.0):
                raise ValueError("Se requiere n >= 0 y 0 <= p <= 1")
            graph = Graph.random_graph(n=n, p=p, seed=args.seed)
            origin = f"grafo aleatorio G({n}, {p}), seed={args.seed}"
        except Exception as e:
            print(f"Error en parámetros de grafo aleatorio: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.barabasi:
        try:
            n, m = args.barabasi[0], args.barabasi[1]
            graph = Graph.barabasi_albert(n=n, m=m, seed=args.seed)
            origin = f"grafo Barabási-Albert(n={n}, m={m}), seed={args.seed}"
        except Exception as e:
            print(f"Error en parámetros Barabási-Albert: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if not (args.complexity or args.benchmark):
            print("Debes indicar --instance <archivo.json>, --random N P, --barabasi N M, --complexity o --benchmark", file=sys.stderr)
            sys.exit(1)
        return

    print("=" * 65)
    print(f"Cargado: {origin}")
    print(f"  |V| = {graph.num_vertices()}   |E| = {graph.num_edges()}   densidad = {graph.density():.4f}")
    print("=" * 65)
    print()

    solver = VertexCoverSolver(graph)
    keys = list(ALGORITHMS_REGISTRY.keys()) if args.algorithm == "all" else [args.algorithm]

    results = {}
    optimal_size = None

    for key in keys:
        if key == "exact" and graph.num_vertices() > 20:
            print(f"[{ALGORITHMS_REGISTRY[key][0]}] omitido: {graph.num_vertices()} vértices > 20 (fuerza bruta no escala)")
            print()
            continue

        try:
            res = solver.solve(key)
        except Exception as e:
            print(f"[{ALGORITHMS_REGISTRY[key][0]}] error: {e}")
            print()
            continue

        results[key] = res
        cover = res["cover"]
        valid = res["valid"]

        if key in ("exact", "ilp") and valid:
            if optimal_size is None or res["size"] < optimal_size:
                optimal_size = res["size"]

        print(f"[{res['label']}]")
        print(f"  Cobertura : {sorted(cover, key=str)}")
        print(f"  Tamaño    : {res['size']}")
        print(f"  Válida    : {'SÍ' if valid else 'NO -- aristas sin cubrir: ' + str(uncovered_edges(graph, cover))}")
        print(f"  Tiempo    : {res['time_ms']:.3f} ms")
        print(f"  Memoria   : {res['memory_kib']:.2f} KiB")
        print()

    # Ratios de aproximación frente al óptimo
    if optimal_size is not None:
        print("-" * 65)
        print(f"Óptimo de referencia: {optimal_size} vértices")
        print("Ratios de aproximación frente al óptimo:")
        for key, res in results.items():
            if key in ("exact", "ilp"):
                continue
            ratio = approximation_ratio(res["size"], optimal_size)
            print(f"  {res['label']:<32}: {ratio:.3f}x")
        print("-" * 65)


if __name__ == "__main__":
    main()
