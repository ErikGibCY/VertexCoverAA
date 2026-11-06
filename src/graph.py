"""
graph.py
---------
Estructura de datos de grafo no dirigido para el problema de Cobertura de
Vértices, usada para representar la topología de una red (routers = vértices,
enlaces = aristas).

Representación interna: lista de adyacencia (diccionario de conjuntos), elegida
por simplicidad, porque permite:
  - obtener el grado de un vértice en O(1)
  - iterar vecinos en O(deg(v))
  - insertar/eliminar aristas en O(1) amortizado

Formato de archivo de instancia (JSON):
{
    "name": "example_small",
    "description": "Mini-red de 6 routers (ver Avance 1)",
    "vertices": ["A", "B", "C", "D", "E", "F"],
    "edges": [["A","B"], ["A","C"], ["A","D"], ["B","C"], ["D","E"], ["E","F"]]
}
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable, Hashable


class InvalidInstanceError(ValueError):
    """Excepcion lanzada cuando una instancia no cumple el formato esperado o es invalida."""


class Graph:
    """Grafo no dirigido y no ponderado basado en listas de adyacencia."""

    def __init__(self, vertices: Iterable[Hashable] = (), edges: Iterable[tuple] = ()):
        self._adj: dict[Hashable, set] = {v: set() for v in vertices}
        for u, v in edges:
            self.add_edge(u, v)

    # ---------- construcción ----------
    def add_vertex(self, v: Hashable) -> None:
        self._adj.setdefault(v, set())

    def add_edge(self, u: Hashable, v: Hashable) -> None:
        if u == v:
            raise ValueError(f"No se permiten auto-ciclos: ({u}, {v})")
        self.add_vertex(u)
        self.add_vertex(v)
        self._adj[u].add(v)
        self._adj[v].add(u)

    def remove_edge(self, u: Hashable, v: Hashable) -> None:
        self._adj[u].discard(v)
        self._adj[v].discard(u)

    # ---------- consultas ----------
    @property
    def vertices(self) -> set:
        return set(self._adj.keys())

    @property
    def edges(self) -> set[tuple]:
        seen = set()
        result = []
        for u in self._adj:
            for v in self._adj[u]:
                key = frozenset((u, v))
                if key not in seen:
                    seen.add(key)
                    result.append((u, v))
        return set(result)

    def neighbors(self, v: Hashable) -> set:
        return set(self._adj.get(v, set()))

    def degree(self, v: Hashable) -> int:
        return len(self._adj.get(v, set()))

    def num_vertices(self) -> int:
        return len(self._adj)

    def num_edges(self) -> int:
        return len(self.edges)

    def density(self) -> float:
        """Calcula la densidad de aristas del grafo: 2|E| / (|V|(|V|-1))."""
        n = self.num_vertices()
        if n <= 1:
            return 0.0
        return (2.0 * self.num_edges()) / (n * (n - 1))

    def is_edge(self, u: Hashable, v: Hashable) -> bool:
        return v in self._adj.get(u, set())

    def copy(self) -> "Graph":
        g = Graph()
        g._adj = {v: set(neigh) for v, neigh in self._adj.items()}
        return g

    def __repr__(self) -> str:
        return f"Graph(|V|={self.num_vertices()}, |E|={self.num_edges()})"

    # ---------- I/O y validación de instancias ----------
    @classmethod
    def validate_instance_data(cls, data: dict) -> None:
        """Valida que los datos de una instancia cumplan el esquema esperado."""
        if not isinstance(data, dict):
            raise InvalidInstanceError("La instancia JSON debe ser un objeto/diccionario.")
        if "edges" not in data:
            raise InvalidInstanceError("Falta la clave requerida 'edges' en la instancia JSON.")
        if not isinstance(data["edges"], (list, tuple)):
            raise InvalidInstanceError("La clave 'edges' debe ser una lista de pares de vertices.")

        vertices_in_list = set()
        if "vertices" in data:
            if not isinstance(data["vertices"], (list, tuple)):
                raise InvalidInstanceError("La clave 'vertices' debe ser una lista.")
            for v in data["vertices"]:
                if not isinstance(v, Hashable):
                    raise InvalidInstanceError(f"El vertice {v!r} no es hashable.")
                vertices_in_list.add(v)

        for idx, edge in enumerate(data["edges"]):
            if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                raise InvalidInstanceError(
                    f"Arista invalida en posicion {idx}: debe ser un par [u, v], recibido: {edge!r}"
                )
            u, v = edge
            if not isinstance(u, Hashable) or not isinstance(v, Hashable):
                raise InvalidInstanceError(f"Los extremos de la arista {edge!r} deben ser hashables.")
            if u == v:
                raise InvalidInstanceError(f"No se permiten auto-ciclos: ({u}, {v}) en arista {idx}.")

    @classmethod
    def from_json(cls, path: str | Path) -> "Graph":
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"No se encontro el archivo de instancia: {path}")

        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise InvalidInstanceError(f"El archivo no tiene codificacion UTF-8 valida: {exc}") from exc

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise InvalidInstanceError(f"Error de sintaxis JSON en el archivo '{path}': {exc}") from exc

        cls.validate_instance_data(data)

        g = cls(vertices=data.get("vertices", []))
        for u, v in data["edges"]:
            g.add_edge(u, v)
        return g

    def to_dict(self, name: str = "instance", description: str = "") -> dict:
        return {
            "name": name,
            "description": description,
            "vertices": sorted(self.vertices, key=str),
            "edges": [list(e) for e in sorted(self.edges, key=lambda e: tuple(sorted(map(str, e))))],
        }

    def save_json(self, path: str | Path, name: str = "instance", description: str = "") -> None:
        data = self.to_dict(name, description)
        vertices_json = json.dumps(data["vertices"], ensure_ascii=False)
        edges_json = ",\n    ".join(json.dumps(e, ensure_ascii=False) for e in data["edges"])
        text = (
            "{\n"
            f'  "name": {json.dumps(data["name"], ensure_ascii=False)},\n'
            f'  "description": {json.dumps(data["description"], ensure_ascii=False)},\n'
            f'  "vertices": {vertices_json},\n'
            f'  "edges": [\n    {edges_json}\n  ]\n'
            "}\n"
        )
        Path(path).write_text(text, encoding="utf-8")

    # ---------- generadores de instancias sintéticas ----------
    @staticmethod
    def random_graph(n: int, p: float, seed: int | None = None) -> "Graph":
        """Modelo Erdos-Renyi G(n, p): red aleatoria simple para pruebas de escala."""
        rng = random.Random(seed)
        g = Graph(vertices=range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    g.add_edge(i, j)
        return g

    @staticmethod
    def barabasi_albert(n: int, m: int, seed: int | None = None) -> "Graph":
        """
        Modelo Barabasi-Albert simplificado: genera hubs de alto grado, similar
        a una topología de red backbone con routers concentradores.
        """
        rng = random.Random(seed)
        if m < 1 or m >= n:
            raise ValueError("Se requiere 1 <= m < n")
        g = Graph(vertices=range(n))
        targets = list(range(m))
        repeated_nodes = []
        for i in range(m):
            for j in range(i + 1, m):
                g.add_edge(i, j)
        for new_node in range(m, n):
            for target in targets:
                g.add_edge(new_node, target)
            repeated_nodes.extend(targets)
            repeated_nodes.extend([new_node] * m)
            targets = list(set(rng.sample(repeated_nodes, m)))
        return g
