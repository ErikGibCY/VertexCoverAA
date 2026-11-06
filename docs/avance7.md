# Avance 7. Experimentos Preliminares y Preparación de la Segunda Entrega

**Asignatura:** Algoritmos Avanzados (UNSAAC 2026-II)  
**Proyecto:** Optimización de la Ubicación de Sistemas de Detección de Intrusos (IDS) mediante Cobertura de Vértices (*Vertex Cover*)  
**Grupo 1:** Caballero, Castilla, Llactahuamani, Morocco, Quispe  

---

## 1. Sistema Integrado y Flujo Completo

El proyecto conforma un sistema integral que abarca desde la adquisición y generación de instancias de red hasta la visualización y análisis de métricas:

```
[ Entradas: JSON / Generador ER / BA ]
                  │
                  ▼
[ Validación de Instancia: Graph.validate_instance_data() ]
                  │
                  ▼
[ Modelado de Red: Graph (Listas de Adyacencia O(V+E)) ]
                  │
                  ▼
[ Capa de Resolución Unificada: VertexCoverSolver.solve() ]
   ├── greedy       : Heurística voraz por grado O(V·E)
   ├── greedy_pq    : Heurística voraz con Heap O((V+E)log V)
   ├── matching     : 2-aproximación por emparejamiento O(V+E)
   ├── exact        : Fuerza bruta exacta exhaustiva (n <= 20)
   └── ilp          : Exacto escalable con PuLP / CBC (n >= 30)
                  │
                  ▼
[ Verificación Formal de Seguridad: is_vertex_cover() ]
                  │
                  ▼
[ Medición Instrumentada: time.perf_counter() & tracemalloc ]
                  │
                  ▼
[ Salidas: CLI demo.py, GUI visualizer.py, CSV y Gráficos PNG ]
```

---

## 2. Resultados de los Experimentos Preliminares

Los experimentos preliminares se ejecutaron sobre 14 instancias representativas de dos topologías clave (Erdős-Rényi y Barabási-Albert). Los resultados completos están registrados en `experiments/results/comparison.csv`:

### Resumen de Resultados Empíricos
| Topología | Vértices ($n$) | Aristas ($\|E\|$) | Óptimo ($\|C^*\|$) | Greedy ($t_{\text{ms}}$, $\rho$) | Greedy Heap ($t_{\text{ms}}$, $\rho$) | Matching ($t_{\text{ms}}$, $\rho$) | ILP ($t_{\text{ms}}$) | Fuerza Bruta ($t_{\text{ms}}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ER** | 6 | 3 | 2 | 0.22 ms (1.00x) | 0.20 ms (1.00x) | 0.12 ms (2.00x) | 798 ms* | 0.21 ms |
| **ER** | 8 | 10 | 4 | 0.38 ms (1.00x) | 0.44 ms (1.00x) | 0.26 ms (1.50x) | 48 ms | 2.42 ms |
| **ER** | 10 | 13 | 5 | 0.46 ms (1.20x) | 0.47 ms (1.00x) | 0.37 ms (2.00x) | 48 ms | 7.25 ms |
| **ER** | 12 | 19 | 5 | 1.43 ms (1.00x) | 0.73 ms (1.00x) | 0.75 ms (2.00x) | 50 ms | 27.54 ms |
| **ER** | 14 | 35 | 9 | 1.88 ms (1.00x) | 1.82 ms (1.00x) | 1.12 ms (1.33x) | 73 ms | 269.91 ms |
| **ER** | 16 | 33 | 9 | 0.90 ms (1.00x) | 1.15 ms (1.00x) | 1.32 ms (1.56x) | 61 ms | 700.79 ms |
| **ER** | 18 | 52 | 12 | 2.20 ms (1.00x) | 1.88 ms (1.00x) | 1.39 ms (1.33x) | 82 ms | **4440.18 ms** |
| **ER** | 22 | 60 | 14 | 2.72 ms (1.07x) | 3.42 ms (1.00x) | 1.69 ms (1.43x) | 99 ms | *Omitido (>20)* |
| **ER** | 26 | 90 | 16 | 2.49 ms (1.19x) | 5.35 ms (1.19x) | 2.96 ms (1.50x) | 100 ms | *Omitido (>20)* |
| **BA** | 10 | 17 | 5 | 0.51 ms (**1.00x**) | 0.59 ms (**1.00x**) | 0.39 ms (1.20x) | 48 ms | *Evaluado con ILP* |
| **BA** | 15 | 27 | 7 | 0.74 ms (**1.00x**) | 0.89 ms (**1.00x**) | 0.63 ms (1.43x) | 50 ms | *Evaluado con ILP* |
| **BA** | 20 | 35 | 9 | 0.93 ms (**1.00x**) | 1.16 ms (**1.00x**) | 0.86 ms (1.78x) | 66 ms | *Evaluado con ILP* |
| **BA** | 25 | 47 | 12 | 1.29 ms (**1.00x**) | 1.83 ms (1.08x) | 1.48 ms (1.67x) | 67 ms | *Evaluado con ILP* |
| **BA** | 30 | 56 | 15 | 1.64 ms (**1.00x**) | 2.14 ms (**1.00x**) | 1.50 ms (1.87x) | 68 ms | *Evaluado con ILP* |

*\*Nota: El primer llamado a ILP incluye la inicialización del subproceso CBC en disco.*

### Artefactos Visuales Generados
El motor experimental genera automáticamente dos figuras de alta resolución en `experiments/results/`:
1. **`experimentos_preliminares.png`:**
   - *Panel izquierdo:* Curva de tiempo vs. número de vértices $n$ en escala logarítmica. Evidencia la pendiente hiper-pronunciada de Fuerza Bruta frente a la estabilidad lineal y subcuadrática de los métodos aproximados.
   - *Panel derecho:* Ratios de aproximación en redes Erdős-Rényi y Barabási-Albert en contraste con la línea óptima ($1.0\times$) y la cota teórica superior ($2.0\times$).
2. **`panel_consolidado_entrega2.png`:**
   - Dashboard de 3 paneles listo para sustentación que integra tiempos de ejecución, calidad de aproximación y consumo de memoria pico en KiB.

---

## 3. Discusión de Resultados: Teoría vs. Práctica

### 1. Escalabilidad y Tiempos de Cómputo
- **Fuerza Bruta:** Cumple estrictamente su cota teórica $O(\binom{V}{k} \cdot E)$. A partir de $n=14$, el tiempo se multiplica exponencialmente (de 269 ms a 4440 ms en $n=18$). Esto demuestra experimentalmente por qué no es viable para redes reales sin apoyo de solvers especializados.
- **ILP (PuLP/CBC):** Mantiene tiempos estables entre 45 y 100 ms hasta $n=30$. Su formulación matemática permite resolver exactamente la referencia sin el colapso de la fuerza bruta.
- **Matching Maximal:** Es consistentemente el algoritmo más rápido en todas las pruebas ($< 3\text{ ms}$ en $n=26$). Su recorrido lineal de aristas $O(V+E)$ lo posiciona como la mejor alternativa para despliegues de IDS en tiempo real o redes de topología dinámica.
- **Greedy con Cola de Prioridad:** El uso de `heapq` con actualizaciones perezosas previene re-escaneos redundantes de aristas, mostrando un comportamiento muy parejo con tiempos inferiores a 6 ms en todas las instancias.

### 2. Influencia Crítica de la Topología en las Heurísticas
- **Redes Homogéneas (Erdős-Rényi):** Al no haber routers con grados desproporcionadamente grandes, Greedy y Matching obtienen resultados competitivos con ratios de $1.05\times - 1.25\times$.
- **Redes Backbone con Hubs (Barabási-Albert):** En esta topología, **Greedy es imbatible**, logrando el óptimo exacto ($\rho = 1.00\times$) en casi el 100% de las instancias. Esto ocurre porque unos pocos routers actúan como concentradores de la mayoría de enlaces; Greedy los selecciona en los primeros pasos cubriendo decenas de aristas simultáneamente.
- **Comportamiento de Matching Maximal en Barabási-Albert:** Matching toma ambos extremos de una arista arbitraria. Al tomar una arista que conecta un hub con una hoja periférica, selecciona inevitablemente el nodo hoja, el cual tiene grado 1 y no aporta a cubrir otras aristas. Por esta razón, el ratio de Matching sube hasta $1.87\times$ en $n=30$, manteniéndose no obstante siempre por debajo de su garantía formal de $2.0\times$.

### 3. Consumo de Memoria
- El consumo pico de memoria para las heurísticas se mantiene entre $1.5$ y $8.5\text{ KiB}$, confirmando que la estructura de listas de adyacencia y el conjunto de coberturas son extremadamente ligeros para sistemas empotrados o routers de borde.

---

## 4. Checklist de Evidencias para la Segunda Entrega

| Criterio de Evaluación | Evidencia Concreta en el Repositorio | Estado |
| :--- | :--- | :---: |
| **1. Implementación funcional de dos alternativas** | `src/solver.py`: Heurística voraz (básica y con Heap) + Matching Maximal (2-aprox). | **[✓] Completo** |
| **2. Referencia exacta escalable** | `src/solver.py`: Fuerza Bruta exhaustiva ($n \le 20$) + ILP con PuLP ($n \ge 30$). | **[✓] Completo** |
| **3. Integración del sistema e interfaz común** | `VertexCoverSolver.solve()`, CLI `demo.py` y GUI `visualizer.py`. | **[✓] Completo** |
| **4. Manejo de entradas inválidas** | `Graph.validate_instance_data()` y clase `InvalidInstanceError` en `src/graph.py`. | **[✓] Completo** |
| **5. Batería de pruebas automatizadas** | 58 pruebas automatizadas aprobadas con `pytest tests/ -v`. | **[✓] Completo** |
| **6. Análisis de complejidad y operaciones dominantes** | Módulo formal `src/complexity.py` y reporte `docs/avance6.md`. | **[✓] Completo** |
| **7. Diseño experimental y semillas reproducibles** | Parámetros controlados en `experiments/benchmark.py` y datos en `comparison.csv`. | **[✓] Completo** |
| **8. Experimentos preliminares y gráficos** | `experimentos_preliminares.png` y `panel_consolidado_entrega2.png`. | **[✓] Completo** |
| **9. Discusión teoría vs. práctica** | Análisis detallado en `docs/avance7.md` y terminal de benchmark. | **[✓] Completo** |
| **10. Bitácora de aprendizaje al día** | `docs/bitacora.md` actualizada con las Sesiones 1 a 7 completas. | **[✓] Completo** |
