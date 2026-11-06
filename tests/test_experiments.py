"""
tests/test_experiments.py
--------------------------
Batería de pruebas automatizadas para el Avance 6 y 7:
1. Validación de reproducibilidad con semillas controladas (cero sorpresas).
2. Integridad del módulo formal de complejidad y operaciones dominantes.
3. Verificación cruzada de todas las heurísticas frente a la referencia exacta (ILP).
4. Verificación de las invariantes matemáticas (rho <= 2.0x en matching, optimalidad de ILP).
5. Ejecución del piloto experimental y consistencia de métricas.
"""

import pytest
from pathlib import Path
from src.graph import Graph
from src.solver import VertexCoverSolver
from src.verify import is_vertex_cover
from src.complexity import COMPLEXITY_DATA, get_complexity_table_str
from experiments.benchmark import run_benchmark, RESULTS_CSV


class TestAvance6DisenoExperimentalYReproducibilidad:
    def test_reproducibilidad_con_semilla_fija_erdos_renyi(self):
        """Dos instancias generadas con la misma semilla deben ser estrictamente idénticas."""
        g1 = Graph.random_graph(n=14, p=0.35, seed=12345)
        g2 = Graph.random_graph(n=14, p=0.35, seed=12345)

        assert g1.vertices == g2.vertices
        assert g1.edges == g2.edges
        assert g1.num_edges() == g2.num_edges()

        # Ambos solvers deben producir exactamente las mismas coberturas y métricas
        s1 = VertexCoverSolver(g1)
        s2 = VertexCoverSolver(g2)
        res1 = s1.solve("greedy_pq")
        res2 = s2.solve("greedy_pq")
        assert res1["cover"] == res2["cover"]
        assert res1["size"] == res2["size"]

    def test_reproducibilidad_con_semilla_fija_barabasi_albert(self):
        """Verifica determinismo estricto en redes Barabási-Albert."""
        g1 = Graph.barabasi_albert(n=15, m=2, seed=999)
        g2 = Graph.barabasi_albert(n=15, m=2, seed=999)

        assert g1.edges == g2.edges
        s1 = VertexCoverSolver(g1)
        s2 = VertexCoverSolver(g2)
        assert s1.solve("matching")["cover"] == s2.solve("matching")["cover"]

    def test_semillas_distintas_producen_grafos_diferentes(self):
        """Comprueba que semillas distintas exploren el espacio muestral adecuadamente."""
        g1 = Graph.random_graph(n=16, p=0.3, seed=101)
        g2 = Graph.random_graph(n=16, p=0.3, seed=102)
        assert g1.edges != g2.edges

    def test_modulo_complejidad_contiene_todas_las_alternativas(self):
        """El módulo de complejidad debe describir todos los componentes evaluados."""
        esperados = [
            "Graph (Listas de Adyacencia)",
            "Greedy por Grado (Básico)",
            "Greedy (Cola de Prioridad - Heap)",
            "Matching Maximal (2-aprox)",
            "Fuerza Bruta (Exacto Exhaustivo)",
            "ILP Exacto (PuLP / Branch & Cut)",
        ]
        for key in esperados:
            assert key in COMPLEXITY_DATA
            item = COMPLEXITY_DATA[key]
            assert "tiempo_peor" in item
            assert "espacio" in item
            assert "operacion_dominante" in item

        tabla = get_complexity_table_str()
        assert "ANÁLISIS DE COMPLEJIDAD TEÓRICA" in tabla
        assert len(tabla.splitlines()) >= 10


class TestAvance6ValidacionCruzadaEInvariantes:
    @pytest.mark.parametrize("seed", [201, 202, 203, 204])
    def test_validacion_cruzada_frente_a_ilp_en_grafos_aleatorios(self, seed):
        """
        En cada grafo aleatorio:
        1. Todas las coberturas encontradas deben ser formalmente válidas.
        2. Ninguna heurística puede ser menor que el óptimo exacto (ILP).
        3. Matching Maximal debe cumplir la cota teórica |C_match| <= 2 * |C_opt|.
        """
        g = Graph.random_graph(n=14, p=0.35, seed=seed)
        solver = VertexCoverSolver(g)

        res_greedy = solver.solve("greedy")
        res_greedy_pq = solver.solve("greedy_pq")
        res_matching = solver.solve("matching")
        res_ilp = solver.solve("ilp")

        # 1. Validez formal
        assert res_greedy["valid"]
        assert res_greedy_pq["valid"]
        assert res_matching["valid"]
        assert res_ilp["valid"]

        opt_size = res_ilp["size"]

        # 2. Invariante de optimalidad
        assert res_greedy["size"] >= opt_size
        assert res_greedy_pq["size"] >= opt_size
        assert res_matching["size"] >= opt_size

        # 3. Invariante formal de 2-aproximación
        assert res_matching["size"] <= 2 * opt_size

    def test_piloto_experimental_genera_metricas_correctas(self, tmp_path):
        """
        Comprueba que la ejecución del protocolo experimental piloto
        genere datos numéricos coherentes y persistentes.
        """
        rows = run_benchmark(
            n_values_er=[6, 8],
            n_values_ba=[6],
            generate_plots=False,
            show_complexity=False,
        )

        assert len(rows) == 3
        for r in rows:
            assert r["n"] in (6, 8)
            assert r["m_edges"] >= 0
            assert r["optimo"] >= 0
            assert r["greedy_ratio"] >= 1.0
            assert r["matching_ratio"] >= 1.0
            assert r["greedy_tiempo_ms"] >= 0.0
            assert r["greedy_memoria_kib"] >= 0.0
