"""
Ejecuta escenarios de calibracion para ParametrosBA y consolida resultados.

Uso recomendado:
    python scripts/ejecutar_escenarios.py

Salidas principales:
    resultados/escenarios/resumen_escenarios.csv
    resultados/escenarios/resumen_escenarios.md
"""

from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


INSTANCIAS = [
    {
        "nombre": "instancia1_bas1",
        "ruta": Path("instancias") / "instancia1_bas1.txt",
        "optimo": 52,
    },
    {
        "nombre": "instancia2_car5",
        "ruta": Path("instancias") / "instancia2_car5.txt",
        "optimo": 7720,
    },
    {
        "nombre": "instancia3_reC01",
        "ruta": Path("instancias") / "instancia3_reC01.txt",
        "optimo": 1247,
    },
]

ESCENARIOS = [
    {
        "nombre": "E1_base",
        "objetivo": "Linea base actual",
        "params": {
            "pob": 30,
            "iter": 500,
            "fmin": 0.0,
            "fmax": 2.0,
            "A0": 1.0,
            "r0": 0.5,
            "alfa": 0.9,
            "gamma": 0.9,
        },
    },
    {
        "nombre": "E2_mayor_diversidad",
        "objetivo": "Mas poblacion con presupuesto similar",
        "params": {
            "pob": 50,
            "iter": 300,
            "fmin": 0.0,
            "fmax": 2.0,
            "A0": 1.0,
            "r0": 0.5,
            "alfa": 0.9,
            "gamma": 0.9,
        },
    },
    {
        "nombre": "E3_mayor_profundidad",
        "objetivo": "Mas iteraciones con presupuesto similar",
        "params": {
            "pob": 20,
            "iter": 750,
            "fmin": 0.0,
            "fmax": 2.0,
            "A0": 1.0,
            "r0": 0.5,
            "alfa": 0.9,
            "gamma": 0.9,
        },
    },
    {
        "nombre": "E4_exploracion_alta",
        "objetivo": "Favorecer exploracion global",
        "params": {
            "pob": 30,
            "iter": 500,
            "fmin": 0.0,
            "fmax": 3.0,
            "A0": 1.0,
            "r0": 0.8,
            "alfa": 0.95,
            "gamma": 0.5,
        },
    },
    {
        "nombre": "E5_explotacion_local",
        "objetivo": "Favorecer busqueda local",
        "params": {
            "pob": 30,
            "iter": 500,
            "fmin": 0.0,
            "fmax": 1.0,
            "A0": 1.0,
            "r0": 0.2,
            "alfa": 0.9,
            "gamma": 1.5,
        },
    },
]

CSV_COLUMNS = [
    "escenario",
    "objetivo",
    "instancia",
    "poblacion",
    "iteraciones",
    "fmin",
    "fmax",
    "A0",
    "r0",
    "alfa",
    "gamma",
    "runs",
    "seed",
    "mejor",
    "peor",
    "promedio",
    "desv_est",
    "tiempo_prom_ms",
    "gap_mejor_pct",
    "mejor_secuencia",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta los 5 escenarios de ParametrosBA sobre las 3 instancias."
    )
    parser.add_argument("--runs", type=int, default=10, help="Ejecuciones por instancia.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla base reproducible.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("resultados") / "escenarios",
        help="Carpeta base para resultados consolidados.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="No recompila pfsp_bat.exe antes de ejecutar escenarios.",
    )
    return parser.parse_args()


def compilar(root: Path, exe: Path) -> None:
    cmd = [
        "g++",
        "-O2",
        "-Wall",
        "-std=c++17",
        str(root / "src" / "pfsp.cpp"),
        str(root / "src" / "bat.cpp"),
        str(root / "src" / "main.cpp"),
        "-o",
        str(exe),
    ]
    print("Compilando pfsp_bat.exe...")
    subprocess.run(cmd, cwd=root, check=True)


def comando_escenario(
    exe: Path,
    instancia: Path,
    out_dir: Path,
    params: Dict[str, float],
    runs: int,
    seed: int,
) -> List[str]:
    cmd = [
        str(exe),
        str(instancia),
        "--runs",
        str(runs),
        "--seed",
        str(seed),
        "--out",
        str(out_dir),
    ]
    for nombre in ("iter", "pob", "fmin", "fmax", "A0", "r0", "alfa", "gamma"):
        cmd.extend([f"--{nombre}", str(params[nombre])])
    return cmd


def leer_resumen(ruta_csv: Path) -> Tuple[int, int, float, float, float, str]:
    filas = []
    with ruta_csv.open(newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            filas.append(fila)

    if not filas:
        raise RuntimeError(f"El resumen esta vacio: {ruta_csv}")

    makespans = [int(fila["makespan"]) for fila in filas]
    tiempos = [float(fila["tiempo_ms"]) for fila in filas]
    mejor = min(makespans)
    peor = max(makespans)
    promedio = statistics.mean(makespans)
    desv = statistics.stdev(makespans) if len(makespans) > 1 else 0.0
    tiempo_prom = statistics.mean(tiempos)
    mejor_fila = min(filas, key=lambda fila: int(fila["makespan"]))
    return mejor, peor, promedio, desv, tiempo_prom, mejor_fila["secuencia"]


def ejecutar(root: Path, exe: Path, out_base: Path, runs: int, seed: int) -> List[Dict[str, object]]:
    resultados: List[Dict[str, object]] = []
    out_base.mkdir(parents=True, exist_ok=True)

    for escenario in ESCENARIOS:
        escenario_dir = out_base / escenario["nombre"]
        escenario_dir.mkdir(parents=True, exist_ok=True)
        params = escenario["params"]

        for instancia in INSTANCIAS:
            print(f"Ejecutando {escenario['nombre']} / {instancia['nombre']}...")
            cmd = comando_escenario(
                exe=exe,
                instancia=root / instancia["ruta"],
                out_dir=escenario_dir,
                params=params,
                runs=runs,
                seed=seed,
            )
            proc = subprocess.run(
                cmd,
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if proc.returncode != 0:
                print(proc.stdout)
                raise RuntimeError(
                    f"Fallo {escenario['nombre']} / {instancia['nombre']} "
                    f"con codigo {proc.returncode}"
                )

            resumen = escenario_dir / f"resumen_{instancia['nombre']}.csv"
            mejor, peor, promedio, desv, tiempo_prom, secuencia = leer_resumen(resumen)
            optimo = instancia["optimo"]
            gap = ((mejor - optimo) / optimo) * 100.0 if optimo else 0.0
            resultados.append(
                {
                    "escenario": escenario["nombre"],
                    "objetivo": escenario["objetivo"],
                    "instancia": instancia["nombre"],
                    "poblacion": params["pob"],
                    "iteraciones": params["iter"],
                    "fmin": params["fmin"],
                    "fmax": params["fmax"],
                    "A0": params["A0"],
                    "r0": params["r0"],
                    "alfa": params["alfa"],
                    "gamma": params["gamma"],
                    "runs": runs,
                    "seed": seed,
                    "mejor": mejor,
                    "peor": peor,
                    "promedio": promedio,
                    "desv_est": desv,
                    "tiempo_prom_ms": tiempo_prom,
                    "gap_mejor_pct": gap,
                    "mejor_secuencia": secuencia,
                }
            )
    return resultados


def escribir_csv(ruta: Path, filas: Iterable[Dict[str, object]]) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for fila in filas:
            salida = dict(fila)
            for clave in ("promedio", "desv_est", "tiempo_prom_ms", "gap_mejor_pct"):
                salida[clave] = f"{float(salida[clave]):.2f}"
            writer.writerow(salida)


def fmt_num(valor: object) -> str:
    numero = float(valor)
    if numero.is_integer():
        return str(int(numero))
    return f"{numero:.2f}"


def mejor_por_instancia(filas: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    mejores: Dict[str, Dict[str, object]] = {}
    for fila in filas:
        instancia = str(fila["instancia"])
        actual = mejores.get(instancia)
        if actual is None:
            mejores[instancia] = fila
            continue
        clave_fila = (
            float(fila["promedio"]),
            float(fila["desv_est"]),
            float(fila["tiempo_prom_ms"]),
        )
        clave_actual = (
            float(actual["promedio"]),
            float(actual["desv_est"]),
            float(actual["tiempo_prom_ms"]),
        )
        if clave_fila < clave_actual:
            mejores[instancia] = fila
    return mejores


def escribir_markdown(ruta: Path, filas: List[Dict[str, object]]) -> None:
    mejores = mejor_por_instancia(filas)
    lineas = [
        "# Resumen de escenarios ParametrosBA",
        "",
        "Criterio de seleccion: menor promedio; en empate, menor desviacion y luego menor tiempo.",
        "",
        "## Mejores escenarios por instancia",
        "",
        "| Instancia | Escenario | Mejor | Promedio | Desv. est. | Tiempo prom. ms | Gap mejor % |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for instancia in sorted(mejores):
        fila = mejores[instancia]
        lineas.append(
            "| {instancia} | {escenario} | {mejor} | {promedio:.2f} | {desv:.2f} | "
            "{tiempo:.2f} | {gap:.2f} |".format(
                instancia=instancia,
                escenario=fila["escenario"],
                mejor=fila["mejor"],
                promedio=float(fila["promedio"]),
                desv=float(fila["desv_est"]),
                tiempo=float(fila["tiempo_prom_ms"]),
                gap=float(fila["gap_mejor_pct"]),
            )
        )

    lineas.extend(
        [
            "",
            "## Tabla completa",
            "",
            "| Escenario | Instancia | Pob. | Iter. | fmax | r0 | alfa | gamma | Mejor | Peor | Promedio | Desv. est. | Tiempo ms | Gap % |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for fila in filas:
        lineas.append(
            "| {escenario} | {instancia} | {poblacion} | {iteraciones} | {fmax} | {r0} | "
            "{alfa} | {gamma} | {mejor} | {peor} | {promedio:.2f} | {desv:.2f} | "
            "{tiempo:.2f} | {gap:.2f} |".format(
                escenario=fila["escenario"],
                instancia=fila["instancia"],
                poblacion=fila["poblacion"],
                iteraciones=fila["iteraciones"],
                fmax=fmt_num(fila["fmax"]),
                r0=fmt_num(fila["r0"]),
                alfa=fmt_num(fila["alfa"]),
                gamma=fmt_num(fila["gamma"]),
                mejor=fila["mejor"],
                peor=fila["peor"],
                promedio=float(fila["promedio"]),
                desv=float(fila["desv_est"]),
                tiempo=float(fila["tiempo_prom_ms"]),
                gap=float(fila["gap_mejor_pct"]),
            )
        )

    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.runs <= 1:
        print("Error: usa --runs mayor que 1 para calcular desviacion estandar.", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    exe = root / "pfsp_bat.exe"
    out_base = (root / args.out).resolve() if not args.out.is_absolute() else args.out

    try:
        if not args.no_build:
            compilar(root, exe)
        resultados = ejecutar(root, exe, out_base, args.runs, args.seed)
        csv_path = out_base / "resumen_escenarios.csv"
        md_path = out_base / "resumen_escenarios.md"
        escribir_csv(csv_path, resultados)
        escribir_markdown(md_path, resultados)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Resumen CSV: {csv_path}")
    print(f"Resumen Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())