"""
solver.py
----------
VertexCoverSolver: implementa los algoritmos a comparar para el problema de
Cobertura de Vertices.

    1. greedy_degree_vertex_cover   -> heuristica voraz por grado
    2. maximal_matching_vertex_cover -> 2-aproximacion con garantia formal
    3. exact_vertex_cover_bruteforce -> solucion de referencia (optima),
       solo para instancias pequenas (|V| <= ~20)

Las dos primeras siguen el pseudocodigo acordado en el Avance 1.
"""

from __future__ import annotations

from itertools import combinations
from typing import Hashable
import heapq
import time
import tracemalloc

from .graph import Graph
from .verify import is_vertex_cover


ALGORITHMS_REGISTRY = {
    "greedy": ("Greedy por grado", "greedy_degree_vertex_cover"),
    "greedy_pq": ("Greedy (cola de prioridad)", "greedy_priority_queue_vertex_cover"),
    "matching": ("Matching maximal (2-aprox)", "maximal_matching_vertex_cover"),
    "exact": ("Exacto (fuerza bruta)", "exact_vertex_cover_bruteforce"),
    "ilp": ("Exacto (ILP / PuLP)", "exact_vertex_cover_ilp"),
}


class VertexCoverSolver:
    def __init__(self, graph: Graph):
        self.graph = graph

    def _sorted_edges(self) -> list[tuple]:
        """
        Devuelve las aristas en un orden canonico y deterministico.

        Python aleatoriza el hash de los strings entre procesos (PYTHONHASHSEED),
        por lo que iterar directamente sobre un set() de aristas produce un
        orden distinto en cada ejecucion. Como el proyecto exige resultados
        reproducibles (instrucciones adicionales, punto 7), tanto el "arbitrario"
        del matching maximal como el desempate del greedy se resuelven siempre
        sobre esta misma lista ordenada.
        """
        canonical = (tuple(sorted((u, v), key=str)) for u, v in self.graph.edges)
        return sorted(canonical, key=lambda e: tuple(map(str, e)))

    # ------------------------------------------------------------------
    # 1. Greedy por grado
    # ------------------------------------------------------------------
    def greedy_degree_vertex_cover(self) -> set:
        """
        En cada paso elige el vertice con mayor numero de aristas incidentes
        entre las aun no cubiertas, lo agrega a la cobertura y elimina esas
        aristas. Repite hasta no tener aristas pendientes. Los empates de
        grado se resuelven por orden canonico (ver `_sorted_edges`), para
        que el resultado sea reproducible.

        Complejidad: O(V * E) en esta implementacion directa (en cada
        iteracion se recorren las aristas restantes para recalcular grados).
        Puede optimizarse a O((V + E) log V) con una cola de prioridad.

        Garantia de aproximacion: ninguna cota fija en el peor caso general,
        pero buen desempeno empirico (ver experiments/compare.py).
        """
        remaining_edges = self._sorted_edges()
        cover: set = set()

        while remaining_edges:
            degree_count: dict[Hashable, int] = {}
            for u, v in remaining_edges:
                degree_count[u] = degree_count.get(u, 0) + 1
                degree_count[v] = degree_count.get(v, 0) + 1

            # max() devuelve el primer elemento de mayor valor segun el
            # orden de iteracion del dict, que aqui es deterministico
            # porque degree_count se construyo a partir de una lista ya
            # ordenada canonicamente.
            best_vertex = max(degree_count, key=degree_count.get)
            cover.add(best_vertex)

            remaining_edges = [
                (u, v) for (u, v) in remaining_edges
                if u != best_vertex and v != best_vertex
            ]

        return cover

    # ------------------------------------------------------------------
    # 1b. Greedy por grado optimizado con Cola de Prioridad (Heap)
    # ------------------------------------------------------------------
    def greedy_priority_queue_vertex_cover(self) -> set:
        """
        Version optimizada del Greedy por grado usando una cola de prioridad (heapq).
        Reduce la complejidad temporal de O(V * E) a O((V + E) log V).

        Estrategia:
        - Mantiene dinamicamente las aristas incidentes no cubiertas por vertice.
        - Utiliza un min-heap con claves negativas (-deg, str(u), u) para simular
          un max-heap de forma determinista y canonica.
        - Emplea actualizacion diferida (lazy update): cuando el grado real en el
          diccionario es menor al extraido del heap, se descarta o reinserta.
        - En cada paso selecciona el vertice de mayor grado respecto a las aristas
          pendientes, lo anade a la cobertura y actualiza a sus vecinos en O(deg(u) log V).
        """
        if not self.graph.edges:
            return set()

        adj_rem: dict[Hashable, set] = {v: set(self.graph.neighbors(v)) for v in self.graph.vertices}
        total_uncovered_edges = self.graph.num_edges()

        # Construir heap inicial: (-grado, str_v, v)
        heap = [(-len(adj_rem[v]), str(v), v) for v in self.graph.vertices if len(adj_rem[v]) > 0]
        heapq.heapify(heap)

        cover: set = set()

        while total_uncovered_edges > 0 and heap:
            neg_deg, _, best_vertex = heapq.heappop(heap)
            current_deg = len(adj_rem[best_vertex])

            # Lazy update: si el grado cambio desde que se encolo
            if -neg_deg != current_deg:
                if current_deg > 0:
                    heapq.heappush(heap, (-current_deg, str(best_vertex), best_vertex))
                continue

            if current_deg == 0:
                continue

            cover.add(best_vertex)
            neighbors = list(adj_rem[best_vertex])

            for neigh in neighbors:
                adj_rem[neigh].discard(best_vertex)
                total_uncovered_edges -= 1
                new_neigh_deg = len(adj_rem[neigh])
                if new_neigh_deg > 0:
                    heapq.heappush(heap, (-new_neigh_deg, str(neigh), neigh))

            adj_rem[best_vertex].clear()

        return cover

    # ------------------------------------------------------------------
    # 2. Matching maximal (2-aproximacion)
    # ------------------------------------------------------------------
    def maximal_matching_vertex_cover(self) -> set:
        """
        Toma una arista arbitraria (u, v), agrega ambos extremos a la
        cobertura y elimina todas las aristas incidentes a u o v. Repite
        hasta agotar las aristas.

        Complejidad: O(V + E).

        Garantia de aproximacion: |cover| <= 2 * |optimo|, porque las
        aristas elegidas forman un matching (no comparten extremos) y toda
        cobertura valida debe incluir al menos un vertice de cada arista
        del matching. La arista "arbitraria" en cada paso se toma siempre
        la primera en el orden canonico (ver `_sorted_edges`), para que el
        resultado sea reproducible entre ejecuciones.
        """
        remaining_edges = self._sorted_edges()
        cover: set = set()

        while remaining_edges:
            u, v = remaining_edges[0]
            cover.add(u)
            cover.add(v)

            remaining_edges = [
                (a, b) for (a, b) in remaining_edges
                if a not in (u, v) and b not in (u, v)
            ]

        return cover

    # ------------------------------------------------------------------
    # 3. Solucion exacta de referencia (fuerza bruta con poda simple)
    # ------------------------------------------------------------------
    def exact_vertex_cover_bruteforce(self, max_vertices: int = 20) -> set:
        """
        Prueba subconjuntos de tamano creciente k = 0, 1, 2, ... hasta
        encontrar el primero que sea una cobertura valida. Garantiza la
        solucion OPTIMA, pero es exponencial: O(C(n, k*) * E) en el peor
        caso, por eso solo se usa como referencia en instancias pequenas.

        Se usa unicamente para validar los algoritmos aproximados en el
        plan de pruebas (Avance 2) y en los experimentos de instancias
        pequenas (Avance 2 / Entrega 2).
        """
        n = self.graph.num_vertices()
        if n > max_vertices:
            raise ValueError(
                f"Instancia demasiado grande para fuerza bruta "
                f"({n} > {max_vertices} vertices). Usar una heuristica o ILP."
            )

        vertices = list(self.graph.vertices)
        edges = self.graph.edges

        if not edges:
            return set()

        for k in range(1, n + 1):
            for subset in combinations(vertices, k):
                candidate = set(subset)
                if all(u in candidate or v in candidate for u, v in edges):
                    return candidate

        return set(vertices)  # caso extremo: el grafo completo es necesario

    # ------------------------------------------------------------------
    # 4. (opcional / Avance 2) Solucion exacta via ILP
    # ------------------------------------------------------------------
    def exact_vertex_cover_ilp(self):
        """
        Formulacion de Programacion Lineal Entera (ILP) usando PuLP, como
        alternativa escalable a la fuerza bruta para instancias algo mas
        grandes (decenas/cientos de vertices, dependiendo del solver).

            minimizar      sum_v x_v
            sujeto a       x_u + x_v >= 1   para toda arista (u, v)
                           x_v in {0, 1}

        Requiere `pip install pulp`. Se deja como componente a completar
        durante el aprendizaje autonomo del indicador AG-C06.02; por ahora
        lanza NotImplementedError si PuLP no esta instalado.
        """
        if not self.graph.edges:
            return set()

        try:
            import pulp
        except ImportError as exc:
            raise NotImplementedError(
                "PuLP no esta instalado. Ejecutar: pip install pulp"
            ) from exc

        prob = pulp.LpProblem("VertexCover", pulp.LpMinimize)
        x = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in self.graph.vertices}

        prob += pulp.lpSum(x.values())
        for u, v in self.graph.edges:
            prob += x[u] + x[v] >= 1

        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        return {v for v, var in x.items() if pulp.value(var) == 1}

    # ------------------------------------------------------------------
    # 5. Interfaz comun de ejecucion unificada (Avance 5)
    # ------------------------------------------------------------------
    def solve(self, algorithm_key: str, **kwargs) -> dict:
        """
        Punto de entrada unificado para ejecutar cualquier algoritmo de cobertura.
        Mide el tiempo de ejecucion en ms, el consumo pico de memoria en KiB,
        y valida formalmente la solucion obtenida mediante `is_vertex_cover`.

        Parametros:
            algorithm_key: clave del algoritmo ('greedy', 'greedy_pq', 'matching', 'exact', 'ilp').

        Retorna:
            dict con las llaves:
                - 'key': clave interna
                - 'label': nombre legible
                - 'cover': conjunto de vertices en la cobertura
                - 'size': cardinalidad de la cobertura
                - 'valid': bool indicando si toda arista quedo cubierta
                - 'time_ms': tiempo de CPU / ejecucion en milisegundos
                - 'memory_kib': memoria pico utilizada en KiB
        """
        if algorithm_key not in ALGORITHMS_REGISTRY:
            raise KeyError(
                f"Algoritmo '{algorithm_key}' desconocido. Disponibles: {list(ALGORITHMS_REGISTRY.keys())}"
            )

        label, method_name = ALGORITHMS_REGISTRY[algorithm_key]
        method = getattr(self, method_name)

        tracemalloc.start()
        start_time = time.perf_counter()

        cover = method(**kwargs)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        cover_set = set(cover)
        valid = is_vertex_cover(self.graph, cover_set)

        return {
            "key": algorithm_key,
            "label": label,
            "cover": cover_set,
            "size": len(cover_set),
            "valid": valid,
            "time_ms": elapsed_ms,
            "memory_kib": peak_bytes / 1024.0,
        }
