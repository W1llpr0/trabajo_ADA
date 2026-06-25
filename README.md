# PFSP con el Algoritmo de Murciélago (Bat Algorithm)

Proyecto del curso **Análisis y Diseño de Algoritmos** (Eval 3, grupo G3): implementación en C++ del **Bat Algorithm** (Yang, 2010) adaptado al **Permutation Flow Shop Scheduling Problem (PFSP)** para minimizar el **makespan**.

## Estructura del proyecto

```
src/
  pfsp.h / pfsp.cpp    Carga de instancias, cálculo del makespan y cronograma (Gantt)
  bat.h / bat.cpp      Algoritmo de Murciélago (variante híbrida SPV + búsqueda local)
  main.cpp             Interfaz de línea de comandos y escritura de resultados
scripts/
  graficar.py          Genera las gráficas (convergencia y Gantt) desde los CSV
instancias/            Instancias de prueba (.txt)
resultados/            Salidas: CSV y PNG
compilar.bat           Script de compilación con g++
```

## Compilación

Requiere `g++` (C++17) en el PATH:

```
compilar.bat
```

o manualmente:

```
g++ -O2 -Wall -std=c++17 src\pfsp.cpp src\bat.cpp src\main.cpp -o pfsp_bat.exe
```

## Ejecución

```
pfsp_bat.exe <instancia.txt> [opciones]
```

| Opción | Descripción | Defecto |
|---|---|---|
| `--iter N` | Iteraciones máximas (criterio de parada) | 500 |
| `--pob N` | Tamaño de la población de murciélagos | 30 |
| `--runs N` | Número de ejecuciones independientes | 1 |
| `--seed S` | Semilla base (la ejecución i usa S+i) | 42 |
| `--fmin X` | Frecuencia minima | 0.0 |
| `--fmax X` | Frecuencia maxima | 2.0 |
| `--A0 X` | Sonoridad inicial | 1.0 |
| `--r0 X` | Tasa de emision inicial | 0.5 |
| `--alfa X` | Factor de reduccion de sonoridad | 0.9 |
| `--gamma X` | Factor de crecimiento de emision | 0.9 |
| `--out DIR` | Carpeta de salida de los CSV | `resultados` |
| `--eval "1 2 3 ..."` | Evalúa el makespan de una secuencia dada (1-based) y termina | — |

### Reproducir los experimentos del informe (10 ejecuciones por instancia)

```
pfsp_bat.exe instancias\instancia1_bas1.txt --runs 10
pfsp_bat.exe instancias\instancia2_car5.txt --runs 10
pfsp_bat.exe instancias\instancia3_reC01.txt --runs 10
```

### Estudio de escenarios ParametrosBA

Para comparar parametros de forma reproducible se agrego un ejecutor automatico:

```
python scripts\ejecutar_escenarios.py
```

El script compila el proyecto, ejecuta 5 escenarios sobre las 3 instancias con `--runs 10 --seed 42` y genera:

- `resultados/escenarios/resumen_escenarios.csv` -- tabla consolidada para analisis.
- `resultados/escenarios/resumen_escenarios.md` -- tabla Markdown lista para el informe.

Mejores escenarios observados con esta corrida:

| Instancia | Mejor escenario | Mejor | Promedio | Desv. est. | Gap mejor |
|---|---|---:|---:|---:|---:|
| instancia1_bas1 | E4_exploracion_alta | 52 | 52.00 | 0.00 | 0.00 % |
| instancia2_car5 | E3_mayor_profundidad | 7720 | 7815.50 | 94.96 | 0.00 % |
| instancia3_reC01 | E4_exploracion_alta | 1249 | 1269.30 | 27.19 | 0.16 % |

Las semillas son reproducibles: con los mismos parámetros y semilla se obtiene siempre el mismo resultado.

### Archivos generados (en `resultados/`)

- `convergencia_<instancia>.csv` — mejor makespan global por iteración (curva de convergencia de la mejor ejecución).
- `gantt_<instancia>.csv` — trabajo, máquina, inicio y fin de cada operación de la mejor solución.
- `resumen_<instancia>.csv` — makespan, tiempo y secuencia de cada ejecución (solo con `--runs > 1`).

## Gráficas

Requiere Python con `matplotlib`:

```
python scripts\graficar.py resultados
```

Genera los PNG de las curvas de convergencia y los diagramas de Gantt junto a cada CSV.

## Adaptación del Bat Algorithm al PFSP

El BA original opera en espacios continuos; el PFSP requiere permutaciones. La adaptación usada es la **variante híbrida SPV + búsqueda local**:

1. Cada murciélago mantiene una **posición continua** `x ∈ R^n` y una velocidad `v`, actualizadas con las ecuaciones originales de Yang: `f = fmin + (fmax−fmin)·β`, `v ← v + (x − x*)·f`, `x ← x + v`.
2. La posición se decodifica a permutación con la regla **SPV** (*Smallest Position Value*): los trabajos se ordenan por valor ascendente de su componente en `x`.
3. El "vuelo aleatorio local" alrededor de la mejor solución se reemplaza por operadores de **swap/insert** sobre la mejor permutación (con probabilidad `1 − r`).
4. Una solución que mejora se acepta con probabilidad ligada a la sonoridad `A`; al aceptar, `A` decrece (`A ← α·A`) y la tasa de emisión crece (`r ← r0·(1 − e^(−γ·t))`), pasando de exploración a explotación.
5. El makespan se evalúa con la recurrencia `C[i][j] = max(C[i−1][j], C[i][j−1]) + p[i][j]`.

Parámetros por defecto: población 30, 500 iteraciones, `fmin=0`, `fmax=2`, `A0=1.0`, `r0=0.5`, `α=0.9`, `γ=0.9`.

## Resultados de referencia (semilla base 42, 10 ejecuciones)

| Instancia | Tamaño | Mejor | Peor | Promedio | Desv. est. | Tiempo prom. |
|---|---|---|---|---|---|---|
| instancia1_bas1 | 5×4 | 52 | 52 | 52.00 | 0.00 | ~3 ms |
| instancia2_car5 | 10×6 | 7720 | 8076 | 7818.70 | 98.93 | ~5 ms |
| instancia3_reC01 | 20×5 | 1249 | 1390 | 1282.80 | 48.22 | ~8 ms |

Para `reC01` (benchmark de Reeves) el óptimo conocido es **1247**; el mejor resultado obtenido (1249) representa un gap del 0.16 %.

## Referencia

Yang, X.-S. (2010). *A New Metaheuristic Bat-Inspired Algorithm*. En: Nature Inspired Cooperative Strategies for Optimization (NICSO 2010), Studies in Computational Intelligence, vol. 284, Springer.
