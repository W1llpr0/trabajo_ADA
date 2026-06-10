"""
Genera las graficas del proyecto a partir de los CSV producidos por pfsp_bat.exe:
  - Curva de convergencia (convergencia_<instancia>.csv)
  - Diagrama de Gantt     (gantt_<instancia>.csv)

Uso:
    python scripts/graficar.py [carpeta_resultados]

Si no se indica carpeta, usa "resultados/". Los PNG se guardan en la misma carpeta.
Requiere: matplotlib
"""

import csv
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")  # no requiere ventana grafica
import matplotlib.pyplot as plt
from matplotlib import colormaps


def graficar_convergencia(ruta_csv: str) -> None:
    """Curva de convergencia: mejor makespan global por iteracion."""
    iteraciones, makespans = [], []
    with open(ruta_csv, newline="") as f:
        for fila in csv.DictReader(f):
            iteraciones.append(int(fila["iteracion"]))
            makespans.append(int(fila["mejor_makespan"]))

    instancia = os.path.basename(ruta_csv).replace("convergencia_", "").replace(".csv", "")
    plt.figure(figsize=(8, 5))
    plt.plot(iteraciones, makespans, color="tab:blue", linewidth=1.8)
    plt.xlabel("Numero de iteraciones")
    plt.ylabel("Mejor makespan encontrado")
    plt.title(f"Curva de convergencia - Bat Algorithm - {instancia}")
    plt.grid(True, alpha=0.4)
    salida = ruta_csv.replace(".csv", ".png")
    plt.tight_layout()
    plt.savefig(salida, dpi=150)
    plt.close()
    print(f"  generado: {salida}")


def graficar_gantt(ruta_csv: str) -> None:
    """Diagrama de Gantt: una fila por maquina, una barra por operacion."""
    operaciones = []
    with open(ruta_csv, newline="") as f:
        for fila in csv.DictReader(f):
            operaciones.append((int(fila["trabajo"]), int(fila["maquina"]),
                                int(fila["inicio"]), int(fila["fin"])))

    instancia = os.path.basename(ruta_csv).replace("gantt_", "").replace(".csv", "")
    n_trabajos = max(op[0] for op in operaciones)
    n_maquinas = max(op[1] for op in operaciones)
    makespan = max(op[3] for op in operaciones)

    cmap = colormaps["tab20"]
    colores = {j: cmap((j - 1) % 20) for j in range(1, n_trabajos + 1)}

    fig, ax = plt.subplots(figsize=(11, 1.2 + 0.8 * n_maquinas))
    for trabajo, maquina, inicio, fin in operaciones:
        ax.barh(y=maquina, width=fin - inicio, left=inicio, height=0.6,
                color=colores[trabajo], edgecolor="black", linewidth=0.5)
        # Etiqueta del trabajo dentro de la barra (si cabe).
        if fin - inicio > makespan * 0.025:
            ax.text((inicio + fin) / 2, maquina, f"J{trabajo}",
                    ha="center", va="center", fontsize=7)

    ax.axvline(makespan, color="red", linestyle="--", linewidth=1.2)
    ax.text(makespan, 0.45, f" makespan = {makespan}", color="red", fontsize=9, va="bottom")
    ax.set_yticks(range(1, n_maquinas + 1))
    ax.set_yticklabels([f"M{j}" for j in range(1, n_maquinas + 1)])
    ax.invert_yaxis()  # M1 arriba
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Maquina")
    ax.set_title(f"Diagrama de Gantt - mejor solucion - {instancia}")
    ax.grid(True, axis="x", alpha=0.4)
    salida = ruta_csv.replace(".csv", ".png")
    plt.tight_layout()
    plt.savefig(salida, dpi=150)
    plt.close()
    print(f"  generado: {salida}")


def main() -> None:
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "resultados"
    if not os.path.isdir(carpeta):
        print(f"Error: no existe la carpeta '{carpeta}'")
        sys.exit(1)

    convergencias = sorted(glob.glob(os.path.join(carpeta, "convergencia_*.csv")))
    gantts = sorted(glob.glob(os.path.join(carpeta, "gantt_*.csv")))
    if not convergencias and not gantts:
        print(f"No se encontraron CSV en '{carpeta}'. Ejecuta primero pfsp_bat.exe")
        sys.exit(1)

    print("Curvas de convergencia:")
    for ruta in convergencias:
        graficar_convergencia(ruta)
    print("Diagramas de Gantt:")
    for ruta in gantts:
        graficar_gantt(ruta)


if __name__ == "__main__":
    main()
