# Vertex Cover IDS Placement

Ubicación óptima de sistemas de detección de intrusos (IDS) en una red, modelada
como el problema clásico de **Cobertura de Vértices (Vertex Cover)**.

> Proyecto semestral — Algoritmos Avanzados — UNSAAC
> Grupo 1 — Línea: Cobertura de vértices y comparación de estrategias de aproximación

## Problema

Cada enlace físico de una red debe tener al menos uno de sus dos extremos (routers)
monitoreado por un IDS/firewall. Se busca el conjunto mínimo de routers a monitorear
tal que **toda** conexión quede cubierta. Ver `docs/avance1.pdf` para la formulación
completa.

## Estado del proyecto

- [x] **Avance 1** — Formulación y delimitación del problema (`docs/avance1.pdf`)
- [x] **Avance 2** — Diseño algorítmico y plan de validación (`docs/avance2.pdf`)
- [x] **Avance 3** — Prototipo mínimo ejecutable (este repositorio)
- [ ] Entrega 2 — Integración completa, experimentos a mayor escala, análisis de complejidad empírico
- [ ] Entrega 3 — Sistema final, informe completo, defensa

Ver `docs/bitacora.md` para el registro de avance sesión a sesión.

## Estructura del repositorio

```
vertex-cover-ids/
├── src/
│   ├── graph.py        # Estructura de grafo (lista de adyacencia) + generadores + I/O
│   ├── solver.py        # VertexCoverSolver: greedy, matching maximal, exacto (fuerza bruta)
│   ├── verify.py        # Validación de coberturas y cálculo de ratio de aproximación
│
├── tests/
│   ├── test_graph.py     # Pruebas de la estructura de grafo
│   └── test_solver.py    # Pruebas básicas, límite y adversarias de los algoritmos
├── data/instances/        # Instancias de ejemplo en formato JSON
├── experiments/
│   ├── compare.py        # Script de comparación empírica (tiempo, ratio)
│   └── results/           # Salidas de los experimentos (CSV)
├── docs/
│   ├── avance1.tex/.pdf
│   ├── avance2.tex/.pdf
│   ├── avance3.md
│   └── bitacora.md
├── demo.py                # Prototipo ejecutable (CLI) para la demostración
└── requirements.txt
```

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso rápido

```bash
# Ejecutar el prototipo sobre la instancia de ejemplo del Avance 1
python demo.py --instance data/instances/example_small.json --algorithm all

# Correr las pruebas
pytest tests/ -v

# Correr el experimento comparativo
python experiments/compare.py
```

## Interfaz gráfica (proyeccion futura)

Además del modo consola —que se conserva tal cual— el proyecto incluye un
visualizador interactivo de grafos:

```bash
python visualizer.py
```

Permite:

- **Generar grafos aleatorios** (Erdős–Rényi `G(n,p)` o Barabási–Albert) eligiendo
  `n`, `p`/`m` y semilla, además de **cargar cualquier instancia JSON** del formato
  del proyecto (así no dependes solo de las dos instancias de ejemplo).
- **Ejecutar los algoritmos** (greedy, matching, exacto por fuerza bruta, exacto ILP)
  y **ver la cobertura resaltada** sobre el propio grafo: vértices en cobertura en
  naranja, y las aristas sin cubrir en rojo punteado (debería quedar vacío en una
  cobertura válida).
- Ver por cada algoritmo el **tamaño, validez, tiempo y ratio** frente al óptimo.
- **Exportar la imagen** a PNG y el **grafo actual a JSON** (para luego usarlo con
  `demo.py`).

> `demo.py` y `experiments/compare.py` **no se modificaron**: la interfaz gráfica es
> una capa adicional. El módulo de dibujo vive en `src/viz.py` y se prueba sin abrir
> ventanas (`tests/test_viz.py`).

## Algoritmos implementados

| Algoritmo                  | Archivo                                        | Garantía                   | Complejidad                                        |
| -------------------------- | ---------------------------------------------- | -------------------------- | -------------------------------------------------- |
| Greedy por grado           | `src/solver.py::greedy_degree_vertex_cover`    | Sin cota fija (heurística) | O(V·E)                                             |
| Matching maximal (2-aprox) | `src/solver.py::maximal_matching_vertex_cover` | ≤ 2·óptimo                 | O(V+E)                                             |
| Exacto (fuerza bruta)      | `src/solver.py::exact_vertex_cover_bruteforce` | Óptimo                     | O(2^V · E), solo referencia en instancias pequeñas |

## Integrantes

| Nombre                             |
| ---------------------------------- |
| Steffano Ricardo Caballero Zegarra |
| Adriel Alfredo Llactahuamani Ayala |
| Albert Erik Morocco Amanca         |
| Diego Alonso Quispe Castilla       |

## Licencia / uso académico

Proyecto desarrollado con fines educativos para la asignatura de Algoritmos Avanzados,
UNSAAC. No destinado a uso en producción.
