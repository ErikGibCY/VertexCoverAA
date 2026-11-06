# Avance 5 — Implementación de la Segunda Alternativa e Integración del Sistema

> **Asignatura:** Algoritmos Avanzados (2026-2)  
> **Institución:** Universidad Nacional de San Antonio Abad del Cusco (UNSAAC)  
> **Grupo 1:** Optimización de la Ubicación de Sistemas de Detección de Intrusos (IDS) mediante Cobertura de Vértices  
> **Integrantes:** Steffano Ricardo Caballero Zegarra, Adriel Alfredo Llactahuamani Ayala, Albert Erik Morocco Amanca, Diego Alonso Quispe Castilla  

---

## 1. Resumen y Objetivos del Avance

El **Avance 5** consolida la **segunda alternativa algorítmica** —el algoritmo de **Matching Maximal (2-aproximación)**— y la **integración total del sistema**. Ambas alternativas operan sobre los mismos formatos de entrada, la misma arquitectura y bajo una interfaz unificada de ejecución y medición.

Asimismo, se incorpora la solución exacta escalable basada en **Programación Lineal Entera (ILP con PuLP)** como oráculo de referencia frente a instancias donde la fuerza bruta no escala, y se evalúan las condiciones matemáticas donde ambas alternativas convergen o divergen en sus soluciones.

---

## 2. Segunda Alternativa: Matching Maximal ($2$-Aproximación)

### 2.1 Principio Algorítmico y Garantía Teórica
A diferencia de la heurística voraz (que evalúa grados locales de vértices), la segunda alternativa selecciona aristas disjuntas (que no comparten extremos) e incluye **ambos extremos** en la cobertura:

```text
Algoritmo MaximalMatchingVertexCover(G = (V, E)):
    C ← ∅
    E_rem ← E
    mientras E_rem ≠ ∅ hacer:
        tomar una arista (u, v) ∈ E_rem
        C ← C ∪ {u, v}
        E_rem ← E_rem \ {e ∈ E_rem : u ∈ e ∨ v ∈ e}
    retornar C
```

**Cota de aproximación demostrada:**
1. Las aristas elegidas constituyen un *matching* $M \subseteq E$ donde ninguna arista comparte vértices.
2. Toda cobertura válida $C^*$ debe cubrir cada arista de $M$, y como son disjuntas, debe contener al menos un extremo por cada arista de $M$:
   $$|C^*| \ge |M|$$
3. El algoritmo selecciona exactamente ambos extremos de cada arista en $M$:
   $$|C| = 2|M| \le 2|C^*|$$
4. Por lo tanto, el ratio de aproximación está matemáticamente acotado por:
   $$\alpha = \frac{|C|}{|C^*|} \le 2.0$$

### 2.2 Complejidad Temporal y Espacial
- **Complejidad Temporal:** $O(V + E)$. En cada paso se toma la primera arista en orden canónico y se eliminan en bloque todas las aristas que tocan a $u$ o $v$.
- **Complejidad Espacial:** $O(V + E)$ para la lista de aristas remanentes y el conjunto de cobertura.

---

## 3. Integración del Sistema y Reutilización Modular

La arquitectura del sistema integra todos los componentes en una tubería común sin duplicación de código:

```
[Entrada: JSON / ER / BA]
           │
           ▼
     [Graph (src/graph.py)] ──(Validación estricta de integridad)
           │
           ▼
[VertexCoverSolver.solve(key)] ──(Medición unificada: CPU perf_counter + tracemalloc)
     ├── 'greedy'     : Voraz por grado O(V*E)
     ├── 'greedy_pq'  : Voraz optimizado Heap O((V+E)log V)
     ├── 'matching'   : Matching maximal 2-aprox O(V+E)
     ├── 'exact'      : Fuerza bruta (ref. |V| <= 20)
     └── 'ilp'        : Programación Lineal Entera PuLP (ref. escalable)
           │
           ▼
     [verify.py] ──(Validación formal is_vertex_cover + ratio aproximación)
           │
           ▼
[Salida: CLI demo.py / GUI visualizer.py / CSV experiments]
```

### 3.1 Interfaz Común de Ejecución: `VertexCoverSolver.solve()`
En lugar de invocar métodos dispersos, el sistema implementa el método `solve(algorithm_key)` que estandariza la ejecución:
```python
res = solver.solve("matching")
# Retorna:
# {
#   "key": "matching",
#   "label": "Matching maximal (2-aprox)",
#   "cover": {'A', 'B', 'D', 'E'},
#   "size": 4,
#   "valid": True,
#   "time_ms": 0.157,
#   "memory_kib": 3.23
# }
```

### 3.2 Manejo de Entradas Inválidas
El sistema captura y reporta de manera comprensible cualquier anomalía de entrada:
- Archivos inexistentes (`FileNotFoundError`).
- Formato JSON con errores de sintaxis (`InvalidInstanceError: Error de sintaxis JSON`).
- Falta de la clave obligatoria `edges` (`InvalidInstanceError: Falta la clave requerida 'edges'`).
- Aristas malformadas con 1 o más de 2 nodos (`InvalidInstanceError: Arista invalida en posicion i`).
- Auto-bucles (`InvalidInstanceError: No se permiten auto-ciclos`).

---

## 4. Demostración Comparativa de Resultados

### 4.1 Instancia Pequeña del Avance 1 (`example_small.json`)
Red de 6 routers ($A, B, C, D, E, F$) y 6 enlaces:

```bash
python demo.py --instance data/instances/example_small.json --algorithm all
```

| Algoritmo | Cobertura Obtenida | Tamaño $|C|$ | Válida | Tiempo (ms) | Memoria (KiB) | Ratio frente al Óptimo |
|---|---|---|---|---|---|---|
| **Greedy por grado** | `['A', 'B', 'E']` | 3 | SÍ | 1.45 ms | 3.20 KiB | **1.000x** (Óptimo) |
| **Greedy (cola prioridad)** | `['A', 'B', 'E']` | 3 | SÍ | 0.26 ms | 4.55 KiB | **1.000x** (Óptimo) |
| **Matching maximal** | `['A', 'B', 'D', 'E']` | 4 | SÍ | 0.16 ms | 3.23 KiB | **1.333x** ($\le 2\times$) |
| **Exacto (fuerza bruta)** | `['A', 'B', 'E']` | 3 | SÍ | 0.40 ms | 3.15 KiB | **1.000x** (Óptimo) |
| **Exacto (ILP / PuLP)** | `['A', 'B', 'E']` | 3 | SÍ | 614.3 ms | 3903 KiB | **1.000x** (Óptimo) |

### 4.2 Instancia Adicional: Topología Backbone (`network_backbone_18.json`)
Red sintética tipo Barabási-Albert con 18 routers y 32 enlaces, con routers concentradores de alto tráfico:

```bash
python demo.py --instance data/instances/network_backbone_18.json --algorithm all
```

- **Óptimo de referencia (ILP y Fuerza Bruta):** 7 routers.
- **Greedy (ambas versiones):** 7 routers $\rightarrow$ **Ratio: 1.000x**. Tiempo: $\sim 1.0\text{ ms}$.
- **Matching maximal:** 14 routers $\rightarrow$ **Ratio: 2.000x**. Tiempo: $\sim 0.7\text{ ms}$.
- **Fuerza bruta:** 7 routers en $681.7\text{ ms}$.

---

## 5. Análisis Riguroso de Equivalencias y Diferencias

### 5.1 Caso de Equivalencia de Resultados ($|C_{\text{greedy}}| = |C_{\text{matching}}|$)
- **Topología Triángulo $K_3$:** Vértices $\{A, B, C\}$, aristas $\{(A,B), (B,C), (A,C)\}$.
  - Greedy selecciona el primer vértice de grado 2 (ej. $A$), cubre 2 aristas; queda $(B, C)$, selecciona $B$ $\rightarrow$ Cobertura $\{A, B\}$, tamaño **2**.
  - Matching selecciona una arista arbitraria (ej. $(A, B)$) e incluye ambos extremos $\rightarrow$ Como $(A, C)$ y $(B, C)$ ya tocan a $A$ y $B$, todas las aristas quedan cubiertas $\rightarrow$ Cobertura $\{A, B\}$, tamaño **2**.
  - **Explicación:** Cuando la estructura del grafo permite que un solo paso de matching cubra todas las aristas incidentes de un clique pequeño, ambas alternativas producen idéntico tamaño y alcanzan el óptimo teórico.

### 5.2 Caso de Diferencia Esperada ($|C_{\text{greedy}}| < |C_{\text{matching}}|$)
- **Topología Estrella $K_{1, k}$ (Centro $C$ conectado a $k$ hojas):**
  - Greedy calcula el grado de $C$ ($k$) y de las hojas ($1$). Selecciona inmediatamente $C$. Todas las $k$ aristas quedan cubiertas en un solo paso $\rightarrow$ Cobertura $\{C\}$, tamaño **1** (Óptimo).
  - Matching toma una arista arbitraria $(C, \text{hoja}_1)$ y agrega **ambos** vértices $\{C, \text{hoja}_1\}$ $\rightarrow$ Cobertura de tamaño **2**.
  - **Explicación:** Esta discrepancia no es un error de programación; responde directamente a la naturaleza teórica de los algoritmos:
    - Greedy pondera la densidad local de aristas y prioriza concentradores.
    - Matching no discrimina grados: añade ambos extremos de una arista para blindar su garantía matemática de 2-aproximación sin importar si una hoja era innecesaria.

---

## 6. Verificación Automatizada del Sistema

El sistema fue sometido a la suite de pruebas completa:

```bash
.\venv\Scripts\python.exe -m pytest tests/ -v
# Salida: 49 passed in 7.23s (100% de éxito)
```

Las 49 pruebas abarcan:
1. Pruebas de la estructura `Graph`, cálculo de densidad y detección de entradas inválidas.
2. Pruebas de corrección del primer algoritmo (Greedy base y Greedy Heap).
3. Pruebas de la 2-aproximación de Matching maximal sobre 10 instancias aleatorias.
4. Pruebas de concordancia exacta entre Fuerza Bruta e ILP (PuLP).
5. Pruebas de equivalencia (triángulo) y discrepancia esperada (estrella).
6. Pruebas de la visualización gráfica con NetworkX y Matplotlib (`test_viz.py`).

---

## 7. Conclusión

El proyecto cuenta ahora con sus dos alternativas completamente operativas, integradas bajo una interfaz común CLI y GUI, con mediciones exhaustivas de tiempo y memoria, manejo robusto de errores y respaldo de 49 pruebas automatizadas.
