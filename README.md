# Adaptación Del Algoritmo De Murciélago Al Permutation Flow Shop Scheduling Problem Para La Minimización Del Makespan

Proyecto del curso Analisis y Diseno de Algoritmos. El repositorio implementa en C++ una metaheuristica Bat Algorithm para resolver el Permutation Flow Shop Scheduling Problem (PFSP), minimizando el makespan.

## Integrantes

- Marcelo Landa
- Cesar Lujan
- Franco Melchor
- Frank Tapia

## Estructura del repositorio

```text
src/
  main.cpp             Entrada por linea de comandos y escritura de resultados
  pfsp.h / pfsp.cpp    Carga de instancias, makespan y cronograma Gantt
  bat.h / bat.cpp      Bat Algorithm adaptado a permutaciones con SPV y busqueda local
instancias/
  instancia1_bas1.txt
  instancia2_car5.txt
  instancia3_reC01.txt
scripts/
  ejecutar_escenarios.py   Compila y ejecuta los 5 escenarios sobre las 3 instancias
  graficar.py              Genera figuras desde los CSV de resultados
resultados/
  CSV y figuras generadas para las corridas base y los escenarios
```

## Requisitos

- `g++` con soporte C++17.
- Python 3.
- `matplotlib` para generar figuras.

## Compilacion

```powershell
g++ -O2 -Wall -std=c++17 src\pfsp.cpp src\bat.cpp src\main.cpp -o pfsp.exe
```

## Ejecucion manual

```powershell
.\pfsp.exe instancias\instancia1_bas1.txt --runs 10 --seed 42 --out resultados
.\pfsp.exe instancias\instancia2_car5.txt --runs 10 --seed 42 --out resultados
.\pfsp.exe instancias\instancia3_reC01.txt --runs 10 --seed 42 --out resultados
```

Opciones principales:

| Opcion | Descripcion | Defecto |
|---|---|---:|
| `--iter N` | Iteraciones maximas | 500 |
| `--pob N` | Tamano de poblacion | 30 |
| `--runs N` | Corridas independientes | 1 |
| `--seed S` | Semilla base | 42 |
| `--fmin X` | Frecuencia minima | 0.0 |
| `--fmax X` | Frecuencia maxima | 2.0 |
| `--A0 X` | Sonoridad inicial | 1.0 |
| `--r0 X` | Tasa de emision inicial | 0.5 |
| `--alfa X` | Reduccion de sonoridad | 0.9 |
| `--gamma X` | Crecimiento de emision | 0.9 |
| `--out DIR` | Carpeta de salida | `resultados` |
| `--eval "1 2 3"` | Evalua una secuencia y termina | - |

## Ejecutar todos los escenarios

```powershell
python scripts\ejecutar_escenarios.py
```

El script recompila `pfsp.exe`, ejecuta 5 escenarios sobre las 3 instancias con `--runs 10 --seed 42` y genera:

- `resultados\escenarios\resumen_escenarios.csv`
- `resultados\escenarios\resumen_escenarios.md`
- CSV de convergencia, Gantt y resumen por instancia dentro de cada escenario.

## Generar figuras

```powershell
python scripts\graficar.py resultados --formatos png pdf
python scripts\graficar.py resultados\escenarios --recursive --formatos png pdf
```

Genera curvas de convergencia, diagramas de Gantt y figuras comparativas en las carpetas de resultados.

## Escenarios evaluados

| Escenario | Poblacion | Iteraciones | fmax | r0 | alfa | gamma | Enfoque |
|---|---:|---:|---:|---:|---:|---:|---|
| E1_base | 30 | 500 | 2.00 | 0.50 | 0.90 | 0.90 | Linea base |
| E2_mayor_diversidad | 50 | 300 | 2.00 | 0.50 | 0.90 | 0.90 | Mayor poblacion |
| E3_mayor_profundidad | 20 | 750 | 2.00 | 0.50 | 0.90 | 0.90 | Mas iteraciones |
| E4_exploracion_alta | 30 | 500 | 3.00 | 0.80 | 0.95 | 0.50 | Exploracion global |
| E5_explotacion_local | 30 | 500 | 1.00 | 0.20 | 0.90 | 1.50 | Busqueda local |

## Resultados base

Corrida con parametros por defecto, `--runs 10 --seed 42`.

| Instancia | Tamano | Mejor | Peor | Promedio | Desv. est. |
|---|---:|---:|---:|---:|---:|
| instancia1_bas1 | 5x4 | 52 | 52 | 52.00 | 0.00 |
| instancia2_car5 | 10x6 | 7720 | 8076 | 7818.70 | 98.93 |
| instancia3_reC01 | 20x5 | 1249 | 1390 | 1282.80 | 48.22 |

## Mejores escenarios por instancia

| Instancia | Mejor escenario | Mejor | Promedio | Desv. est. | Gap mejor |
|---|---|---:|---:|---:|---:|
| instancia1_bas1 | E4_exploracion_alta | 52 | 52.00 | 0.00 | 0.00% |
| instancia2_car5 | E3_mayor_profundidad | 7720 | 7815.50 | 94.96 | 0.00% |
| instancia3_reC01 | E4_exploracion_alta | 1249 | 1269.30 | 27.19 | 0.16% |

## Archivos de salida

- `convergencia_<instancia>.csv`: mejor makespan por iteracion.
- `gantt_<instancia>.csv`: trabajo, maquina, inicio y fin de cada operacion.
- `resumen_<instancia>.csv`: makespan, tiempo y secuencia por corrida.
- `*.png` y `*.pdf`: figuras generadas desde los CSV.
