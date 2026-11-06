"""
viz.py
------
Utilidades de visualizacion de grafos y coberturas usando NetworkX y
matplotlib. Se mantiene separado de la logica algoritmica (solver.py,
verify.py) para no mezclar calculo con presentacion.

El modo consola (demo.py) NO depende de este modulo: es una capa opcional
pensada para la interfaz grafica (visualizer.py) y para exportar imagenes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Hashable, Iterable, Mapping, Optional

import networkx as nx
from matplotlib.lines import Line2D

from .graph import Graph

# ---- paleta de colores ----
COLOR_COVERED = "#e4572e"        # vertices dentro de la cobertura
COLOR_UNCOVERED = "#cfe8ff"      # vertices fuera de la cobertura
COLOR_COVERED_EDGE = "#586069"   # aristas cubiertas
COLOR_UNCOVERED_EDGE = "#d62728" # aristas sin cubrir (no deberia haber en una cobertura valida)
COLOR_BASE_EDGE = "#b0b8c1"      # aristas cuando aun no se ejecuto ningun algoritmo
NODE_BORDER = "#22333b"
TEXT_COLOR = "#111111"

LAYOUTS = ("spring", "circular", "kamada", "shell")


def to_networkx(graph: Graph) -> nx.Graph:
    """Convierte un Graph propio a un grafo de NetworkX (solo para dibujar)."""
    g = nx.Graph()
    for v in graph.vertices:
        g.add_node(v)
    for u, v in graph.edges:
        g.add_edge(u, v)
    return g


def compute_layout(
    graph: Graph,
    seed: int = 0,
    layout: str = "spring",
    scale: float = 1.0,
) -> dict:
    """Devuelve posiciones {vertice: (x, y)} para dibujar el grafo."""
    if graph.num_vertices() == 0:
        return {}
    g = to_networkx(graph)
    if layout == "circular":
        return dict(nx.circular_layout(g, scale=scale))
    if layout == "kamada":
        return dict(nx.kamada_kawai_layout(g, scale=scale))
    if layout == "shell":
        return dict(nx.shell_layout(g, scale=scale))
    return dict(nx.spring_layout(g, seed=seed, scale=scale))


def split_edges(graph: Graph, cover: Iterable[Hashable]) -> tuple[list, list]:
    """Separa las aristas en cubiertas / no cubiertas por `cover`."""
    cover_set = set(cover)
    covered: list = []
    uncovered: list = []
    for u, v in graph.edges:
        if u in cover_set or v in cover_set:
            covered.append((u, v))
        else:
            uncovered.append((u, v))
    return covered, uncovered


def draw_graph(
    ax,
    graph: Graph,
    cover: Optional[Iterable[Hashable]] = None,
    positions: Optional[Mapping] = None,
    seed: int = 0,
    layout: str = "spring",
    title: Optional[str] = None,
    show_labels: bool = True,
    scale: float = 1.0,
):
    """
    Dibuja el grafo en el eje `ax`.

    Si `cover` es None no se resalta ninguna cobertura (dibujo neutro).
    Si `cover` se entrega (aunque sea vacio), los vertices de la cobertura se
    resaltan y las aristas sin cubrir se dibujan punteadas en rojo, para poder
    *verificar visualmente* que una cobertura valida no deja aristas sueltas.
    """
    ax.clear()
    g = to_networkx(graph)
    nodes = list(graph.vertices)

    if not nodes:
        ax.text(0.5, 0.5, "Grafo vacio", ha="center", va="center",
                fontsize=14, color="#666666")
        ax.set_axis_off()
        if title:
            ax.set_title(title)
        return ax

    if positions is None:
        positions = compute_layout(graph, seed=seed, layout=layout, scale=scale)

    if cover is None:
        nx.draw_networkx_edges(g, positions, ax=ax, edge_color=COLOR_BASE_EDGE, width=1.4)
        covered_set: set = set()
        legend_edges = False
    else:
        covered_set = set(cover)
        covered_edges, uncovered_edges = split_edges(graph, covered_set)
        if uncovered_edges:
            nx.draw_networkx_edges(g, positions, ax=ax, edgelist=uncovered_edges,
                                   edge_color=COLOR_UNCOVERED_EDGE, style="dashed", width=1.9)
        if covered_edges:
            nx.draw_networkx_edges(g, positions, ax=ax, edgelist=covered_edges,
                                   edge_color=COLOR_COVERED_EDGE, width=1.5)
        legend_edges = True

    uncovered_nodes = [v for v in nodes if v not in covered_set]
    covered_nodes = [v for v in nodes if v in covered_set]

    nx.draw_networkx_nodes(g, positions, ax=ax, nodelist=uncovered_nodes,
                           node_color=COLOR_UNCOVERED, node_size=520,
                           edgecolors=NODE_BORDER, linewidths=1.3)
    nx.draw_networkx_nodes(g, positions, ax=ax, nodelist=covered_nodes,
                           node_color=COLOR_COVERED, node_size=620,
                           edgecolors=NODE_BORDER, linewidths=1.3)

    if show_labels:
        nx.draw_networkx_labels(g, positions, ax=ax, font_size=9, font_color=TEXT_COLOR)

    handles = [
        Line2D([], [], marker="o", color="w", markerfacecolor=COLOR_COVERED,
               markeredgecolor=NODE_BORDER, markersize=11, label="En cobertura"),
        Line2D([], [], marker="o", color="w", markerfacecolor=COLOR_UNCOVERED,
               markeredgecolor=NODE_BORDER, markersize=11, label="Fuera de cobertura"),
    ]
    if legend_edges:
        handles.append(Line2D([], [], color=COLOR_COVERED_EDGE, lw=2, label="Arista cubierta"))
        handles.append(Line2D([], [], color=COLOR_UNCOVERED_EDGE, lw=2, ls="--",
                              label="Arista sin cubrir"))
    ax.legend(handles=handles, loc="best", fontsize=8, framealpha=0.9)

    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=11)
    ax.margins(0.12)
    return ax


def render_to_png(
    graph: Graph,
    cover: Optional[Iterable[Hashable]],
    path: str | Path,
    *,
    title: Optional[str] = None,
    layout: str = "spring",
    seed: int = 0,
    show_labels: bool = True,
    dpi: int = 140,
    figsize: tuple[float, float] = (8.0, 6.0),
) -> Path:
    """Renderiza el grafo a un PNG sin necesidad de pantalla (util para el informe)."""
    from matplotlib.figure import Figure

    fig = Figure(figsize=figsize, dpi=100)
    ax = fig.add_subplot(111)
    draw_graph(ax, graph, cover=cover, layout=layout, seed=seed,
               title=title, show_labels=show_labels)
    fig.tight_layout()
    path = Path(path)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
