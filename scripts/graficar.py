"""
Genera figuras desde los CSV producidos por pfsp.exe.

Uso:
    python scripts/graficar.py resultados
    python scripts/graficar.py resultados/escenarios --recursive

Salidas:
    - PNG junto a cada CSV de convergencia y Gantt.
    - Figuras comparativas en una subcarpeta figuras/ cuando existen datos
      suficientes en la carpeta procesada.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib import colormaps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera figuras de convergencia y Gantt.")
    parser.add_argument(
        "carpeta",
        nargs="?",
        default="resultados",
        type=Path,
        help="Carpeta que contiene CSV de resultados.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Procesa tambien subcarpetas con CSV.",
    )
    parser.add_argument(
        "--formatos",
        nargs="+",
        default=["png"],
        choices=["png", "pdf"],
        help="Formatos de salida.",
    )
    return parser.parse_args()


def leer_convergencia(ruta_csv: Path) -> tuple[list[int], list[int]]:
    iteraciones, makespans = [], []
    with ruta_csv.open(newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            iteraciones.append(int(fila["iteracion"]))
            makespans.append(int(fila["mejor_makespan"]))
    return iteraciones, makespans


def leer_gantt(ruta_csv: Path) -> list[tuple[int, int, int, int]]:
    operaciones = []
    with ruta_csv.open(newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            operaciones.append(
                (
                    int(fila["trabajo"]),
                    int(fila["maquina"]),
                    int(fila["inicio"]),
                    int(fila["fin"]),
                )
            )
    return operaciones


def leer_resumen_escenarios(ruta_csv: Path) -> list[dict[str, str]]:
    with ruta_csv.open(newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def guardar_figura(fig: plt.Figure, salida_base: Path, formatos: list[str], dpi: int = 160) -> None:
    salida_base.parent.mkdir(parents=True, exist_ok=True)
    for formato in formatos:
        salida = salida_base.with_suffix(f".{formato}")
        fig.savefig(salida, dpi=dpi, facecolor="white", bbox_inches="tight")
        print(f"  generado: {salida}")
    plt.close(fig)


def nombre_instancia(ruta_csv: Path, prefijo: str) -> str:
    return ruta_csv.stem.replace(prefijo, "")


def graficar_convergencia(ruta_csv: Path, formatos: list[str]) -> None:
    iteraciones, makespans = leer_convergencia(ruta_csv)
    if not iteraciones:
        return

    instancia = nombre_instancia(ruta_csv, "convergencia_")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(iteraciones, makespans, color="#1f77b4", linewidth=1.8)
    ax.set_title(f"Convergencia - {instancia}")
    ax.set_xlabel("Iteracion")
    ax.set_ylabel("Mejor makespan")
    ax.grid(True, alpha=0.35)
    guardar_figura(fig, ruta_csv.with_suffix(""), formatos)


def suavizar_color(color: object, factor: float = 0.18) -> tuple[float, float, float]:
    r, g, b = mcolors.to_rgb(color)
    return (
        r + (1.0 - r) * factor,
        g + (1.0 - g) * factor,
        b + (1.0 - b) * factor,
    )


def color_texto_contraste(color: object) -> str:
    r, g, b = mcolors.to_rgb(color)
    luminancia = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#1a1a1a" if luminancia > 0.58 else "white"


def graficar_gantt(ruta_csv: Path, formatos: list[str]) -> None:
    operaciones = leer_gantt(ruta_csv)
    if not operaciones:
        return

    instancia = nombre_instancia(ruta_csv, "gantt_")
    trabajos = sorted({op[0] for op in operaciones})
    maquinas = sorted({op[1] for op in operaciones})
    makespan = max(op[3] for op in operaciones)
    cmap = colormaps["tab20"]
    colores = {
        trabajo: suavizar_color(cmap(i % cmap.N))
        for i, trabajo in enumerate(trabajos)
    }

    fig, ax = plt.subplots(figsize=(11, 1.4 + 0.62 * len(maquinas)))
    umbral_etiqueta = max(makespan * 0.025, 1.0)

    for trabajo, maquina, inicio, fin in operaciones:
        duracion = fin - inicio
        color = colores[trabajo]
        ax.barh(
            y=maquina,
            width=duracion,
            left=inicio,
            height=0.58,
            color=color,
            edgecolor="white",
            linewidth=0.45,
        )
        if duracion >= umbral_etiqueta:
            ax.text(
                inicio + duracion / 2,
                maquina,
                f"J{trabajo}",
                ha="center",
                va="center",
                fontsize=7,
                color=color_texto_contraste(color),
                clip_on=True,
            )

    ax.axvline(makespan, color="#b22222", linestyle="--", linewidth=1.1)
    ax.text(makespan, min(maquinas) - 0.45, f"Cmax = {makespan}", color="#b22222", ha="right")
    ax.set_title(f"Diagrama de Gantt - {instancia}")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Maquina")
    ax.set_yticks(maquinas)
    ax.set_yticklabels([f"M{m}" for m in maquinas])
    ax.invert_yaxis()
    ax.grid(True, axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    guardar_figura(fig, ruta_csv.with_suffix(""), formatos)


def graficar_convergencia_compuesta(carpeta: Path, convergencias: list[Path], formatos: list[str]) -> None:
    if len(convergencias) < 2:
        return

    datos = []
    for ruta_csv in sorted(convergencias):
        iteraciones, makespans = leer_convergencia(ruta_csv)
        if iteraciones:
            datos.append((nombre_instancia(ruta_csv, "convergencia_"), iteraciones, makespans))

    if len(datos) < 2:
        return

    columnas = min(3, len(datos))
    filas = (len(datos) + columnas - 1) // columnas
    fig, axes = plt.subplots(filas, columnas, figsize=(4.2 * columnas, 3.2 * filas), squeeze=False)
    axes_planos = [ax for fila in axes for ax in fila]

    for ax, (instancia, iteraciones, makespans) in zip(axes_planos, datos):
        ax.plot(iteraciones, makespans, color="#1f4e79", linewidth=1.35)
        ax.set_title(instancia)
        ax.set_xlabel("Iteracion")
        ax.set_ylabel("Makespan")
        ax.grid(True, alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    for ax in axes_planos[len(datos) :]:
        ax.axis("off")

    guardar_figura(fig, carpeta / "figuras" / "convergencia_compuesta", formatos, dpi=220)


def graficar_comparacion_escenarios(carpeta: Path, formatos: list[str]) -> None:
    resumen = carpeta / "resumen_escenarios.csv"
    if not resumen.is_file():
        return

    filas = leer_resumen_escenarios(resumen)
    if not filas:
        return

    por_instancia: dict[str, list[dict[str, str]]] = defaultdict(list)
    for fila in filas:
        por_instancia[fila["instancia"]].append(fila)

    fig, axes = plt.subplots(
        len(por_instancia),
        1,
        figsize=(9.5, 2.9 * len(por_instancia)),
        squeeze=False,
    )
    for ax, instancia in zip([fila[0] for fila in axes], sorted(por_instancia)):
        datos = sorted(por_instancia[instancia], key=lambda fila: fila["escenario"])
        escenarios = [fila["escenario"].replace("_", "\n") for fila in datos]
        promedios = [float(fila["promedio"]) for fila in datos]
        mejores = [float(fila["mejor"]) for fila in datos]
        ax.bar(escenarios, promedios, color="#9ecae1", edgecolor="#2b5d7c", linewidth=0.7)
        ax.plot(escenarios, mejores, color="#b22222", marker="o", linewidth=1.2, label="Mejor")
        ax.set_title(instancia)
        ax.set_ylabel("Makespan")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(loc="best", frameon=False)

    guardar_figura(fig, carpeta / "figuras" / "comparacion_escenarios", formatos, dpi=220)


def carpetas_a_procesar(carpeta: Path, recursive: bool) -> list[Path]:
    if not recursive:
        return [carpeta]

    carpetas = {
        ruta.parent
        for patron in ("convergencia_*.csv", "gantt_*.csv", "resumen_escenarios.csv")
        for ruta in carpeta.rglob(patron)
    }
    return sorted(carpetas)


def procesar_carpeta(carpeta: Path, formatos: list[str]) -> bool:
    convergencias = sorted(carpeta.glob("convergencia_*.csv"))
    gantts = sorted(carpeta.glob("gantt_*.csv"))
    resumen = carpeta / "resumen_escenarios.csv"

    if not convergencias and not gantts and not resumen.is_file():
        return False

    print(f"Procesando: {carpeta}")
    for ruta_csv in convergencias:
        graficar_convergencia(ruta_csv, formatos)
    for ruta_csv in gantts:
        graficar_gantt(ruta_csv, formatos)
    graficar_convergencia_compuesta(carpeta, convergencias, formatos)
    graficar_comparacion_escenarios(carpeta, formatos)
    return True


def main() -> int:
    args = parse_args()
    carpeta = args.carpeta
    if not carpeta.is_dir():
        print(f"Error: no existe la carpeta '{carpeta}'")
        return 1

    procesadas = 0
    for subcarpeta in carpetas_a_procesar(carpeta, args.recursive):
        if procesar_carpeta(subcarpeta, args.formatos):
            procesadas += 1

    if procesadas == 0:
        print(f"No se encontraron CSV de resultados en '{carpeta}'.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
