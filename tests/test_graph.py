"""Pruebas de la estructura Graph."""

import pytest

from src.graph import Graph


def test_add_edge_updates_both_adjacency_lists():
    g = Graph()
    g.add_edge("A", "B")
    assert g.is_edge("A", "B")
    assert g.is_edge("B", "A")
    assert g.degree("A") == 1
    assert g.degree("B") == 1


def test_no_self_loops():
    g = Graph()
    with pytest.raises(ValueError):
        g.add_edge("A", "A")


def test_num_vertices_and_edges():
    g = Graph(vertices=["A", "B", "C"], edges=[("A", "B"), ("B", "C")])
    assert g.num_vertices() == 3
    assert g.num_edges() == 2


def test_isolated_vertex_has_degree_zero():
    g = Graph(vertices=["A", "B"], edges=[])
    g.add_vertex("Z")
    assert g.degree("Z") == 0
    assert "Z" in g.vertices


def test_from_json_loads_known_instance():
    g = Graph.from_json("data/instances/example_small.json")
    assert g.num_vertices() == 6
    assert g.num_edges() == 6
    assert g.degree("A") == 3  # vertice de mayor grado en la instancia de ejemplo


def test_random_graph_respects_vertex_count():
    g = Graph.random_graph(n=15, p=0.3, seed=42)
    assert g.num_vertices() == 15


def test_barabasi_albert_requires_valid_m():
    with pytest.raises(ValueError):
        Graph.barabasi_albert(n=5, m=5)


def test_graph_density():
    # Grafo vacio o con 1 vertice
    assert Graph().density() == 0.0
    assert Graph(vertices=["A"]).density() == 0.0

    # Grafo completo K3: 3 aristas / (3*2/2 = 3) = 1.0
    k3 = Graph(vertices=["A", "B", "C"], edges=[("A", "B"), ("B", "C"), ("A", "C")])
    assert k3.density() == 1.0

    # Camino de 2 aristas en 3 vertices: 2 / 3 = 0.6667
    p3 = Graph(vertices=["A", "B", "C"], edges=[("A", "B"), ("B", "C")])
    assert round(p3.density(), 4) == 0.6667


def test_invalid_instance_errors(tmp_path):
    from src.graph import InvalidInstanceError

    # Archivo no encontrado
    with pytest.raises(FileNotFoundError):
        Graph.from_json("ruta/inexistente/grafo.json")

    # JSON con sintaxis rota
    broken_json = tmp_path / "broken.json"
    broken_json.write_text("{esta_roto: true", encoding="utf-8")
    with pytest.raises(InvalidInstanceError, match="Error de sintaxis JSON"):
        Graph.from_json(broken_json)

    # JSON que no es un objeto
    list_json = tmp_path / "list.json"
    list_json.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(InvalidInstanceError, match="debe ser un objeto"):
        Graph.from_json(list_json)

    # Falta clave edges
    no_edges = tmp_path / "no_edges.json"
    no_edges.write_text('{"name": "test", "vertices": ["A"]}', encoding="utf-8")
    with pytest.raises(InvalidInstanceError, match="Falta la clave requerida 'edges'"):
        Graph.from_json(no_edges)

    # Arista mal formateada (solo 1 elemento)
    bad_edge = tmp_path / "bad_edge.json"
    bad_edge.write_text('{"edges": [["A"]]}', encoding="utf-8")
    with pytest.raises(InvalidInstanceError, match="Arista invalida"):
        Graph.from_json(bad_edge)

    # Arista con auto-ciclo
    self_loop = tmp_path / "self_loop.json"
    self_loop.write_text('{"edges": [["A", "A"]]}', encoding="utf-8")
    with pytest.raises(InvalidInstanceError, match="No se permiten auto-ciclos"):
        Graph.from_json(self_loop)

