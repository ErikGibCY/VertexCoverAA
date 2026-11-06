# Guía de estudio — Bloque 1 (Fundamentos y Stack tecnológico)

> Material de estudio para la exposición. **Bloque 1 = §3.1 Fundamentos + §4 Stack + §5 Problema.**
> **Las tres partes están completas.** Duración total en vivo: ~4–5 minutos.
>
> Nota: este bloque NO expone bitácora, avances previos ni README. Solo el informe final y el código.

---

# PARTE 1 · FUNDAMENTOS (§3.1)

**Duración en vivo:** ~90 segundos. **Objetivo:** poner las bases conceptuales para que todo lo que siga (algoritmos, pruebas, resultados) tenga sentido.

## 1.1 Teoría de grafos básica

**Grafo no dirigido** `G = (V, E)`:
- `V` = routers/switches (vértices)
- `E` = enlaces físicos (aristas)
- No dirigido = `(A,B)` es lo mismo que `(B,A)`; el enlace es físico en ambos sentidos.

**Grado** `deg(v)` = número de aristas incidentes a `v`.

Mini-red de ejemplo (la misma en todos los bloques):

```
E = {(A,B), (A,C), (A,D), (B,C), (D,E), (E,F)}
```

| Vértice | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| **grado** | **3** | 2 | 2 | 2 | 2 | 1 |

**Dato util (handshaking lemma):** suma de grados = `2|E|`. Aquí `3+2+2+2+2+1 = 12 = 2×6` ✔

**Interpretación de red:** el grado es *cuántos enlaces vigila el router si lo monitoreas*. Por eso el vértice de mayor grado es el mejor candidato inicial → eso es exactamente lo que explota el **greedy** (Bloque 2).

## 1.2 Cobertura de vértices (Vertex Cover)

**Definición formal:**

> `C ⊆ V` es una **cobertura de vértices** si: **para toda `(u,v) ∈ E` se cumple `u ∈ C ∨ v ∈ C`**

**Problema de optimización:**

```
min |C|   sujeto a   C ⊆ V  y  ∀(u,v)∈E : u∈C ∨ v∈C
```

**Ejemplos rápidos (prepararlos, pueden pedirselos):**

| Conjunto | ¿Cubre? | Por qué |
|---|---|---|
| `{A, C, E}` | ✅ Sí | AB→A, AC→A, AD→A, BC→C, DE→E, EF→E |
| `{A, B, D, E}` | ✅ Sí | (lo que devuelve el matching) |
| `{F}` | ❌ No | F solo toca EF; quedan sin cubrir AB, AC, AD, BC, DE |
| `{A}` | ❌ No | Cubre AB, AC, AD pero no BC, DE, EF |

**Tres matices:**
1. **Cobertura válida ≠ cobertura mínima.** `V` entero (6) es válida, no óptima.
2. **Óptimo `|C*|`** = la cobertura más pequeña posible. Aquí `|C*| = 3` (ej. `{A,C,E}`).
3. **Minimal ≠ mínima:** *minimal* = si quitas cualquier vértice deja de ser cobertura; *mínima* = la de menor tamaño. El exacto garantiza **mínima (óptima)**.

## 1.3 Dualidad con Independent Set ⭐

**Conjunto independiente (stable set)** `I ⊆ V`: subconjunto **sin aristas entre sus miembros**.

**Teorema (informe §3.1):**

```
C es cobertura de vértices  ⟺  V \ C es un conjunto independiente
```

**Demostración (90 segundos — pregunta clásica), por contrapositiva:**

- **(⇒)** Si `C` es cobertura y `V\C` **NO** fuera independiente, existiría una arista `(u,v)` con ambos extremos en `V\C`, es decir, **ninguno** en `C` → contradice que `C` cubra esa arista. ∎
- **(⇐)** Si `V\C` es independiente, para cualquier arista `(u,v)` **no** pueden estar ambos en `V\C` → al menos uno está en `C`. ∎

**Verificación con la red real:**

| Cobertura `C` | `V\C` | ¿Aristas internas? | ¿Independiente? |
|---|---|---|---|
| `{A,C,E}` | `{B,D,F}` | ¿BD? ¿DF? ¿BF? → ninguna | ✅ |
| `{A,B,D,E}` | `{C,F}` | ¿CF? no está en E | ✅ |
| `{F}` | `{A,B,C,D,E}` | claro (AB, AC…) | ❌ (coherente: no era cobertura) |

**Por qué importa (respuesta «inteligente»):**
1. **Paso numérico:** `|C| + |V\C| = |V|`, luego `mínimo Vertex Cover = |V| − máximo Independent Set`. Uno resuelve al otro ⇒ mismamente difíciles.
2. **Paso de complejidad:** es la vía de la reducción (Clique/Independent Set → Vertex Cover) que muestra su NP-completitud. Karp (1972) lo incluyó en su lista de 21 problemas NP-completos.
3. **Paso práctico:** el proyecto puede discutir cobertura e independent set como dos caras del mismo problema.

> **Frase para exponer:** «Esta dualidad no es un detalle teórico: es lo que hace que el problema sea NP-completo, y por eso la guía pidió comparar estrategias en vez de buscar un algoritmo exacto polinomial.»

## 1.4 NP-completitud (§3.1)

| Clase | Significado | Analogía |
|---|---|---|
| **P** | se **resuelve** en tiempo polinomial | encontrar la salida de un laberinto de un solo camino |
| **NP** | una solución propuesta se **verifica** en polinomial | comprobar que un camino recorre todo el laberinto |
| **NP-difícil** | al menos tan duro como todo NP | un problema «subyacente» |
| **NP-completo** | NP-difícil **y** está en NP | el más duro de los verificables |

**¿Por qué Vertex Cover está en NP? → conexión directa con el código**

El certificado es `C`: verificarla toma `O(|E|)`. Eso es exactamente `src/verify.py`:

```python
return all(u in cover or v in cover for u, v in graph.edges)
```

> «Nuestro verificador lineal es, en la práctica, la prueba de que el problema está en NP.»

**¿Por qué es NP-difícil?** (versión para decir en voz alta)
- Karp (1972): reducción desde 3-SAT (y desde Clique/Independent Set vía la dualidad).
- Reducir = transformar cualquier instancia NP en una de Vertex Cover en polinomial. Si VC se resolviera en polinomial, **todo NP se resolvería** ⇒ `P = NP`.
- Se asume `P ≠ NP` ⇒ **no hay algoritmo exacto polinomial esperable**.

**Consecuencia que justifica todo el proyecto (§3.1):**

| Estrategia | ¿Rápida? | ¿Correcta? | Ejemplo del proyecto |
|---|---|---|---|
| **Exacta** | ❌ exponencial | ✅ óptima siempre | fuerza bruta `O(2^V·E)` — solo referencia |
| **Heurística** | ✅ | ✅ válida, **sin cota** | greedy por grado |
| **Aproximación con garantía** | ✅ | ✅ válida **y acotada** | matching maximal (≤ 2×) |

> **Frase de cierre:** «Por eso la línea asignada es *comparación de estrategias de aproximación*: la pregunta no es si existe un algoritmo óptimo eficiente —no existe—, sino cuánto se acerca cada alternativa rápida al óptimo y cuándo conviene cada una.»

## 1.5 Algoritmos de aproximación (§3.1)

**Definición de k-aproximación** (`k ≥ 1`): un algoritmo `A` es k-aprox si **para toda instancia**:

```
|A(I)| ≤ k · |OPT(I)|
```

- `k=1` → óptimo. `k=2` → nunca peor que el doble.
- **Ratio empírico** (lo que mide el proyecto: `|C_alg|/|C*|`) vs **cota demostrada** (la garantía del peor caso). **No son lo mismo** → es la tensión central del informe.

**Los 3 pasos de toda demostración de cota:**
1. Identificar una **estructura** que el algoritmo construye (en el matching: las aristas elegidas forman un *matching*, disjuntas).
2. **Cotar el óptimo por abajo** con esa estructura (`|C*| ≥ k`).
3. **Contar lo que devuelve** el algoritmo (`2k`) y comparar: `2k ≤ 2|C*|`.

> La demostración completa la expone el **Bloque 2**. Tú solo presentas el concepto y das el paso.

**Greedy: por qué no tiene cota.** En cada paso no conoce el futuro: elegir el mayor grado hoy puede dejar aristas caras después. Enunciado correcto: **«no tiene una cota constante demostrada en el peor caso general»**, **no** «es peor que el matching». Si insisten: *«existen instancias construidas para hacerlo mal; diseñarlas es trabajo pendiente (§12.4.6).»*

> 🔥 **Dato avanzado opcional (munición en preguntas):** por el teorema PCP, Vertex Cover **no puede aproximarse dentro de un factor `2−ε`** para ningún `ε>0` salvo que `P=NP` (Dinur & Steurer, 2014; antes Khot & Regev, 2008). O sea: **la cota 2× es en la práctica la mejor posible**. No está en el informe; decirlo como literatura adicional.

## 1.6 Complejidad con notación O(·) (§3.1)

`T(n) ∈ O(f(n))` = «a partir de cierto tamaño, el tiempo de peor caso crece como **mucho** como `f(n)`».

| Algoritmo | Complejidad | Intuición |
|---|---|---|
| Matching maximal | `O(V + E)` | cada arista se visita y elimina **una sola vez** |
| Greedy por grado | `O(V · E)` | hasta `V` iteraciones × recorrer `E` aristas para recalcular grados |
| Fuerza bruta | `O(C(V,k*)·E) ≤ O(2^V · E)` | el número de subconjuntos **se duplica** por vértice nuevo |

**El salto de escala (2^n):**

| n | 2^n |
|---|---|
| 6 | 64 |
| 18 | 262 144 |
| 20 | 1 048 576 |
| 30 | ~10⁹ |

> «Por eso el sistema **rechaza** las instancias de más de 20 vértices con `ValueError` en vez de colgarse.»

**Datos reales del proyecto:** de **0.02 ms** (`n=6`) a **173.90 ms** (`n=18`) → **≈ 8 700× con solo 12 vértices más**.

## 1.7 Fuentes (§3.2)

| Fuente | Para qué |
|---|---|
| Cormen et al., *Introduction to Algorithms* | complejidad `O(·)`, grafos |
| Vazirani, *Approximation Algorithms* | teoría de aproximación y garantías |
| Karp (1972) | NP-completitud de Vertex Cover |
| Docs oficiales (pytest, PuLP, NetworkX) | stack (Parte 2) |

Criterio de selección: *«texto estándar ampliamente citado»* y *«documentación oficial por ser la fuente autoritativa y vigente»*.

## 1.8 Qué es tuyo y qué NO en §3.3 (no pisarte con los demás)

| Conocimiento nuevo (§3.3) | Quién lo expone |
|---|---|
| Conceptos de NP, grafos, complejidad → los resumiste arriba | ✅ **TÚ** |
| Demostración formal de la cota 2× | ❌ Bloque 2 |
| `PYTHONHASHSEED` y el no-determinismo | ❌ Bloque 4 |
| Formulación ILP (`min Σx_v`, `x_u+x_v ≥ 1`) | ❌ Bloque 2 (mención) |
| `pytest` con `@parametrize` | ❌ Bloque 3 |

**No expones:** bitácora (§3.4), avances previos, README. Solo Q&A: *«la evidencia está en `docs/bitacora.md`, disponible si la quieren ver.»*

## 🎤 Guion de 60–90 segundos (fundamentos)

> «Empezamos por las bases. Modelamos la red como un **grafo no dirigido** `G=(V,E)`: routers y enlaces. El grado de un router es cuántos enlaces vigila si lo monitoreamos.
>
> Una **cobertura de vértices** es un subconjunto `C` tal que **cada arista tiene al menos un extremo** en `C`; buscamos la más pequeña. En nuestra mini-red, `{A,C,E}` cubre las 6 aristas, así que `|C*|=3`.
>
> La clave teórica es la **dualidad con Independent Set**: `C` es cobertura si y solo si `V\C` es un conjunto sin aristas internas — se demuestra en dos pasos por contrapositiva, y de ahí sale que mínimo vertex cover = `n` menos máximo independent set.
>
> Como Vertex Cover es **NP-completo** (Karp, 1972), no esperamos un algoritmo exacto polinomial. Noten que nuestro `is_vertex_cover` verifica una solución en tiempo lineal `O(E)` — eso es exactamente lo que pone al problema en NP.
>
> Por eso comparamos tres estrategias: una **exacta** exponencial solo como referencia, una **heurística** sin cota (greedy) y una **2-aproximación** con garantía demostrable (matching). Y para hablar de calidad usamos la **notación `O(·)`** y el **ratio de aproximación** `|C|/|C*|`.
>
> Con eso claro, pasemos al stack tecnológico con el que lo construimos.»

## ❓ 8 preguntas probables de fundamentos + respuesta modelo

1. **¿Por qué Vertex Cover modela la ubicación de IDS?** → *Un router monitoreado ve todo su tráfico, incluido el de cada enlace que toca; basta cubrir un extremo de cada enlace para inspeccionarlo, y minimizar `|C|` minimiza equipos y licencias.*
2. **Demuestra que `C` cobertura ⟺ `V\C` independiente.** → los dos pasos por contrapositiva de §1.3.
3. **¿Qué diferencia hay entre NP y NP-completo?** → *NP = verificable en polinomial; NP-completo = además NP-difícil (todo NP se reduce a él). Vertex Cover es NP-completo.*
4. **¿Cómo sabes que Vertex Cover está en NP?** → *porque el certificado es `C` y lo verificamos en `O(E)` con `is_vertex_cover`.*
5. **¿Qué significa que un algoritmo sea una k-aproximación?** → *`|A(I)| ≤ k·|OPT(I)|` para toda instancia: garantía del peor caso, no promedio observado.*
6. **¿Por qué el greedy no tiene cota y se usa igual?** → *no la tiene demostrada en el peor caso, pero se mide empíricamente; en nuestro experimento igualó al óptimo en 6 de 7 casos. Si se necesita garantía, se usa el matching.*
7. **¿Qué es peor: `O(V·E)` o `O(2^V)`?** → *la exponencial: duplica el trabajo por cada vértice nuevo; por eso el límite de 20 y los 0.02 ms → 173.90 ms observados.*
8. **¿Qué relación tiene la dualidad con la complejidad?** → *permite reducir Clique/Independent Set a Vertex Cover, la vía de su NP-completitud; además da `mín vertex cover = n − máx independent set`.*

---

# PARTE 2 · STACK TECNOLÓGICO (§4)

**Duración en vivo:** ~60–90 segundos. Estructura: **5 criterios → tabla de decisiones → procedimiento de aprendizaje → dificultades**.

## 2.1 Los 5 criterios de selección (§4.1)

Se aplican a **toda** la tabla: se enuncian **una vez** y luego «aplicando esos criterios…».

| # | Criterio | Por qué importa |
|---|---|---|
| **1** | **Instalación sin dependencias del sistema operativo** | Nada de compilar C ni `apt install`; todo con `pip install -r requirements.txt`, en Windows o Linux. Portabilidad + 0 fricción. |
| **2** | **Calidad y vigencia de la documentación oficial** | Documentación autoritativa > tutoriales de terceros que envejecen mal. Fuentes verificables. |
| **3** | **Curva de aprendizaje razonable para el tiempo disponible** | El proyecto dura un semestre; no se pierde tiempo en herramienta potente pero lenta de dominar. |
| **4** | **Adopción y soporte de la comunidad** | Herramienta viva = ayuda disponible, mantenimiento, empleabilidad. |
| **5** | **No añadir complejidad innecesaria al núcleo algorítmico** | ⭐ Instrucción adicional 5 de la guía: *«la interfaz es un medio de interacción y no reemplaza el núcleo algorítmico»*. |

> **Frase de puente:** «Aplicamos los mismos cinco criterios a todas las decisiones, para que la comparación fuera justa y no caprichosa.»

## 2.2 La tabla de decisiones: 7 filas

### Fila 1 · Lenguaje — Python 3 · Java · C++ → **Python 3**
Justificación: sintaxis concisa para prototipado; `set`/`dict` nativos encajan con la lista de adyacencia `dict[v] -> set[v]`; es la configuración de referencia de la guía.

**Si preguntan «¿y no C++ por la velocidad?»:** *«El eje es comparar estrategias, no velocidad absoluta: medimos en milisegundos y comparamos algoritmos entre sí, y eso vale en cualquier lenguaje. El cuello de botella real es la fuerza bruta exponencial, que lo sería igual en C++ (es `O(2^V)`, no un problema de lenguaje). Y Python permitió que los cuatro pudiéramos leer y explicar el código, que es requisito del proyecto.»*

### Fila 2 · Pruebas — pytest · unittest → **pytest**
Justificación: `assert` plano (más legible); **parametrización nativa** `@pytest.mark.parametrize` → repetir una verificación sobre 10 grafos aleatorios sin duplicar código; adopción y documentación.

**Si preguntan «unittest viene incluido»:** *«Sí, y hablaba a favor del criterio 1. Pero pesó el 5: `unittest` exige clases y boilerplate y su parametrización no es directa; como nuestro plan adversarial depende de correr una misma verificación sobre muchas instancias, `pytest` reducía y aclaraba el código de prueba.»*

### Fila 3 · Grafos — NetworkX · implementación propia → **Propia en el núcleo** ⭐
Justificación: (1) control total sobre la complejidad → poder afirmar «este paso es `O(V+E)`»; (2) requisito pedagógico → dominio individual, hay que explicar cada línea.
NetworkX no se rechaza: se **posterga** a lo que aporta sin distraer (visualización).

**Respuesta modelo a «¿no es re-inventar la rueda?»:** *«Es un trade-off consciente. Re-inventamos exactamente una rueda pequeña: la lista de adyacencia, ~160 líneas que **necesitamos** entender para poder afirmar la complejidad de nuestros algoritmos. NetworkX trae miles de líneas que no usamos en el núcleo. La regla fue: **implemento lo que debo dominar, uso la biblioteca para lo que solo necesito consumir** — exactamente lo que dice la instrucción 5.»*

### Fila 4 · Solver ILP — PuLP · OR-Tools → **PuLP** (tecnología emergente, AG-C06.02)
Justificación: instala **CBC embebido** (criterio 1); API declarativa casi idéntica a la formulación:

```python
prob += pulp.lpSum(x.values())     # min Σ x_v
prob += x[u] + x[v] >= 1           # para cada arista (u,v)
x = {v: pulp.LpVariable(f"x_{v}", cat="Binary")}
```

OR-Tools: curva de aprendizaje mayor sin beneficio proporcional (criterio 3).

**Honestidad del estado:** *«En esta entrega PuLP está elegido y bosquejado, pendiente de integración y validación: la entrega no incluye el solver ILP.»* → pasas la mano: *«la implementación concreta es parte de la Entrega 2.»*

### Fila 5 · Datos y gráficos — **pandas + matplotlib**
Estándar de facto, documentación extensa, **suficiente** para decenas–cientos de filas. No hace falta nada exótico.

### Fila 6 · Versiones — **Git + GitHub**
Exigido por la guía (instrucción adicional 3). El historial de commits es evidencia de evolución real, no una subida final.

### Fila 7 · Documentación — **LaTeX + Markdown**
LaTeX para documentos formales (control tipográfico de fórmulas, pseudocódigo, tablas); Markdown para bitácora y notas (se edita rápido y hace diffs claros en Git).

### Resumen para diapositiva

| Necesidad | Candidatas | Decisión | Por qué (criterio) |
|---|---|---|---|
| Lenguaje | Python / Java / C++ | **Python 3** | `set`+`dict` nativos, prototipado, referencia de la guía (1,3) |
| Pruebas | pytest / unittest | **pytest** | `assert` plano + parametrización (3,4) |
| Grafos | NetworkX / propia | **Propia (núcleo)** | control de complejidad + dominio (5) |
| Solver ILP | PuLP / OR-Tools | **PuLP** | CBC embebido, API declarativa (1,3) |
| Datos y gráficos | pandas / matplotlib | **ambos** | estándar, suficiente (2,4) |
| Versiones | Git / GitHub | **Git+GitHub** | exigido por la guía, historial = evidencia (—) |
| Documentación | LaTeX / Markdown | **ambos** | LaTeX para fórmulas, Markdown para diffs (2,5) |

## 2.3 §4.2 · Procedimiento de aprendizaje e integración (4 pasos)

```
1. Leer la documentación oficial de inicio rápido
2. Escribir un script MÍNIMO de prueba FUERA del proyecto
3. Integrarla al proyecto real
4. Cubrirla con al menos una prueba automatizada
```

**Ejemplo concreto obligatorio:** *«La sintaxis de `@pytest.mark.parametrize` se validó primero en un archivo de prueba aislado, antes de usarla en `tests/test_solver.py`.»*

Por qué importa: el paso 2 evita contaminar el proyecto con un error de principiante; el paso 4 convierte la adquisición en algo verificable.

> **Frase:** «No aprendimos a usar las herramientas dentro del proyecto; aprendimos afuera y luego las integramos con una prueba que demuestra que funcionan.»

## 2.4 §4.3 · Dificultades de adopción

**Dificultad 1 — la más significativa NO fue una biblioteca, fue el lenguaje:** el no-determinismo al iterar `set()` en Python.
⚠️ **No desarrollar:** es material del **Bloque 4 (§11.2)**. Solo:
> «La dificultad de adopción más importante no vino de una biblioteca, sino del propio lenguaje. La investigaron y corrigieron mis compañeros; ellos les cuentan el detalle en la parte de análisis.»

**Dificultad 2 — `babel-spanish` de LaTeX no disponible** (una frase y ya): no se pudo instalar en el entorno de compilación; se prescindió de `babel` y se ajustó a mano los anchos de columna y cortes de línea en las tablas. Marco: priorizar el núcleo sobre una herramienta no esencial (instrucción 5). Si insisten: *«los PDFs se compilan correctamente; fue un ajuste manual de maquetación.»*

## 2.5 Idea central (el hilo de §4)

1. **Cero fricción para instalar** → criterio 1.
2. **Máxima legibilidad para aprender** → criterios 2, 3, 5.
3. **Cero acoplamiento en el núcleo** → criterio 5 + (§7.5, lo desarrolla el Bloque 3).

### ⚠️ Matiz trampa: «pero `requirements.txt` trae 5 librerías»
> *«Hay que distinguir el **núcleo** de las **capas periféricas**. `src/graph.py`, `src/solver.py` y `src/verify.py` usan solo biblioteca estándar. `pytest` es para `tests/`; `pandas`/`matplotlib`/`networkx` son candidatas de apoyo; y `pulp` es una **extensión opcional**: está importado dentro del método ILP en un `try/except`, así que si no está instalado ese método avisa y **el resto del sistema sigue funcionando**. Ese es justo el objetivo: núcleo auditable y sin puntos de fallo externos.»*

## 🎤 Guion de 70 segundos (stack tecnológico)

> «Las herramientas no las elegimos por gusto: aplicamos **cinco criterios** — instalación sin dependencias del sistema, documentación oficial vigente, curva de aprendizaje dentro del tiempo disponible, adopción de la comunidad, y no añadir complejidad al núcleo algorítmico, que es lo que pide la guía.
>
> Con ellos decidimos: **Python 3**, porque `set` y `dict` nativos encajan con la lista de adyacencia y es la configuración de referencia; **pytest** por el `assert` plano y su parametrización, que usamos para repetir una misma verificación sobre 10 grafos aleatorios; **implementación propia para el núcleo** en vez de NetworkX, porque necesitamos controlar y poder explicar la complejidad de cada paso — NetworkX queda para visualización; **PuLP** para el solver ILP, porque trae CBC embebido y su API se parece a la formulación matemática; **pandas y matplotlib** para datos, **Git+GitHub** exigido por la guía, y **LaTeX** con **Markdown** para documentar.
>
> Cada herramienta nueva siguió el mismo procedimiento: leer la documentación oficial, probarla en un script aislado fuera del proyecto, integrarla y cubrirla con una prueba. El ejemplo: la parametrización de `pytest` se validó aislada antes de usarse en `tests/test_solver.py`.
>
> La mayor dificultad, por cierto, no vino de una biblioteca sino del propio lenguaje — eso lo desarrollarán en la parte de análisis. Ahora pasemos al problema que resolvemos.»

## ❓ Preguntas probables de stack + respuesta modelo

1. **¿Por qué no C++/Java?** → comparar estrategias, no velocidad absoluta; el cuello de botella es exponencial; requisito de dominio individual.
2. **¿Por qué no NetworkX? ¿Re-inventar la rueda?** → *implemento lo que debo dominar, uso la biblioteca para lo que solo consumo.*
3. **¿`unittest` no viene incluido?** → parametrización + legibilidad pesaron más que evitar una instalación de una línea.
4. **PuLP u OR-Tools?** → CBC embebido, API declarativa; OR-Tools: más curva sin beneficio proporcional.
5. **¿Cuál criterio pesó más?** → el **5**, porque es exigencia de la guía: la herramienta no puede contaminar el núcleo.
6. **¿Cómo saben que la elección fue buena?** → 27 pruebas automatizadas pasando, experimento reproducible con semillas fijas y resultados en CSV.
7. **«Si Python es lento, ¿sirven sus tiempos?»** → los tiempos se comparan **entre algoritmos en el mismo entorno**; el crecimiento observado lo produce la complejidad exponencial, no el lenguaje.
8. **¿Qué harían distinto?** → lockfile de versiones exactas y usar el ILP desde el inicio para comparar en rangos mayores.

## 🚫 Qué NO tocar en esta parte

| Tema de §4 | Dueño |
|---|---|
| Detalle del no-determinismo / `PYTHONHASHSEED` | Bloque 4 (solo anunciar) |
| Implementación y validación del ILP con PuLP | Bloque 2 (solo decir que es la tecnología elegida) |
| §7.5 «el núcleo sin dependencias externas» | Bloque 3 (idea general una vez) |
| Visualización con NetworkX | Entrega 2 → no mencionar |

---

---

# PARTE 3 · PROBLEMA (§5)

**Duración en vivo:** ~2 minutos (la más larga del Bloque 1, porque incluye la instancia resuelta a mano).
**Objetivo:** dejar *cerrado* el problema: qué entra, qué sale, qué reglas se cumplen, qué se asume, qué se minimiza, y probarlo en un caso concreto.

## 3.1 §5.1 Modelo — ¿por qué un grafo?

La topología se representa como un **grafo no dirigido** `G = (V, E)`:
- `V` = routers/switches
- `E` = enlaces físicos

**¿Por qué grafo?** El problema es de *relación entre pares*: importa qué está conectado con qué, nada más.
**¿Por qué no dirigido?** El enlace físico es simétrico (el tráfico va en ambos sentidos) y **un router monitoreado ve lo que entra y lo que sale**. Dirigirlo duplicaría aristas sin cambiar la solución: cada enlace sigue necesitando un extremo.

> *«El grafo es la abstracción exacta del problema: no se pierde nada de la topología y no se añade nada que no importe.»*

## 3.2 §5.2 Entradas

1. **Un grafo `G=(V,E)` en formato JSON** (el formato es §7.4 → lo expone el **Bloque 2**).
2. **(Extensión futura, NO implementada)** **costo de instalación por nodo** → **variante ponderada**.

### ⭐ La variante ponderada (pregunta asegurada)
«¿Y si un router cuesta más que otro?» → **Weighted Vertex Cover**: `min Σ cost(v)`; la restricción no cambia. **No está implementado**: es entrada válida del modelo pero **fuera del alcance de esta entrega**.

## 3.3 §5.3 Salidas

| Salida | ¿Por qué se pide? |
|---|---|
| **`C ⊆ V`** | es la **respuesta**: qué routers monitorear. |
| **`\|C\|` de cada algoritmo** | ⭐ porque el proyecto es **comparación**: sin tamaño no hay comparación. |
| **Verificación booleana** | porque un conjunto con el tamaño correcto **puede no cubrir**; hay que demostrar que es válido. |

> *«No basta devolver el conjunto: hay que devolverlo **y comprobarlo**. Esa tercera salida es la que hace confiables los resultados.»*

## 3.4 §5.4 Restricciones

```
1.  C ⊆ V                        (solo routers que existen)
2.  ∀(u,v) ∈ E : u ∈ C ∨ v ∈ C   (cada enlace, al menos un extremo)
```

**Frase potente:** en la mini-red son solo **6 `or`**. El problema no es difícil por la restricción, sino porque el número de conjuntos posibles es **exponencial**: $\binom{6}{3}=20$, pero en una red real $\binom{100}{50}\approx10^{29}$. **Ahí está la raíz de la NP-completitud, en una frase.**

## 3.5 §5.5 Supuestos — los tres y qué pasa si se violan

| # | Supuesto | ¿Si se viola? |
|---|---|---|
| **1** | Topología **estática** durante el cálculo | Si cambia (enlace caído, router nuevo) → **re-ejecutar**. La solución no queda incorrecta, queda **desactualizada**. |
| **2** | Grafo **no dirigido y no ponderado** | Dirigido → aristas dobles. Ponderado → **variante ponderada** con algoritmos distintos (el 2× ya no aplica tal cual). |
| **3** | Un router monitoreado detecta el tráfico de **todos** sus enlaces directos | Si solo viera algunos, la restricción 2 deja de bastar → dejaría de ser Vertex Cover. |

> *«Supuestos explícitos = límites explícitos. Los tres están escritos en el informe para que se sepa hasta dónde llega la solución.»*

## 3.6 §5.6 Función objetivo

$$\min_{C \subseteq V} |C| \quad \text{sujeto a} \quad \forall (u,v)\in E:\; u \in C \;\lor\; v \in C$$

1. Es **minimización**, no satisfacción: hay muchas válidas, buscamos la más pequeña.
2. El «sujeto a» **es** la restricción 2 escrita en fórmula.
3. Es un problema de optimización combinatorio **NP-difícil** → de ahí la necesidad de comparar estrategias (Parte 1).

## 3.7 §5.7 La instancia resuelta a mano ⭐ (el corazón del Bloque 1)

> Esta traza la **conoces de memoria**: la confirma el código (Bloque 2) y la reportan los resultados (Bloque 4).

**Red:** `V = {A,B,C,D,E,F}`, `E = {(A,B),(A,C),(A,D),(B,C),(D,E),(E,F)}`
**Grados iniciales:** A=3, B=2, C=2, D=2, E=2, F=1

### 🔹 GREEDY por grado — 3 pasos

| Paso | Pendientes | Grados (solo pendientes) | Elige | Elimina |
|---|---|---|---|---|
| 1 | `AB,AC,AD,BC,DE,EF` | **A=3**, B=2, C=2, D=2, E=2, F=1 | **A** | AB, AC, AD |
| 2 | `BC,DE,EF` | B=1, C=1, D=1, **E=2**, F=1 | **E** | DE, EF |
| 3 | `BC` | **B=1**, C=1 (empate) | **B** | BC |

→ `C_greedy = {A, E, B}`, **|C| = 3** ✅

⚠️ Paso 3: **empate B vs C** (el informe dice «B o C, indistinto»). En el sistema ese empate se resuelve por un **orden canónico fijo** para ser reproducible → **una frase; el detalle es del Bloque 2**.

### 🔹 MATCHING MAXIMAL — 2 pasos

| Paso | Toma | Agrega | Elimina | Quedan |
|---|---|---|---|---|
| 1 | `(A,B)` | A, B | las que tocan A o B → `AB,AC,AD,BC` | `DE, EF` |
| 2 | `(D,E)` | D, E | las que tocan D o E → `DE,EF` | — |

→ `C_match = {A,B,D,E}`, **|C| = 4** ✅

**Por qué es más «caro»:** cubre todo, pero paga **dos vértices por arista elegida**, mientras el greedy paga solo el que más rinde.

### 🔹 Óptimo de referencia

`C* = {A, C, E}`, **|C*| = 3** → verificación: `AB→A`, `AC→A`, `AD→A`, `BC→C`, `DE→E`, `EF→E` ✔

### ⭐ «¿Cómo sabes que 3 es óptimo y no 2?» (pregunta dura)

> *«Basta ver que 2 no alcanza. Si la cobertura **no** incluye `A`, hay que cubrir `AB, AC, AD` por sus otros extremos → `B, C, D` = 3 ya. Si **sí** incluye `A`, quedan sin cubrir `BC`, `DE` y `EF`; `BC` exige `B` o `C`, que no tocan `DE` ni `EF`, así que hacen falta **al menos 2 más**. Total: `1 + 2 = 3`. Y `{A,C,E}` lo logra ⇒ `|C*| = 3`.»*

**Refuerzo:** la fuerza bruta prueba `k=1` (6 subconjuntos), `k=2` (15), y en `k=3` encuentra uno → lo confirma **por exhaustividad**.

### 🚨 El matiz que nadie espera (te salva la vida)

La salida **real** de `demo.py` es `Exacto: ['A','B','E']  Tamano: 3`, pero el informe dice que el óptimo es `{A,C,E}`. ¿Contradicción? **No**:

`{A,B,E}` también cubre las 6 aristas y también tiene 3 vértices (`AB→A, AC→A, AD→A, BC→B, DE→E, EF→E` ✔).

> 🎯 *«El óptimo **no es único**: lo único único es su **tamaño**. Hay varias coberturas óptimas de tamaño 3 y el algoritmo exacto devuelve **una** de ellas, no **la**. Por eso comparamos **tamaños**, no conjuntos.»*

(Además explica por qué el greedy → ratio **1.000×**: acertó un óptimo.)

### 📊 Tabla final §5.7

| Algoritmo | Cobertura | Tamaño | vs óptimo (3) |
|---|---|---|---|
| Greedy por grado | `{A, B, E}` | **3** | Óptimo en esta instancia |
| Matching maximal (2-approx) | `{A, B, D, E}` | **4** | **1.33×** |
| Exacto (referencia) | `{A, C, E}` | 3 | — |

### 🎯 La «observación comparativa» = la tesis de TODO el proyecto

> *«Heurística **sin garantía formal** pero **buen desempeño práctico**, frente a aproximación con **garantía matemática** pero **subóptima en casos concretos** — ese contraste es el eje de la comparación experimental.»*

Dila casi textual: conecta tu bloque con los tres restantes.

## 🎤 Guion de 2 minutos (problema + ejemplo)

> *«El problema. Modelamos la red como un **grafo no dirigido** `G=(V,E)`: routers y enlaces. La **entrada** es ese grafo en JSON; la **salida** son tres cosas: el conjunto `C` de routers a monitorear, **su tamaño** — porque el proyecto es comparación —, y una **verificación booleana** de que realmente cubre todo.*
>
> *Las **restricciones** son dos: `C` solo puede contener routers existentes, y **cada enlace debe tener al menos un extremo en `C`**. La **función objetivo** es minimizar `|C|` bajo esa restricción.*
>
> *Los **supuestos** son explícitos: topología estática, grafo **no dirigido y no ponderado**, y que un router monitoreado ve **todos** sus enlaces directos. Si alguno falla, sabemos qué se rompe: el ponderado llevaría a una variante distinta que está identificada pero fuera de alcance.*
>
> *Y esto se ve en una **instancia de 6 routers**. Greedy: primero `A` por grado 3, luego `E`, luego `B` → **3 vértices**. Matching maximal: `(A,B)` y luego `(D,E)` → **4 vértices**. El óptimo es **3**, lo confirma el algoritmo exacto.*
>
> *Fíjense: el greedy **igualó al óptimo**, el matching quedó en **1.33 veces**… y aun así **ambos son coberturas válidas**. Ahí está el contraste central: **heurística sin garantía pero buena en la práctica**, frente a **aproximación con garantía matemática pero subóptima en casos concretos**. Eso es lo que mediremos experimentalmente.*
>
> *Con el problema cerrado, paso a los algoritmos que lo resuelven.»*

## ❓ Preguntas probables del problema + respuesta modelo

1. **¿Por qué grafo no dirigido?** → enlace simétrico; el IDS ve tráfico en ambos sentidos; dirigirlo duplica aristas sin cambiar la solución.
2. **¿Y si los enlaces/routers tienen distinto costo?** → **variante ponderada** (`min Σ cost(v)`), identificada como extensión futura, **fuera del alcance**.
3. **¿Y si la red cambia durante el cálculo?** → supuesto de topología estática; se re-ejecuta. No queda incorrecta, queda **desactualizada**.
4. **¿Cómo sabes que el óptimo es 3?** → demostración `1+2≥3` + fuerza bruta exhaustiva.
5. **¿Por qué el matching da más?** → paga **dos extremos por arista**; el greedy paga el vértice más rinde. El matching compra **garantía**, el greedy **eficiencia**.
6. **¿La cobertura óptima es única?** → **No**: `{A,C,E}` y `{A,B,E}` (tamaño 3). Comparamos **tamaños**. ⭐
7. **¿Un router aislado?** → nunca entra en la cobertura; no cubre nada y solo empeoraría `|C|` (lo cubre `test_vertices_aislados_no_aparecen_en_la_cobertura`).
8. **¿Grafo desconectado?** → la definición no lo exige; se resuelve componente por componente (`test_componentes_desconectadas`).
9. **¿Por qué verificar si el algoritmo es correcto?** → la corrección es un argumento, la verificación es **evidencia en cada corrida**; un bug podría devolver el tamaño correcto sin cubrir.
10. **¿Miden el conjunto o el tamaño?** → el **tamaño** y el **ratio**, porque los conjuntos pueden diferir siendo igualmente óptimos.

## 🚫 Qué NO tocar en esta parte

| Tema | Dueño |
|---|---|
| Detalle del formato JSON (§7.4) | Bloque 2 → solo «en formato JSON» |
| Salida de `demo.py` / validación (§10.1) | Bloque 4 |
| Orden canónico en empates (`_sorted_edges`) | Bloque 2 / 4 → 1 frase |
| Demostración de la cota 2× | Bloque 2 |

---

# Resumen del Bloque 1 completo

| Parte | Sección | En vivo | Tu frase clave |
|---|---|---|---|
| 1 | Fundamentos (§3.1) | ~90 s | «Por eso comparamos estrategias: no existe el algoritmo exacto polinomial.» |
| 2 | Stack (§4) | ~70 s | «Implemento lo que debo dominar, uso la biblioteca para lo que solo consumo.» |
| 3 | Problema (§5) | ~120 s | «Heurística sin garantía vs. aproximación con garantía: ese es el eje.» |
| | **Apertura + cierre de preguntas** | +30 s | moderas el Q&A y cedes el paso al Bloque 2 |
| | **Total** | **~5 min** | |
