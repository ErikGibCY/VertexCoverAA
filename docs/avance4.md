# Avance 4 — Implementación del Primer Algoritmo y Estructura Principal

> **Asignatura:** Algoritmos Avanzados (2026-2)  
> **Institución:** Universidad Nacional de San Antonio Abad del Cusco (UNSAAC)  
> **Grupo 1:** Optimización de la Ubicación de Sistemas de Detección de Intrusos (IDS) mediante Cobertura de Vértices  
> **Integrantes:** Steffano Ricardo Caballero Zegarra, Adriel Alfredo Llactahuamani Ayala, Albert Erik Morocco Amanca, Diego Alonso Quispe Castilla  

---

## 1. Resumen y Objetivos del Avance

En este cuarto avance se presenta la consolidación, optimización y validación formal del **primer algoritmo principal** del proyecto: la **heurística voraz (Greedy por grado)** para el problema de Cobertura de Vértices (Vertex Cover), junto con la **estructura de datos central**: el grafo no dirigido basado en listas de adyacencia (`Graph`).

El desarrollo responde a las metas comprometidas en la Entrega 1:
1. Implementación funcional verificable directamente sobre la CLI (`demo.py`) y la interfaz visual (`visualizer.py`).
2. Análisis comparativo entre la versión directa $O(V \cdot E)$ y la versión optimizada con cola de prioridad / min-heap $O((V + E) \log V)$ (`greedy_priority_queue_vertex_cover`).
3. Validación estricta contra la solución manual de 6 routers (`example_small.json`) y frente a soluciones exactas de referencia (fuerza bruta e ILP).
4. Cobertura de pruebas automatizadas que abarcan casos básicos, límite y adversos.

---

## 2. Estructura de Datos Principal: `Graph` (Lista de Adyacencia)

### 2.1 Justificación Teórica y Práctica
Para modelar redes de telecomunicaciones (routers como vértices $V$, enlaces físicos como aristas $E$), las topologías reales son predominantemente **dispersas** ($|E| \ll |V|^2$, densidades típicas entre $0.1$ y $0.3$).

La clase `Graph` implementa una lista de adyacencia mediante un diccionario de conjuntos de Python:
$$\text{adj}: \text{dict}[v, \text{set}[\text{vecinos}]]$$

| Operación | Complejidad Lista Adyacencia | Complejidad Matriz Adyacencia | Justificación en el Proyecto |
|---|---|---|---|
| Espacio en memoria | $O(V + E)$ | $O(V^2)$ | Permite escalar a cientos de routers sin sobrecosto cuadrático. |
| Grado de un vértice $\deg(v)$ | $O(1)$ (`len(adj[v])`) | $O(V)$ | Fundamental para el greedy, que evalúa grados frecuentemente. |
| Consulta de adyacencia $(u,v)$ | $O(1)$ promedio | $O(1)$ | Verificación instantánea en tabla hash. |
| Iterar vecinos de $v$ | $O(\deg(v))$ | $O(V)$ | Vital para la actualización local de aristas no cubiertas. |

### 2.2 Validación de Integridad y Robustez de Entradas
Respecto al diseño inicial de la Unidad 1, se incorporó una capa de validación exhaustiva (`validate_instance_data`) y la excepción `InvalidInstanceError`:
- Rechazo explícito de auto-ciclos ($(u, u)$ no tiene sentido en enlaces físicos de red).
- Verificación de tipos hashables para vértices y pares de aristas de longitud exacta 2.
- Captura de errores de sintaxis JSON y archivos no existentes, impidiendo excepciones no controladas.

---

## 3. Primer Algoritmo: Heurística Voraz (Greedy por Grado)

### 3.1 Correspondencia entre Pseudocódigo y Código Fuente

#### Pseudocódigo de Diseño (Avance 2)
```text
Algoritmo GreedyVertexCover(G = (V, E)):
    C ← ∅
    E_rem ← E
    mientras E_rem ≠ ∅ hacer:
        u* ← vértice en V con mayor grado en E_rem
        C ← C ∪ {u*}
        E_rem ← E_rem \ {e ∈ E_rem : u* es extremo de e}
    retornar C
```

#### Implementación 1: Línea Base Determinista $O(V \cdot E)$
En `src/solver.py::greedy_degree_vertex_cover`:
- Se extraen las aristas canónicamente ordenadas con `_sorted_edges()`.
- En cada iteración se cuentan las incidencias de cada vértice sobre las aristas restantes (`degree_count`).
- Se selecciona `best_vertex = max(degree_count, key=degree_count.get)` y se filtran las aristas incidentes.
- **Correspondencia:** Es una traducción directa 1 a 1 del pseudocódigo teórico.

#### Implementación 2: Optimización con Cola de Prioridad $O((V + E) \log V)$
En `src/solver.py::greedy_priority_queue_vertex_cover`:
- **Decisión de diseño:** En grafos densos o de gran escala, recalcular el grado recorriendo todas las aristas pendientes cuesta $O(E)$ por paso, acumulando $O(V \cdot E)$.
- **Estructura optimizada:** Se usa un min-heap (`heapq`) almacenando tuplas $(-deg, \text{str}(v), v)$ para simular un max-heap con desempates canónicos reproducibles.
- **Actualización diferida (Lazy Updates):** Cuando un vértice $u^*$ es seleccionado, sus vecinos ven reducido su grado residual. En lugar de reestructurar el heap en $O(V)$, se inserta la nueva tupla con el grado actualizado. Al desapilar, si $(-deg \neq \text{len}(adj\_rem[v]))$, la entrada obsoleta se descarta o reinserta.
- **Complejidad resultante:** Cada arista se elimina exactamente una vez y desencadena a lo sumo una inserción en el heap. Costo total: $O((V + E) \log V)$.

---

## 4. Modificaciones Realizadas Respecto al Diseño Inicial

| Aspecto | Diseño Inicial (Avance 1 y 2) | Implementación Final (Avance 4) | Razón del Cambio |
|---|---|---|---|
| **Determinismo en desempates** | Selección por orden de iteración de `set` | Orden canónico estricto `_sorted_edges()` y `str(v)` en tuplas del heap | Python aleatoriza `PYTHONHASHSEED` entre procesos; sin orden canónico, las pruebas no eran reproducibles. |
| **Complejidad temporal** | Únicamente versión $O(V \cdot E)$ | Coexistencia de versión base $O(V \cdot E)$ y versión Heap $O((V+E)\log V)$ | Permite verificar equivalencia algorítmica y estudiar la mejora empírica de rendimiento. |
| **Métricas de ejecución** | Solo tiempo manual por `time.time()` | Medición con `time.perf_counter()` y memoria pico con `tracemalloc` | Precisión de microsegundos y evaluación del consumo de memoria exigido en la rúbrica. |
| **Manejo de entradas inválidas** | Excepciones genéricas `KeyError`/`ValueError` | `InvalidInstanceError` con mensajes estructurados | Robustez ante archivos mal formados presentados en sesión de evaluación. |

---

## 5. Pruebas Automatizadas y Validación

El conjunto de pruebas automatizadas (`pytest tests/ -v`) contiene pruebas enfocadas específicamente en este primer algoritmo:

### 5.1 Instancias Pequeñas y Validación Manual
- **Instancia del Avance 1 (`data/instances/example_small.json`):**
  - Red de 6 routers ($A, B, C, D, E, F$) y 6 enlaces.
  - Resolución manual: Vértice $A$ (grado 3), luego $E$ (grado 2), luego $B$ (grado 1).
  - Salida de `greedy_degree_vertex_cover`: $\{A, B, E\}$ (tamaño 3, óptimo).
  - Salida de `greedy_priority_queue_vertex_cover`: $\{A, B, E\}$ (tamaño 3, óptimo).
  - Ambas implementaciones coinciden exactamente con la derivación manual teórica.

### 5.2 Casos Límite
- **Grafo sin aristas ($E = \emptyset$):** Devuelve cobertura vacía $\emptyset$ inmediatamente sin iterar.
- **Una sola arista ($(A, B)$):** Devuelve un conjunto unitario ($\{A\}$ o $\{B\}$), validado con `is_vertex_cover`.
- **Vértices aislados:** Un router desconectado con grado 0 nunca ingresa a la cobertura.
- **Grafo completo $K_n$:** Devuelve $n - 1$ routers, que es el óptimo analítico.

### 5.3 Casos Adversos
- **Grafo Estrella ($K_{1, k}$):** Un concentrador central conectado a $k$ routers secundarios.
  - Greedy detecta inmediatamente al centro como el vértice de grado máximo ($k$) y lo selecciona.
  - Cobertura resultante: tamaño 1 (óptimo absoluto en 1 solo paso).
- **Grafos aleatorios parametrizados:** Validación sobre múltiples semillas comprobando que en el 100% de los casos las aristas pendientes quedan en 0 (`uncovered_edges == ∅`).

---

## 6. Demostración del Sistema

Para ejecutar y verificar el primer algoritmo desde consola:

```bash
# Ejecución sobre la instancia manual conocida
python demo.py --instance data/instances/example_small.json --algorithm greedy

# Ejecución de la versión optimizada con cola de prioridad
python demo.py --instance data/instances/example_small.json --algorithm greedy_pq

# Generación al vuelo de una red aleatoria
python demo.py --random 20 0.25 --seed 123 --algorithm greedy_pq
```

---

## 7. Dificultades Encontradas y Estado Actual

1. **Gestión de desempates en Heap:** Al usar un heap con tuplas `(-deg, v)`, si dos vértices tienen el mismo grado, Python intenta comparar `v`. Si los identificadores son de tipos mixtos (int y str), se producía un `TypeError`. Se corrigió almacenando `(-deg, str(v), v)` para asegurar comparabilidad total.
2. **Actualización de grados:** Mantener la sincronía del grado residual al eliminar aristas requería evitar que aristas compartidas se descuenten dos veces. Se solucionó con un mapa bidireccional de adyacencia residual (`adj_rem`).
3. **Estado:** El primer algoritmo y su estructura se encuentran completados, optimizados y con cobertura de pruebas al 100%.
