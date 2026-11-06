# Avance 6. Pruebas Automatizadas, Análisis de Complejidad y Diseño Experimental

**Asignatura:** Algoritmos Avanzados (UNSAAC 2026-II)  
**Proyecto:** Optimización de la Ubicación de Sistemas de Detección de Intrusos (IDS) mediante Cobertura de Vértices (*Vertex Cover*)  
**Grupo 1:** Caballero, Castilla, Llactahuamani, Morocco, Quispe  

---

## 1. Batería Organizada de Pruebas Automatizadas

El proyecto cuenta con una suite integral de **58 pruebas automatizadas** gestionadas mediante `pytest`, distribuidas modularmente para certificar la corrección, solidez y reproducibilidad de todo el sistema:

| Módulo de Pruebas | N° Pruebas | Cobertura y Operaciones Evaluadas |
| :--- | :---: | :--- |
| `tests/test_graph.py` | 9 | Construcción de listas de adyacencia, prevención de auto-ciclos, grados aislados, serialización/deserialización JSON, cálculo de densidad $2\|E\|/(n(n-1))$ y rechazo controlado con `InvalidInstanceError`. |
| `tests/test_solver.py` | 35 | **Casos básicos:** coincidencia exacta con cálculo manual ($n=6$, $K_3$).<br>**Casos límite:** grafos vacíos, 1 arista, componentes desconectadas, cliques $K_n$, rechazo de fuerza bruta en $n>20$.<br>**Casos adversarios:** grafos estrella $K_{1,k}$ donde greedy es óptimo ($1.0\times$) y matching es subóptimo ($2.0\times$).<br>**Avance 4 (Heap):** coincidencia del Greedy con cola de prioridad $O((V+E)\log V)$ con solución manual y pruebas con semillas aleatorias.<br>**Avance 5 (ILP):** equivalencia estricta entre PuLP e ILP frente a Fuerza Bruta, interfaz unificada `solve()` y perfilado de memoria. |
| `tests/test_viz.py` | 5 | Transformación a grafos NetworkX, partición de aristas cubiertas/descubiertas, cálculo de layouts deterministas y renderizado a archivos de imagen sin bloqueos. |
| `tests/test_experiments.py` | 9 | **Avance 6:** Determinismo estricto bajo semillas fijas (ER y BA), generación de grafos distintos ante semillas variadas, verificación cruzada de que ninguna heurística produzca coberturas menores al óptimo ILP, cumplimiento estricto de la invariante formal $\rho \le 2.0\times$ en Matching Maximal, e integridad del módulo de complejidad y piloto experimental. |

> **Comando de ejecución:**
> ```bash
> pytest tests/ -v
> ```
> *Resultado actual:* **58 pasadas, 0 fallidas (100% de éxito en < 5 segundos).**

---

## 2. Análisis de Complejidad Teórica y Operaciones Dominantes

Se formalizó la matriz de complejidad de todos los componentes del sistema en `src/complexity.py`:

```
=========================================================================================================
 ANÁLISIS DE COMPLEJIDAD TEÓRICA Y OPERACIONES DOMINANTES
=========================================================================================================
Componente / Algoritmo             | Peor Caso          | Espacial   | Operación Dominante
---------------------------------------------------------------------------------------------------------
Graph (Listas de Adyacencia)       | O(V + E)           | O(V + E)   | Inserción / Consulta de vecinos en dict de sets
Greedy por Grado (Básico)          | O(V * E)           | O(V + E)   | Recálculo iterativo de grados residuales
Greedy (Cola de Prioridad - Heap)  | O((V + E) log V)   | O(V + E)   | Extracción max-heap con lazy updates
Matching Maximal (2-aprox)         | O(V + E)           | O(V + E)   | Filtrado lineal de aristas disjuntas
Fuerza Bruta (Exacto Exhaustivo)   | O(C(V, k*) * E)    | O(V)       | Generación combinatoria y verificación exhaustiva
ILP Exacto (PuLP / Branch & Cut)   | O(2^V) [NP-difícil] | O(V + E)   | Simplex + Branch and Cut (solver CBC)
=========================================================================================================
```

### Operaciones Dominantes y Costos Amortizados
1. **Lista de Adyacencia (`Graph`):** Utiliza un diccionario de conjuntos (`dict[Hashable, set[Hashable]]`). La adición de aristas y consulta de adyacencia se realiza en tiempo promedio $O(1)$ y costo amortizado $O(1)$.
2. **Greedy con Cola de Prioridad (`heapq`):**
   - Utiliza una cola de prioridad de tuplas `(-deg, str(v), v)` para emular un max-heap canónico.
   - Aplica **actualizaciones perezosas (lazy updates)**: en lugar de un heap mutable complejo, al extraer un vértice se verifica si su grado residual actual coincide con el grado con el que fue encolado; de no ser así, se descarta o reencola en $O(\log V)$.
   - Cada arista $(u, v)$ desencadena decrementos en sus extremos a lo más una vez, garantizando una complejidad estricta de $O((V + E) \log V)$.
3. **Matching Maximal (2-Aproximación):**
   - Almacena las aristas en orden canónico ordenado. En una sola pasada lineal $O(E)$, si una arista $(u, v)$ tiene ambos extremos fuera del conjunto de vértices ya seleccionados, se seleccionan ambos $u$ y $v$.
   - Cada arista se evalúa una sola vez con consultas hash $O(1)$, operando en tiempo lineal $O(V + E)$.
4. **Fuerza Bruta vs. ILP:**
   - La fuerza bruta explora combinaciones $\binom{V}{k}$ para $k=1, 2, \dots$. En $n=18$ realiza miles de verificaciones ($>4400\text{ ms}$).
   - El solver ILP formula el programa lineal binario entero minimizando $\sum x_v$ sujeto a $x_u + x_v \ge 1$, y resuelve instancias de hasta $n=100$ en menos de $100\text{ ms}$ mediante relajación lineal y cortes Gomory.

---

## 3. Diseño Experimental Definitivo

### Variables Controladas y Parámetros
- **Topologías evaluadas:**
  1. **Redes Homogéneas Erdős-Rényi $G(n, p)$:** Modelan enlaces de red con probabilidad uniforme ($p=0.3$).
  2. **Redes Backbone Barabási-Albert:** Modelan redes de telecomunicaciones con topología libre de escala (*scale-free*), donde nuevos routers se conectan preferentemente a routers existentes de alto grado ($m=2$).
- **Tamaños de Instancia ($n$):**
  - Erdős-Rényi: $n \in \{6, 8, 10, 12, 14, 16, 18, 22, 26\}$.
  - Barabási-Albert: $n \in \{10, 15, 20, 25, 30\}$.
- **Control de Reproducibilidad:**
  - Semillas deterministas fijadas: $\text{seed} = 100 + n$ (ER) y $\text{seed} = 200 + n$ (BA).
  - Orden canónico en el ordenamiento de vértices y aristas para neutralizar el hash randomization de Python (`PYTHONHASHSEED`).

### Métricas Registradas
1. **Tamaño de la Cobertura ($\|C\|$):** Cantidad de routers seleccionados para instalar IDS.
2. **Ratio de Aproximación Empírico ($\rho$):** $\rho = \frac{\|C\|}{\|C^*\|}$, donde $\|C^*\|$ es la solución óptima exacta (calculada por Fuerza Bruta o ILP).
3. **Tiempo de Ejecución de CPU ($t_{\text{ms}}$):** Medido en milisegundos mediante `time.perf_counter()`.
4. **Consumo de Memoria Pico ($M_{\text{KiB}}$):** Medido en KiB mediante `tracemalloc`.
5. **Densidad del Grafo ($\delta$):** $\delta = \frac{2\|E\|}{n(n-1)}$.

---

## 4. Experimento Piloto y Validación

El experimento piloto se ejecutó a través de `experiments/benchmark.py`, generando la salida estructurada en `experiments/results/comparison.csv`:

- **Consistencia Numérica:** En el 100% de las instancias, los tamaños obtenidos por Greedy, Greedy Heap y Matching fueron $\ge \|C^*\|$.
- **Validación de Cota Teórica:** En ninguna instancia Matching superó el doble del óptimo ($\rho \le 2.0\times$), alcanzando un máximo empírico de $1.87\times$ en Barabási-Albert.
- **Reproducibilidad:** Múltiples ejecuciones sobre el mismo entorno produjeron exactamente los mismos valores de cobertura y ratios con varianza cero en los resultados combinatorios.
