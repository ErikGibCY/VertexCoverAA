"""
test_viz.py
-----------
Pruebas del modulo de visualizacion (src/viz.py). Se ejecutan sin abrir
ninguna ventana: se usa el backend "Agg" de matplotlib para dibujar en
memoria y exportar a PNG dentro de una carpeta temporal.
"""

import matplotlib
matplotlib.use("Agg")

from matplotlib.figure import Figure

from src import viz
from src.graph import Graph
from src.solver import VertexCoverSolver
from src.verify import is_vertex_cover


def test_to_networkx_preserves_vertices_and_edges():
    g = Graph(vertices=["A", "B", "C"], edges=[("A", "B"), ("B", "C")])
    nxg = viz.to_networkx(g)
    assert set(nxg.nodes) == {"A", "B", "C"}
    assert nxg.number_of_edges() == 2


def test_split_edges_separa_cubiertas_de_no_cubiertas():
    g = Graph(vertices=["A", "B", "C", "D"],
              edges=[("A", "B"), ("C", "D"), ("B", "C")])
    covered, uncovered = viz.split_edges(g, {"A"})
    assert ("A", "B") in covered
    assert ("C", "D") in uncovered


def test_compute_layout_devuelve_una_posicion_por_vertice():
    g = Graph.random_graph(n=8, p=0.4, seed=3)
    positions = viz.compute_layout(g, seed=1)
    assert set(positions) == g.vertices


def test_draw_graph_y_render_a_png(tmp_path):
    g = Graph.from_json("data/instances/example_small.json")
    cover = VertexCoverSolver(g).greedy_degree_vertex_cover()
    assert is_vertex_cover(g, cover)

    fig = Figure()
    ax = fig.add_subplot(111)
    viz.draw_graph(ax, g, cover=cover)  # no debe lanzar excepcion

    salida = viz.render_to_png(g, cover, tmp_path / "grafo.png", title="prueba")
    assert salida.exists()
    assert salida.stat().st_size > 0


def test_draw_graph_grafo_vacio_no_falla():
    g = Graph()
    fig = Figure()
    ax = fig.add_subplot(111)
    viz.draw_graph(ax, g)  # caso limite: no hay nada que dibujar
