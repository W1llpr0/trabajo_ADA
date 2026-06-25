# Material para el informe técnico — Bat Algorithm aplicado al PFSP

Este documento reúne todo el contenido derivado del código y de los experimentos, organizado según las secciones del informe que dependen de la implementación (secciones 4 a 9 de la estructura exigida). Las tablas están listas para copiar al Word; los textos son insumos para redactar con sus propias palabras.

---

## Sección 4 del informe: Adaptación del algoritmo al PFSP

### El problema de fondo

El Bat Algorithm (Yang, 2010) fue diseñado para optimización **continua**: cada murciélago es un punto en R^n que se mueve con ecuaciones de frecuencia, velocidad y posición. El PFSP, en cambio, es un problema **combinatorio** cuyas soluciones son permutaciones de trabajos. La adaptación elegida es la **variante híbrida SPV + búsqueda local**, que conserva intactas las ecuaciones originales y agrega una capa de decodificación.

### Representación de las soluciones

Cada murciélago mantiene dos representaciones acopladas:

- **Posición continua** `x ∈ R^n` (una componente por trabajo) y velocidad `v ∈ R^n`, sobre las que operan las ecuaciones originales del BA.
- **Permutación de trabajos**, obtenida con la regla **SPV** (*Smallest Position Value*, Tasgetiren et al., 2004): los trabajos se ordenan por valor ascendente de su componente en `x`. Ejemplo con n=5: si `x = (2.7, 0.4, 3.1, 1.5, 0.9)`, la permutación es [J2, J5, J4, J1, J3], porque x₂=0.4 es el menor valor, luego x₅=0.9, etc.

La ventaja de SPV es que **cualquier** vector continuo decodifica a una permutación válida: nunca se generan soluciones infactibles, sin necesidad de reparación.

### Generación de soluciones iniciales

Población de N=30 murciélagos con posiciones aleatorias uniformes en [0, n] y velocidad cero. Al decodificar con SPV, esto equivale a 30 permutaciones aleatorias uniformes. Cada uno conserva su sonoridad inicial A₀=1.0 y tasa de emisión r₀=0.5.

### Operadores sobre permutaciones (búsqueda local)

El BA original incluye un "vuelo aleatorio local" alrededor de la mejor solución (`x_nuevo = x_mejor + ε·A`). Como ese paso es el responsable de la intensificación, se reemplazó por operadores propios de permutaciones aplicados a la **mejor solución global**:

- **Swap**: intercambiar los trabajos de dos posiciones aleatorias (probabilidad 0.5).
- **Insert**: extraer el trabajo de una posición e insertarlo en otra (probabilidad 0.5).

Tras la búsqueda local, la posición continua del murciélago se reconstruye de forma coherente con la permutación obtenida (asignando a cada trabajo su índice de posición), de modo que SPV(x) reproduce exactamente esa permutación y los vuelos posteriores parten de un punto consistente.

### Función objetivo (evaluación)

El makespan de una permutación se calcula con la recurrencia del enunciado:

```
C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j]
```

implementada con un único vector de tamaño m (arreglo rodante): al procesar la posición i, `C[j]` aún contiene el tiempo de liberación de la máquina j (fila anterior) y `C[j-1]` ya contiene el fin del trabajo actual en la máquina previa. Complejidad: **O(n·m)** por evaluación con memoria O(m).

### Mecánica exploración → explotación

- Con probabilidad `1 − r[k]` el murciélago hace búsqueda local sobre la mejor global (explotación); en caso contrario vuela con sus ecuaciones (exploración).
- Una solución que **mejora** al murciélago se acepta solo si `rand < A[k]`. Al aceptar: `A ← α·A` (grita más bajo) y `r ← r₀·(1 − e^(−γ·t))` (pulsa más rápido). El efecto neto: al inicio domina la exploración global y, conforme se aceptan mejoras, el algoritmo se concentra en refinar la mejor solución.
- **Elitismo**: si un candidato supera a la mejor global, se adopta inmediatamente.

### Parámetros y criterio de parada

| Parámetro | Valor | Rol |
|---|---|---|
| Población N | 30 | Número de murciélagos (soluciones simultáneas) |
| Iteraciones máx. | 500 | **Criterio de parada** |
| f_min, f_max | 0, 2 | Rango de frecuencias (magnitud del movimiento) |
| A₀ | 1.0 | Sonoridad inicial (probabilidad de aceptar mejoras) |
| r₀ | 0.5 | Tasa de emisión inicial (controla cuánta búsqueda local) |
| α | 0.9 | Factor de reducción de la sonoridad |
| γ | 0.9 | Velocidad de crecimiento de la tasa de emisión |
| Semilla | 42 + i | Reproducibilidad (la ejecución i usa semilla 42+i) |

Los valores de f, A₀, r₀, α y γ son los recomendados por Yang (2010). El presupuesto total es 30 × 500 = **15,000 evaluaciones del makespan por ejecución**.

---

## Sección 5 del informe: Pseudocódigo

```
ALGORITMO BatAlgorithm-PFSP
Entrada: matriz de tiempos p (n trabajos × m máquinas), parámetros (N, T, fmin, fmax, A0, r0, α, γ)
Salida: mejor permutación π* y su makespan

1.  PARA cada murciélago k = 1..N:
2.      x[k] ← vector aleatorio uniforme en [0, n]^n;  v[k] ← 0
3.      A[k] ← A0;  r[k] ← r0
4.      π[k] ← SPV(x[k])                            // decodificar a permutación
5.      fit[k] ← makespan(π[k])
6.  (π*, fit*) ← mejor de la población;  x* ← x del mejor
7.  PARA t = 1..T:                                   // criterio de parada: T iteraciones
8.      PARA cada murciélago k = 1..N:
9.          f ← fmin + (fmax − fmin)·β,  β ~ U(0,1)  // frecuencia
10.         v[k] ← v[k] + (x[k] − x*)·f              // velocidad (atracción al mejor)
11.         x_cand ← x[k] + v[k]                     // posición candidata
12.         SI rand > r[k]:                          // búsqueda local (explotación)
13.             π_cand ← vecino(π*)                  // swap o insert sobre la mejor global
14.             x_cand ← posición coherente con π_cand
15.         SINO:
16.             π_cand ← SPV(x_cand)
17.         fit_cand ← makespan(π_cand)
18.         SI fit_cand ≤ fit[k] Y rand < A[k]:      // aceptación por sonoridad
19.             (x[k], π[k], fit[k]) ← candidato
20.             A[k] ← α·A[k];  r[k] ← r0·(1 − e^(−γ·t))
21.         SI fit_cand < fit*:                      // actualizar mejor global (elitismo)
22.             (π*, fit*, x*) ← candidato;  el murciélago k lo adopta
23.     registrar fit* (curva de convergencia)
24. DEVOLVER (π*, fit*)
```

---

## Sección 6 del informe: Descripción de la implementación

### Estructura del código (C++17, ~470 líneas)

| Módulo | Archivos | Responsabilidad |
|---|---|---|
| Problema | `src/pfsp.h`, `src/pfsp.cpp` | `struct Instancia`, carga del .txt con validación, `makespan()`, `calcularGantt()` |
| Algoritmo | `src/bat.h`, `src/bat.cpp` | Clase `BatAlgorithm` con los métodos privados `spv()`, `vecino()`, `posicionDesdePerm()` y el método público `ejecutar()` |
| Interfaz | `src/main.cpp` | Línea de comandos, ejecuciones múltiples, cronometraje, estadísticas, escritura de CSV |

Diseño: el módulo del problema no conoce al algoritmo; la clase `BatAlgorithm` solo depende de `pfsp.h` y encapsula su estado (instancia, parámetros, generador aleatorio `std::mt19937`). Los datos puros (`Instancia`, `ParametrosBA`, `ResultadoBA`, `Operacion`) son structs sin lógica.

### Carga de archivos de entrada

Formato: primera línea `n m`; luego una línea por trabajo con m pares `(índice_de_máquina, tiempo)`. `cargarInstancia()` valida apertura del archivo, dimensiones positivas, datos completos e índices de máquina en rango, lanzando excepciones descriptivas si algo falla.

### Generación de resultados

El programa imprime en consola la mejor secuencia (formato J1..Jn), el makespan, el tiempo (cronometrado con `std::chrono::steady_clock`) y los parámetros; y escribe en `resultados/`:

- `convergencia_<instancia>.csv` — mejor makespan global por iteración.
- `gantt_<instancia>.csv` — trabajo, máquina, inicio y fin de cada operación de la mejor solución.
- `resumen_<instancia>.csv` — makespan, semilla, tiempo y secuencia de cada ejecución (modo `--runs`).

Un script auxiliar (`scripts/graficar.py`, matplotlib) convierte los CSV en las figuras del informe. El modo `--eval "1 2 3 ..."` permite verificar manualmente el makespan de cualquier secuencia (útil para el video).

### Compilación y ejecución

```
g++ -O2 -Wall -std=c++17 src\pfsp.cpp src\bat.cpp src\main.cpp -o pfsp_bat.exe
pfsp_bat.exe instancias\instancia1_bas1.txt --runs 10
python scripts\graficar.py resultados
```

---

## Sección 7 del informe: Experimentación

### Condiciones de las pruebas

| Aspecto | Detalle |
|---|---|
| Hardware | Intel Core i5-12450H (12.ª gen.), 32 GB RAM |
| Sistema operativo | Windows 11 |
| Compilador | g++ 15.2.0 (MSYS2), flags `-O2 -Wall -std=c++17` |
| Ejecuciones por instancia | 10, con semillas 42 a 51 (reproducibles) |
| Parámetros | N=30, T=500, fmin=0, fmax=2, A₀=1.0, r₀=0.5, α=0.9, γ=0.9 |

### Estudio de sensibilidad de ParametrosBA

Adicionalmente se probaron 5 escenarios de parametros, manteniendo 10 ejecuciones por instancia y semilla base 42. Los escenarios comparan la linea base con mayor diversidad poblacional, mayor profundidad iterativa, mayor exploracion global y mayor explotacion local. La comparacion usa como criterio principal el menor makespan promedio; ante empate, menor desviacion estandar y luego menor tiempo promedio.

| Escenario | Proposito | Parametros principales |
|---|---|---|
| E1_base | Linea base actual | N=30, T=500, fmax=2, r0=0.5, alfa=0.9, gamma=0.9 |
| E2_mayor_diversidad | Mas poblacion con presupuesto similar | N=50, T=300 |
| E3_mayor_profundidad | Mas iteraciones con presupuesto similar | N=20, T=750 |
| E4_exploracion_alta | Favorecer exploracion global | fmax=3, r0=0.8, alfa=0.95, gamma=0.5 |
| E5_explotacion_local | Favorecer busqueda local | fmax=1, r0=0.2, alfa=0.9, gamma=1.5 |

### Instancias

| Instancia | Trabajos × Máquinas | Archivo | Espacio de búsqueda | Origen |
|---|---|---|---|---|
| Pequeña | 5 × 4 | instancia1_bas1.txt | 5! = 120 | — |
| Mediana | 10 × 6 | instancia2_car5.txt | 10! ≈ 3.6×10⁶ | car5 (Carlier, 1978) |
| Grande | 20 × 5 | instancia3_reC01.txt | 20! ≈ 2.4×10¹⁸ | reC01 (Reeves, 1995) |

---

## Sección 8 del informe: Resultados

### Resultados por ejecución — Instancia pequeña (instancia1_bas1)

| Ejec. | Semilla | Makespan | Tiempo (ms) | Mejor secuencia |
|---|---|---|---|---|
| 1 | 42 | 52 | 3.22 | [J2, J4, J5, J3, J1] |
| 2 | 43 | 52 | 3.17 | [J2, J4, J5, J1, J3] |
| 3 | 44 | 52 | 3.57 | [J2, J4, J5, J1, J3] |
| 4 | 45 | 52 | 3.74 | [J2, J4, J5, J3, J1] |
| 5 | 46 | 52 | 3.32 | [J2, J4, J5, J3, J1] |
| 6 | 47 | 52 | 3.22 | [J5, J2, J4, J1, J3] |
| 7 | 48 | 52 | 3.28 | [J5, J2, J4, J3, J1] |
| 8 | 49 | 52 | 3.33 | [J2, J4, J5, J3, J1] |
| 9 | 50 | 52 | 3.19 | [J2, J4, J5, J1, J3] |
| 10 | 51 | 52 | 3.07 | [J2, J4, J5, J3, J1] |

Nota: el problema tiene varios óptimos alternativos (distintas secuencias con makespan 52).

### Resultados por ejecución — Instancia mediana (instancia2_car5)

| Ejec. | Semilla | Makespan | Tiempo (ms) | Mejor secuencia |
|---|---|---|---|---|
| 1 | 42 | 7835 | 7.68 | [J4, J1, J2, J3, J7, J10, J5, J6, J9, J8] |
| 2 | 43 | 7821 | 5.43 | [J5, J6, J4, J3, J1, J10, J2, J7, J9, J8] |
| 3 | 44 | 7738 | 5.65 | [J6, J2, J4, J1, J3, J8, J10, J9, J7, J5] |
| 4 | 45 | 7821 | 7.48 | [J5, J6, J4, J3, J1, J7, J10, J2, J9, J8] |
| 5 | 46 | 7821 | 4.75 | [J5, J3, J4, J1, J10, J2, J6, J7, J9, J8] |
| 6 | 47 | 8076 | 5.89 | [J1, J3, J6, J2, J4, J10, J9, J8, J7, J5] |
| 7 | 48 | 7821 | 4.58 | [J5, J3, J4, J1, J6, J9, J7, J10, J2, J8] |
| 8 | 49 | **7720** | 4.05 | [J5, J4, J2, J1, J3, J8, J6, J10, J9, J7] |
| 9 | 50 | 7767 | 4.26 | [J3, J4, J5, J1, J10, J2, J8, J6, J9, J7] |
| 10 | 51 | 7767 | 4.14 | [J4, J5, J3, J1, J10, J2, J8, J6, J9, J7] |

### Resultados por ejecución — Instancia grande (instancia3_reC01)

| Ejec. | Semilla | Makespan | Tiempo (ms) |
|---|---|---|---|
| 1 | 42 | 1255 | 7.64 |
| 2 | 43 | **1249** | 5.50 |
| 3 | 44 | 1319 | 5.68 |
| 4 | 45 | 1326 | 5.94 |
| 5 | 46 | 1251 | 9.91 |
| 6 | 47 | **1249** | 7.29 |
| 7 | 48 | 1289 | 8.36 |
| 8 | 49 | **1249** | 8.16 |
| 9 | 50 | 1251 | 7.44 |
| 10 | 51 | 1390 | 13.53 |

Mejor secuencia (ejec. 2): [J6, J9, J17, J15, J18, J12, J2, J20, J14, J11, J7, J3, J13, J4, J1, J5, J10, J8, J16, J19]

### Tabla resumen (formato exigido en la sección 5.2 del enunciado)

| Instancia | Mejor makespan | Peor makespan | Promedio | Desv. estándar | Tiempo promedio | Mejor secuencia |
|---|---|---|---|---|---|---|
| Pequeña | 52 | 52 | 52.00 | 0.00 | 3.31 ms | [J2, J4, J5, J3, J1] |
| Mediana | 7720 | 8076 | 7818.70 | 98.93 | 5.39 ms | [J5, J4, J2, J1, J3, J8, J6, J10, J9, J7] |
| Grande | 1249 | 1390 | 1282.80 | 48.22 | 7.94 ms | [J6, J9, J17, J15, J18, J12, J2, J20, J14, J11, J7, J3, J13, J4, J1, J5, J10, J8, J16, J19] |

(Desviación estándar muestral, n−1.)

### Resultados del estudio de sensibilidad

Resumen de los mejores escenarios por instancia, usando menor promedio como criterio principal:

| Instancia | Mejor escenario | Mejor | Peor | Promedio | Desv. est. | Tiempo prom. | Gap mejor |
|---|---|---:|---:|---:|---:|---:|---:|
| Pequeña | E4_exploracion_alta | 52 | 52 | 52.00 | 0.00 | 2.28 ms | 0.00 % |
| Mediana | E3_mayor_profundidad | 7720 | 8047 | 7815.50 | 94.96 | 3.02 ms | 0.00 % |
| Grande | E4_exploracion_alta | 1249 | 1313 | 1269.30 | 27.19 | 4.41 ms | 0.16 % |

La instancia pequeña no discrimina parametros porque todos los escenarios alcanzan el optimo. En la mediana, aumentar iteraciones con menor poblacion mejora ligeramente el promedio frente a la linea base. En la grande, el escenario de exploracion alta reduce el promedio de 1282.80 a 1269.30 y baja la desviacion de 48.22 a 27.19, por lo que es la configuracion mas estable para reC01 aunque mantiene el mismo mejor makespan 1249.

Los datos completos quedan en `resultados/escenarios/resumen_escenarios.csv` y `resultados/escenarios/resumen_escenarios.md`.

### Verificación de optimalidad (punto fuerte para el informe)

Para validar la calidad de las soluciones se implementó un verificador por **enumeración exhaustiva** (fuerza bruta sobre todas las permutaciones):

| Instancia | Óptimo verificado | Resultado del BA | Gap |
|---|---|---|---|
| Pequeña | 52 (exacto, 120 permutaciones) | 52 en 10/10 ejecuciones | **0 %** |
| Mediana | 7720 (exacto, 3.6M permutaciones) | 7720 (mejor de 10) | **0 %** |
| Grande | 1247 (mejor valor conocido en la literatura para reC01; fuerza bruta inviable: 2.4×10¹⁸) | 1249 | **0.16 %** |

### Curvas de convergencia (figuras: `resultados/convergencia_*.png`)

Comportamiento medido sobre la mejor ejecución de cada instancia:

| Instancia | Makespan inicial (iter. 1) | Makespan final | Última iteración con mejora |
|---|---|---|---|
| Pequeña | 52 | 52 | 1 (óptimo en la población inicial / primera iteración) |
| Mediana | 8378 | 7720 | 124 de 500 |
| Grande | 1400 | 1249 | 220 de 500 |

### Diagrama de Gantt (figuras: `resultados/gantt_*.png`)

Generados a partir de los tiempos de inicio/fin de cada operación de la mejor solución (`gantt_<instancia>.csv`). Cada figura muestra las máquinas (filas), los trabajos (barras de colores con etiqueta), los tiempos de inicio y fin, y el makespan final marcado con línea roja. El máximo tiempo de fin del cronograma coincide con el makespan reportado (verificación de coherencia exigida en la sección 5.4 del enunciado).

---

## Sección 9 del informe: Análisis y discusión (argumentos)

**Calidad de las soluciones.** El algoritmo alcanzó el óptimo exacto (verificado por enumeración) en las instancias pequeña y mediana, y quedó a 0.16 % del mejor valor conocido en la grande. El contraste clave: en reC01 se evaluaron 15,000 permutaciones de un espacio de 2.4×10¹⁸ (fracción ~10⁻¹⁴) — la búsqueda guiada por la metaheurística logra lo que el muestreo aleatorio o la fuerza bruta no podrían.

**Estabilidad entre ejecuciones.** La variabilidad crece con el tamaño de la instancia: desviación 0.00 (pequeña), 98.93 = 1.3 % del promedio (mediana), 48.22 = 3.8 % del rango (grande). Causa: cada semilla parte de una población distinta, y el esquema sonoridad/tasa de emisión hace que el algoritmo se comprometa pronto con una región del espacio; si esa región contiene solo un óptimo local (p. ej. la ejecución 10 de reC01, makespan 1390), ya no hay mecanismo fuerte de escape. Por eso la metodología exige 10 ejecuciones y análisis estadístico: la calidad de una metaheurística estocástica se evalúa en distribución, no en una corrida.

**Forma de la curva de convergencia.** Las curvas muestran caída abrupta inicial y estabilización temprana (última mejora en las iteraciones 1, 124 y 220 respectivamente). Esto NO indica mal funcionamiento: la curva grafica el mejor-hasta-el-momento (monótona no creciente por definición) y se aplana porque el algoritmo alcanza el óptimo o un valor muy cercano — en las instancias pequeña y mediana está demostrado que es el óptimo exacto, de modo que la línea no puede bajar más. La forma "caída rápida + meseta" es la firma de la transición exploración→explotación del BA (sonoridad decreciente, tasa de emisión creciente).

**Tiempo de ejecución.** Crece con el tamaño (3.31 → 5.39 → 7.94 ms) pero se mantiene en milisegundos: la evaluación del makespan es O(n·m) con arreglo rodante, y el presupuesto es fijo (15,000 evaluaciones). El costo por evaluación domina, por eso el tiempo escala aproximadamente con n·m (20, 60, 100 celdas).

**Influencia de los parámetros.** El estudio de sensibilidad confirma que los parametros cambian sobre todo la estabilidad. En la instancia grande, `E4_exploracion_alta` mantuvo el mismo mejor makespan de la linea base (1249), pero redujo el promedio de 1282.80 a 1269.30 y la desviacion de 48.22 a 27.19. Esto sugiere que aumentar la exploracion global (`fmax=3`, `r0=0.8`, `alfa=0.95`, `gamma=0.5`) ayuda a evitar estancamientos tempranos en reC01. En la instancia mediana, `E3_mayor_profundidad` fue ligeramente mejor por promedio, lo que indica que mas iteraciones con menor poblacion puede ser suficiente cuando el espacio es mas pequeño.

**Relación tiempo/resultado.** Para estas instancias, 500 iteraciones son más que suficientes (mejoras concentradas en el primer 44 % de la ejecución). En instancias mayores (p. ej. 50×20 de Taillard) convendría aumentar T o añadir un mecanismo de reinicio/diversificación cuando la búsqueda se estanca.

**Limitaciones y mejoras futuras** (para Conclusiones): (1) el esquema de aceptación solo admite mejoras, lo que acelera la convergencia pero favorece óptimos locales — podría relajarse al estilo recocido simulado; (2) la búsqueda local usa un solo vecino por llamada — una variante con exploración del vecindario completo (best-improvement) o con NEH como solución inicial probablemente cerraría el gap de la instancia grande; (3) la calibracion aun cubre solo 5 escenarios discretos; para trabajos futuros se podria ampliar a una busqueda factorial o a mas instancias de benchmark.

---

## Datos sueltos útiles

- **Reproducibilidad**: cualquier resultado del informe se regenera con `pfsp_bat.exe instancias\<archivo> --runs 10` (semilla base 42 por defecto). Verificado: misma semilla → resultado idéntico.
- **Makespan de la secuencia identidad** [J1..J5] en la instancia pequeña: 57 (útil como ejemplo de cálculo manual en la sección 3 del informe; la tabla C completa puede generarse con `--eval "1 2 3 4 5"` y el CSV de Gantt).
- El óptimo de la instancia mediana tiene empates: la fuerza bruta encontró [J4, J5, J2, J1, J3, J8, J6, J10, J9, J7] y el BA [J5, J4, J2, J1, J3, J8, J6, J10, J9, J7] — ambas con makespan 7720 (difieren solo en el orden de J4/J5).

## Referencias sugeridas (formato APA)

- Yang, X.-S. (2010). A new metaheuristic bat-inspired algorithm. En J. R. González et al. (Eds.), *Nature Inspired Cooperative Strategies for Optimization (NICSO 2010)* (Studies in Computational Intelligence, Vol. 284, pp. 65–74). Springer.
- Tasgetiren, M. F., Sevkli, M., Liang, Y.-C., & Gencyilmaz, G. (2004). Particle swarm optimization algorithm for permutation flowshop sequencing problem. En *Ant Colony Optimization and Swarm Intelligence (ANTS 2004)* (Lecture Notes in Computer Science, Vol. 3172, pp. 382–389). Springer. *(origen de la regla SPV)*
- Carlier, J. (1978). Ordonnancements à contraintes disjonctives. *RAIRO - Operations Research, 12*(4), 333–350. *(instancia car5)*
- Reeves, C. R. (1995). A genetic algorithm for flowshop sequencing. *Computers & Operations Research, 22*(1), 5–13. *(instancia reC01)*
- Johnson, S. M. (1954). Optimal two- and three-stage production schedules with setup times included. *Naval Research Logistics Quarterly, 1*(1), 61–68. *(clásico del flow shop, útil para la introducción)*
