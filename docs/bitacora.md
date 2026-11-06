# Bitácora de aprendizaje

Evidencia de proceso para el indicador **AG-C06.01** (aprendizaje autónomo y desarrollo
sin supervisión externa). Cada entrada corresponde a una sesión real de trabajo: qué se
hizo, qué se tuvo que aprender o decidir por cuenta propia, y qué quedó pendiente.

> Cómo seguir esta bitácora: agreguen una entrada nueva cada vez que se sienten a trabajar
> en el proyecto (no solo antes de cada entrega). Una entrada corta de 5 líneas honestas
> vale más que una entrada larga escrita de memoria varias semanas después.

---

## Sesión 1 — 2026-10-03 — Formulación del problema (Avance 1)

**Qué se hizo:** Se definió la aplicación concreta de Vertex Cover (ubicación de IDS en una
red), se formuló el problema (entradas, salidas, restricciones, supuestos, función
objetivo) y se resolvió a mano una instancia de 6 routers con los dos algoritmos ya
acordados (greedy por grado y matching maximal).

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Cómo se demuestra formalmente la garantía de 2-aproximación del matching maximal
  (el argumento de que las aristas elegidas forman un *matching* y por qué eso acota el
  óptimo).
- Por qué el greedy por grado no tiene una cota de aproximación fija en el peor caso,
  a pesar de funcionar bien en la práctica.

**Pendiente para la siguiente sesión:** Diseñar la estructura de datos del grafo y decidir
el formato de archivo para las instancias.

---

## Sesión 2 — 2026-10-04 — Implementación del núcleo y pruebas (Avance 2)

**Qué se hizo:** Se implementó `Graph` (lista de adyacencia), `VertexCoverSolver` con los
tres algoritmos (greedy, matching maximal, exacto por fuerza bruta), `verify.py`, y un plan
de pruebas de 27 casos (básicos, límite, adversarios) con `pytest`.

**Qué tuvimos que aprender / decidir por cuenta propia:**
- **Bug de reproducibilidad (el hallazgo más importante de esta sesión).** Al escribir las
  pruebas, un mismo algoritmo sobre la misma instancia devolvía coberturas de distinto
  tamaño en ejecuciones distintas. Investigando, encontramos que Python aleatoriza el hash
  de los `str` entre procesos (`PYTHONHASHSEED`), así que iterar directamente sobre un
  `set()` de aristas no tiene un orden garantizado entre ejecuciones. Tuvimos que aprender
  sobre hashing en Python y rediseñar ambos algoritmos para que usen un orden canónico fijo
  (`_sorted_edges`), no porque lo pidiera el enunciado del algoritmo, sino porque el
  proyecto exige reproducibilidad (instrucción adicional 7 de la guía) y sin este arreglo
  no podíamos confiar en nuestros propios resultados experimentales.
- Cómo estructurar pruebas con `pytest` (fixtures implícitas, `@pytest.mark.parametrize`
  para repetir una verificación sobre varias instancias aleatorias sin duplicar código).
- Diferencia práctica entre lista de adyacencia y matriz de adyacencia para grafos dispersos,
  y por qué importa para este problema específico (redes reales son dispersas).

**Decisiones tomadas:**
- JSON como formato de instancia (en vez de un formato propio o CSV de aristas), por ser
  nativo en Python y fácil de diffear en Git.
- Separar la verificación (`verify.py`) de los algoritmos (`solver.py`), para que ninguna
  prueba pueda "hacer trampa" confiando solo en el tamaño devuelto.

**Pendiente para la siguiente sesión:** Escribir el prototipo ejecutable (`demo.py`) y el
primer experimento comparativo.

---

## Sesión 3 — 2026-10-04 — Prototipo, experimentos y documentación (Avance 2 cierre / Avance 3)

**Qué se hizo:** Se construyó `demo.py` (CLI de demostración), `experiments/compare.py`
(primer experimento reproducible), y se redactó el documento del Avance 2 con los
resultados reales obtenidos (no estimados).

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Manejo de `argparse` para una CLI con múltiples modos (archivo vs. instancia generada al
  vuelo), pensando en que la demostración del Avance 3 se hace en vivo y el docente puede
  pedir una instancia nueva en el momento.
- Al correr el primer experimento nos encontramos con que el tiempo del algoritmo exacto
  ya crecía de forma visiblemente exponencial entre 6 y 18 vértices (de 0.02ms a 174ms).
  Esto no lo "sabíamos" en abstracto hasta verlo en los datos; confirma por qué el proyecto
  pide un mecanismo de referencia aparte y por qué vamos a necesitar ILP (PuLP) para
  instancias más grandes en la Entrega 2.
- Configuración de LaTeX para generar los documentos de las entregas: tuvimos que resolver
  que el entorno de compilación no tenía el paquete de idioma español de `babel`
  disponible, lo que rompía el guionado automático del texto en tablas con palabras largas;
  se corrigió ajustando manualmente los anchos de columna y los puntos de corte de línea.

**Pendiente para la Entrega 2:**
- Incorporar `exact_vertex_cover_ilp` (PuLP) como referencia escalable más allá de
  ~20 vértices.
- Optimizar el greedy a `O((V+E) log V)` con una cola de prioridad.
- Ampliar el experimento a distintas densidades y a la topología tipo backbone
  (Barabási-Albert), no solo Erdos-Renyi.
- Instrumentar uso de memoria como métrica adicional.
- Visualización de grafos pequeños (candidato: NetworkX + matplotlib).

---

## Sesión 4 — 2026-10-18 — Optimización del Greedy y validación del primer algoritmo (Avance 4)

**Qué se hizo:**
- Se implementó la versión optimizada del algoritmo voraz con cola de prioridad (`heapq`), logrando bajar la complejidad de $O(V \cdot E)$ a $O((V+E)\log V)$ (`greedy_priority_queue_vertex_cover`).
- Se introdujo una capa de validación de integridad de instancias en `Graph` (`validate_instance_data` y `InvalidInstanceError`) para asegurar el rechazo controlado de auto-ciclos, archivos corruptos o aristas mal formadas.
- Se incorporaron pruebas automatizadas específicas para el primer algoritmo, verificando coincidencia exacta contra la derivación manual de 6 routers (`example_small.json`) y casos límite (grafos vacíos, grafos estrella, aristas aisladas).

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Cómo gestionar actualizaciones de grados residuales en un min-heap sin necesidad de un heap indexable mutable (que no viene en la biblioteca estándar de Python). Aprendimos a usar la técnica de **actualización perezosa (lazy update)**: al extraer un vértice del heap, si su grado en el heap no coincide con su grado residual actual en el diccionario de adyacencia, se descarta o re-inserta con su valor vigente.
- Resolución de desempates canónicos en el heap: descubrimos que si dos tuplas tienen el mismo grado negativo, Python intenta desempatar comparando el siguiente elemento. Al usar `(-deg, str(v), v)` garantizamos que la comparación sea siempre determinista y segura entre tipos heterogéneos.

**Pendiente para la siguiente sesión:**
- Integrar la segunda alternativa (Matching maximal) e ILP bajo una interfaz común `solve()`, e instrumentar la medición de memoria en KiB con `tracemalloc`.

---

## Sesión 5 — 2026-10-23 — Segunda alternativa, interfaz unificada y experimentos extendidos (Avance 5)

**Qué se hizo:**
- Se implementó la interfaz común unificada `VertexCoverSolver.solve(algorithm_key)`, que estandariza la ejecución de cualquier algoritmo, midiendo tiempo de CPU con `time.perf_counter()`, consumo pico de memoria con `tracemalloc`, y validando la cobertura con `is_vertex_cover`.
- Se integró el solver exacto escalable por Programación Lineal Entera (`exact_vertex_cover_ilp`) usando `PuLP` con el solver CBC.
- Se extendió el script de experimentos (`experiments/compare.py`) para contrastar ambas alternativas aproximadas frente a ILP y fuerza bruta sobre grafos aleatorios Erdős–Rényi y redes backbone Barabási–Albert hasta $n=30$.
- Se actualizaron la CLI (`demo.py`) y la interfaz gráfica (`visualizer.py`) para soportar todas las opciones y métricas.
- La suite de pruebas pytest alcanzó 49/49 pruebas aprobadas al 100%.

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Comprobación de equivalencias y discrepancias teóricas: estudiamos por qué en grafos como el triángulo $K_3$ tanto Greedy como Matching dan el óptimo (2), mientras que en grafos estrella $K_{1,k}$ y redes Barabási–Albert, Greedy obtiene ratio 1.00x y Matching alcanza su peor cota teórica (2.00x). Comprendimos que esto no es un error de código, sino una consecuencia directa de la estrategia matemática: matching añade ambos extremos de una arista para garantizar $2\text{-aprox}$, mientras que greedy capitaliza los routers concentradores de alto grado.
- Instrumentación de `tracemalloc` para medir la memoria pico sin introducir sobrecostos desmedidos en los algoritmos ligeros.

**Pendiente para la Entrega 2 / Entrega Final:**
- Consolidar el informe formal de la Entrega 2 integrando las gráficas comparativas generadas y los análisis de complejidad empíricos.
---

## Sesión 6 — 2026-11-04 — Batería de pruebas automatizadas, complejidad formal y diseño experimental (Avance 6)

**Qué se hizo:**
- Se formalizó el módulo de análisis de complejidad teórica y operaciones dominantes (src/complexity.py), detallando para cada estructura y algoritmo el peor caso, caso promedio, costo amortizado y operaciones dominantes.
- Se amplió la batería de pruebas automatizadas a 58 pruebas (	ests/test_experiments.py, 	ests/test_solver.py, 	ests/test_graph.py, 	ests/test_viz.py):
  - Pruebas de reproducibilidad estricta bajo semillas fijas tanto en grafos Erdős–Rényi como en redes backbone Barabási–Albert.
  - Verificación cruzada sistemática de todas las heurísticas frente al solver exacto (ILP) en grafos aleatorios, validando la invariante formal de que ningún algoritmo aproximado supere la cota de 2-aproximación (rho <= 2.0x) ni devuelva un tamaño inferior al óptimo formal.
  - Prueba automatizada del protocolo experimental piloto sobre instancias controladas.
- Se definió el diseño experimental definitivo: fijación de semillas base, selección de parámetros de densidad (p=0.3 en ER y m=2 en BA) y protocolo de medición de tiempo de CPU (perf_counter), memoria pico (	racemalloc) y ratio empírico.

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Cómo estructurar el protocolo de pruebas automatizadas para que verifique formalmente las propiedades asintóticas y de aproximación teórica sin depender de salidas fijadas a mano. Descubrimos que al usar pytest.mark.parametrize con semillas controladas y contrastar directamente contra la formulación ILP, pudimos validar la cota rho <= 2.0x en docenas de topologías disímiles.
- Detección de incompatibilidades de codificación en consolas de Windows (páginas de códigos como CP-1252): aprendimos que caracteres especiales o diacríticos fuera del conjunto ANSI básico en las salidas de consola pueden provocar UnicodeEncodeError en terminales locales si no se maneja la serialización o caracteres normalizados.

**Pendiente para la siguiente sesión:**
- Ejecutar el flujo completo de experimentos preliminares sobre el rango amplio de instancias, generar las curvas de escalabilidad y ratios con matplotlib y consolidar el informe para la Segunda Entrega.

---

## Sesión 7 — 2026-11-06 — Experimentos preliminares, visualizaciones analíticas y cierre de la Segunda Entrega (Avance 7)

**Qué se hizo:**
- Se construyó el motor integrado de experimentación experiments/benchmark.py y se actualizó experiments/compare.py, unificando el flujo completo del proyecto: generación y carga de instancias JSON, validación de integridad, resolución con los 5 algoritmos, verificación estricta de coberturas con is_vertex_cover() y exportación estructurada a CSV (experiments/results/comparison.csv).
- Se implementó la generación automática de gráficos analíticos de alta resolución (300 DPI) con matplotlib:
  1. experimentos_preliminares.png: Panel dual comparando escalabilidad temporal en escala logarítmica y ratios de aproximación frente a las cotas 1.0x y 2.0x.
  2. panel_consolidado_entrega2.png: Dashboard consolidado de 3 paneles que incluye tiempos de ejecución, calidad de la cobertura (ER vs BA) y consumo de memoria pico en KiB.
- Se integró la suite experimental y la consulta de complejidad teórica en la interfaz de consola (demo.py --complexity, demo.py --benchmark) y en la aplicación gráfica de escritorio (isualizer.py).
- Se contrastaron empíricamente las hipótesis teóricas: se comprobó el colapso exponencial de la Fuerza Bruta a partir de n > 18 (>4400 ms), mientras que ILP resolvió óptimos en n=30 en menos de 70 ms; y se evidenció por qué Greedy alcanza ratio 1.00x en redes tipo Barabási–Albert al explotar los routers concentradores de tráfico.
- Se consolidó la documentación técnica completa (README.md, docs/avance6.md, docs/avance7.md) y el repositorio con 58/58 pruebas aprobadas (100%).

**Qué tuvimos que aprender / decidir por cuenta propia:**
- Representación visual de datos empíricos a múltiples escalas: aprendimos a configurar escalas logarítmicas en el eje de tiempos para poder visualizar conjuntamente algoritmos de tiempo lineal (O(V+E)) con algoritmos exactos de complejidad exponencial (O(2^V * E)) sin que las curvas lineales queden aplastadas contra el eje horizontal.
- Comprensión empírica de la topología sobre las heurísticas: descubrimos que en redes backbone Barabási–Albert, Matching Maximal se degrada hacia ratios de 1.6x - 1.87x debido a que toma ambos vértices de aristas que inciden en nodos hoja, mientras que Greedy aprovecha la ley de potencia de los hubs logrando la cobertura óptima con el mínimo número de IDS.

**Pendiente para la Entrega Final (Unidad 3):**
- Explorar heurísticas metaheurísticas o algoritmos parametrizados FPT (Fixed-Parameter Tractable) con kernelización O(k^2) para ampliar aún más la capacidad del sistema ante grafos masivos de miles de nodos.
