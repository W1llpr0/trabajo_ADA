"""
Ejecuta todos los escenarios del proyecto y consolida los resultados.

Uso:
    python scripts/ejecutar_escenarios.py

Por defecto compila pfsp.exe, ejecuta 5 escenarios sobre las 3 instancias con
10 corridas independientes por instancia y guarda los CSV en resultados/.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Iterable


INSTANCIAS = [
    {
        "nombre": "instancia1_bas1",
        "ruta": Path("instancias") / "instancia1_bas1.txt",
        "optimo": 52,
        "tamano": "5x4",
    },
    {
        "nombre": "instancia2_car5",
        "ruta": Path("instancias") / "instancia2_car5.txt",
        "optimo": 7720,
        "tamano": "10x6",
    },
    {
        "nombre": "instancia3_reC01",
        "ruta": Path("instancias") / "instancia3_reC01.txt",
        "optimo": 1247,
        "tamano": "20x5",
    },
]


ESCENARIOS = [
    {
        "nombre": "E1_base",
        "objetivo": "Linea base",
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
        "objetivo": "Mayor poblacion con menos iteraciones",
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
        "objetivo": "Menor poblacion con mas iteraciones",
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
    "tamano",
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
        description="Ejecuta 5 escenarios del Bat Algorithm sobre las 3 instancias."
    )
    parser.add_argument("--runs", type=int, default=10, help="Corridas por instancia.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla base.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("resultados") / "escenarios",
        help="Carpeta base para los resultados por escenario.",
    )
    parser.add_argument(
        "--exe",
        type=Path,
        default=Path("pfsp.exe"),
        help="Ruta del ejecutable a usar o generar.",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Usa el ejecutable existente sin recompilar.",
    )
    return parser.parse_args()


def formato_decimal(valor: object, decimales: int = 2) -> str:
    return f"{float(valor):.{decimales}f}"


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
    print(f"Compilando {exe.name}...")
    subprocess.run(cmd, cwd=root, check=True)


def comando_ejecucion(
    exe: Path,
    instancia: Path,
    out_dir: Path,
    params: dict[str, float],
    runs: int,
    seed: int,
) -> list[str]:
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


def leer_resumen(ruta_csv: Path) -> dict[str, object]:
    with ruta_csv.open(newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))

    if not filas:
        raise RuntimeError(f"Resumen vacio: {ruta_csv}")

    makespans = [int(fila["makespan"]) for fila in filas]
    tiempos = [float(fila["tiempo_ms"]) for fila in filas]
    mejor_fila = min(filas, key=lambda fila: int(fila["makespan"]))
    return {
        "mejor": min(makespans),
        "peor": max(makespans),
        "promedio": statistics.mean(makespans),
        "desv_est": statistics.stdev(makespans) if len(makespans) > 1 else 0.0,
        "tiempo_prom_ms": statistics.mean(tiempos),
        "mejor_secuencia": mejor_fila["secuencia"],
    }


def ejecutar_escenarios(
    root: Path,
    exe: Path,
    out_base: Path,
    runs: int,
    seed: int,
) -> list[dict[str, object]]:
    resultados: list[dict[str, object]] = []
    out_base.mkdir(parents=True, exist_ok=True)

    for escenario in ESCENARIOS:
        escenario_dir = out_base / escenario["nombre"]
        escenario_dir.mkdir(parents=True, exist_ok=True)
        params = escenario["params"]

        for instancia in INSTANCIAS:
            print(f"Ejecutando {escenario['nombre']} / {instancia['nombre']}...")
            cmd = comando_ejecucion(
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

            resumen = leer_resumen(escenario_dir / f"resumen_{instancia['nombre']}.csv")
            optimo = int(instancia["optimo"])
            gap = ((int(resumen["mejor"]) - optimo) / optimo) * 100.0 if optimo else 0.0
            resultados.append(
                {
                    "escenario": escenario["nombre"],
                    "objetivo": escenario["objetivo"],
                    "instancia": instancia["nombre"],
                    "tamano": instancia["tamano"],
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
                    "gap_mejor_pct": gap,
                    **resumen,
                }
            )
    return resultados


def escribir_csv(ruta: Path, filas: Iterable[dict[str, object]]) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for fila in filas:
            salida = dict(fila)
            for clave in ("promedio", "desv_est", "tiempo_prom_ms", "gap_mejor_pct"):
                salida[clave] = formato_decimal(salida[clave])
            writer.writerow(salida)


def mejores_por_instancia(filas: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    mejores: dict[str, dict[str, object]] = {}
    for fila in filas:
        instancia = str(fila["instancia"])
        actual = mejores.get(instancia)
        if actual is None:
            mejores[instancia] = fila
            continue

        clave_fila = (
            float(fila["mejor"]),
            float(fila["promedio"]),
            float(fila["desv_est"]),
            float(fila["tiempo_prom_ms"]),
        )
        clave_actual = (
            float(actual["mejor"]),
            float(actual["promedio"]),
            float(actual["desv_est"]),
            float(actual["tiempo_prom_ms"]),
        )
        if clave_fila < clave_actual:
            mejores[instancia] = fila
    return mejores


def escribir_markdown(ruta: Path, filas: list[dict[str, object]]) -> None:
    mejores = mejores_por_instancia(filas)
    lineas = [
        "# Resumen de escenarios",
        "",
        "Criterio de seleccion: menor mejor makespan; en empate, menor promedio, desviacion y tiempo.",
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
            "| {escenario} | {instancia} | {poblacion} | {iteraciones} | {fmax:.2f} | "
            "{r0:.2f} | {alfa:.2f} | {gamma:.2f} | {mejor} | {peor} | "
            "{promedio:.2f} | {desv:.2f} | {tiempo:.2f} | {gap:.2f} |".format(
                escenario=fila["escenario"],
                instancia=fila["instancia"],
                poblacion=fila["poblacion"],
                iteraciones=fila["iteraciones"],
                fmax=float(fila["fmax"]),
                r0=float(fila["r0"]),
                alfa=float(fila["alfa"]),
                gamma=float(fila["gamma"]),
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
    if args.runs <= 0:
        print("Error: --runs debe ser mayor que 0.", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    exe = args.exe if args.exe.is_absolute() else root / args.exe
    out_base = args.out if args.out.is_absolute() else root / args.out

    try:
        if not args.no_build:
            compilar(root, exe)
        resultados = ejecutar_escenarios(root, exe, out_base, args.runs, args.seed)
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
