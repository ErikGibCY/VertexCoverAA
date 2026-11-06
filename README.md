# Vertex Cover IDS Placement

Ubicación óptima de sistemas de detección de intrusos (IDS) en una red, modelada
como el problema clásico de **Cobertura de Vértices (*Vertex Cover*)**.

> Proyecto semestral — Algoritmos Avanzados — UNSAAC (2026-II)  
> Grupo 1 — Línea: Cobertura de vértices y comparación de estrategias de aproximación

---

## 📌 Problema y Contexto de Aplicación

En una infraestructura de red de telecomunicaciones, cada enlace físico de comunicación debe tener al menos uno de sus dos extremos (routers/switches) monitoreado por un IDS/firewall. Se busca identificar el conjunto mínimo de routers a instrumentar de modo que **toda** conexión quede cubierta, minimizando el costo de equipamiento y mantenimiento sin dejar puntos ciegos.

---

## 🚀 Estado del Proyecto y Avances

- [x] **Avance 1** — Formulación y delimitación del problema (`docs/avance1.pdf`)
- [x] **Avance 2** — Diseño algorítmico y plan de validación (`docs/avance2.pdf`)
- [x] **Avance 3** — Prototipo mínimo ejecutable (`docs/avance3.md`)
- [x] **Avance 4** — Implementación del primer algoritmo y optimización con Heap $O((V+E)\log V)$ (`docs/avance4.md`)
- [x] **Avance 5** — Segunda alternativa (Matching 2-aprox), solver exacto ILP (PuLP) e integración del sistema (`docs/avance5.md`, `docs/Avance05.pdf`)
- [x] **Avance 6** — Batería organizada de 58 pruebas automatizadas, complejidad formal y diseño experimental (`docs/avance6.md`)
- [x] **Avance 7** — Experimentos preliminares completos, visualizaciones analíticas y cierre de la Segunda Entrega (`docs/avance7.md`)

*Consulta `docs/bitacora.md` para la bitácora continua de aprendizaje (Sesiones 1 a 7 completas).*

---

## 📁 Estructura del Repositorio

```
VertexCover/
├── src/
│   ├── graph.py        # Estructura Graph (listas de adyacencia) + generadores ER/BA + validación JSON
│   ├── solver.py       # VertexCoverSolver: greedy, greedy_pq (heap), matching maximal, exacto y PuLP ILP
│   ├── verify.py       # Validación formal de coberturas (is_vertex_cover) y ratio de aproximación
│   ├── complexity.py   # Módulo formal de análisis de complejidad teórica y operaciones dominantes
│   └── viz.py          # Utilidades de renderizado y visualización gráfica (NetworkX / Matplotlib)
├── tests/
│   ├── test_graph.py       # Pruebas de Graph, cálculo de densidad y manejo de entradas inválidas
│   ├── test_solver.py      # Pruebas de casos básicos, límites, adversarios, Greedy Heap e ILP
│   ├── test_viz.py         # Pruebas del módulo de visualización y exportación de imágenes
│   └── test_experiments.py # Pruebas de Avance 6: reproducibilidad con semillas e invariantes de cota 2-aprox
├── data/instances/
│   ├── example_small.json       # Instancia canónica de 6 routers (del Avance 1)
│   └── network_backbone_18.json # Topología backbone de 18 routers
├── experiments/
│   ├── benchmark.py    # Motor experimental completo: evaluación ER/BA, exportación CSV y gráficos
│   ├── compare.py      # Script de compatibilidad que invoca el benchmark experimental
│   └── results/        # comparison.csv, experimentos_preliminares.png, panel_consolidado_entrega2.png
├── docs/               # Informes técnicos (avances 1 al 7), bitácora y PDFs formales
├── demo.py             # CLI unificada: ejecución individual, lote, análisis teórico y benchmark
├── visualizer.py       # Interfaz gráfica interactiva de escritorio (Tkinter + Matplotlib)
└── requirements.txt    # Dependencias del proyecto (pytest, networkx, matplotlib, pandas, pulp)
```

---

## ⚙️ Instalación y Requisitos

Se recomienda utilizar Python 3.10 o superior y un entorno virtual dedicado:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux / macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🧪 Guía Rápida de Uso y Pruebas

### 1. Ejecutar las Pruebas Automatizadas (Avance 6)
Ejecuta la suite completa de 58 pruebas unitarias:
```bash
pytest tests/ -v
```

### 2. Consultar el Análisis Teórico de Complejidad (Avance 6)
Despliega la matriz de complejidad temporal, espacial y caracterización de operaciones dominantes:
```bash
python demo.py --complexity
```

### 3. Ejecutar los Experimentos Preliminares y Generar Gráficos (Avance 7)
Corre el protocolo experimental completo sobre redes Erdős-Rényi y Barabási-Albert, exportando los datos a CSV y generando las gráficas en `experiments/results/`:
```bash
# Opción directa por demo.py
python demo.py --benchmark

# O mediante el módulo de experimentos
python -m experiments.benchmark
```

### 4. Demostración por Consola (CLI)
Probar instancias puntuales o generar redes aleatorias al vuelo:
```bash
# Instancia pequeña del Avance 1 (6 routers):
python demo.py --instance data/instances/example_small.json --algorithm all

# Instancia backbone mediana (18 routers):
python demo.py --instance data/instances/network_backbone_18.json --algorithm all

# Generar grafo aleatorio Erdos-Renyi G(14, 0.3) con semilla controlada:
python demo.py --random 14 0.3 --seed 42 --algorithm all
```

### 5. Interfaz Gráfica Interactiva (GUI)
Inicia la aplicación de escritorio interactiva para generar grafos, ejecutar algoritmos paso a paso, visualizar los routers seleccionados en color y consultar métricas:
```bash
python visualizer.py
```

---

## 📊 Algoritmos Comparados

| Algoritmo | Identificador CLI | Archivo / Método | Garantía Teórica | Temporal (Peor Caso) | Espacial |
| :--- | :---: | :--- | :---: | :---: | :---: |
| **Greedy por grado** | `greedy` | `src/solver.py::greedy_degree_vertex_cover` | Heurística voraz | $O(V \cdot E)$ | $O(V + E)$ |
| **Greedy Heap** | `greedy_pq` | `src/solver.py::greedy_priority_queue_vertex_cover` | Heurística voraz | $O((V+E)\log V)$ | $O(V + E)$ |
| **Matching Maximal** | `matching` | `src/solver.py::maximal_matching_vertex_cover` | $\le 2 \cdot \text{óptimo}$ | $O(V + E)$ | $O(V + E)$ |
| **Fuerza Bruta** | `exact` | `src/solver.py::exact_vertex_cover_bruteforce` | Óptimo exacto | $O(\binom{V}{k^*} \cdot E)$ | $O(V)$ |
| **ILP (PuLP / CBC)** | `ilp` | `src/solver.py::exact_vertex_cover_ilp` | Óptimo exacto | Branch & Cut | $O(V + E)$ |

---

## 👥 Integrantes del Grupo 1

- Steffano Ricardo Caballero Zegarra
- Adriel Alfredo Llactahuamani Ayala
- Albert Erik Morocco Amanca
- Jean Franco Castilla
- Erik Quispe
