"""
Paquete src para Cobertura de Vértices (Vertex Cover).
Exporta clases y funciones principales para modelado, resolución, verificación y análisis.
"""

from .graph import Graph, InvalidInstanceError
from .solver import VertexCoverSolver, ALGORITHMS_REGISTRY
from .verify import is_vertex_cover, approximation_ratio, uncovered_edges
from .complexity import COMPLEXITY_DATA, get_complexity_table_str, print_complexity_table

__all__ = [
    "Graph",
    "InvalidInstanceError",
    "VertexCoverSolver",
    "ALGORITHMS_REGISTRY",
    "is_vertex_cover",
    "approximation_ratio",
    "uncovered_edges",
    "COMPLEXITY_DATA",
    "get_complexity_table_str",
    "print_complexity_table",
]
