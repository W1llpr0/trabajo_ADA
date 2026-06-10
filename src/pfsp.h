#ifndef PFSP_H
#define PFSP_H

#include <string>
#include <vector>

// ============================================================
// Modulo PFSP: representacion de la instancia, calculo del
// makespan y construccion del cronograma (diagrama de Gantt).
// ============================================================

// Instancia del Permutation Flow Shop Scheduling Problem.
// p[i][j] = tiempo de procesamiento del trabajo i en la maquina j.
struct Instancia {
    int n = 0;                          // numero de trabajos
    int m = 0;                          // numero de maquinas
    std::vector<std::vector<int>> p;    // matriz de tiempos (n x m)
    std::string nombre;                 // nombre base del archivo (sin extension)
};

// Una operacion programada: usada para construir el diagrama de Gantt.
struct Operacion {
    int trabajo;    // indice del trabajo (0-based)
    int maquina;    // indice de la maquina (0-based)
    int inicio;     // tiempo de inicio
    int fin;        // tiempo de finalizacion
};

// Carga una instancia desde un archivo .txt con el formato:
//   linea 1: n m
//   luego n lineas con m pares (indice_maquina, tiempo)
// Lanza std::runtime_error si el archivo no existe o esta mal formado.
Instancia cargarInstancia(const std::string& ruta);

// Calcula el makespan de una permutacion de trabajos usando la
// recurrencia C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j].
int makespan(const Instancia& inst, const std::vector<int>& perm);

// Construye el cronograma completo (inicio y fin de cada operacion)
// para la permutacion dada. Sirve para generar el diagrama de Gantt.
std::vector<Operacion> calcularGantt(const Instancia& inst, const std::vector<int>& perm);

#endif // PFSP_H
