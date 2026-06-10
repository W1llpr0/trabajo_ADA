#include "pfsp.h"

#include <algorithm>
#include <fstream>
#include <sstream>
#include <stdexcept>

// Extrae el nombre base de un archivo (sin carpetas ni extension).
static std::string nombreBase(const std::string& ruta) {
    size_t barra = ruta.find_last_of("/\\");
    std::string archivo = (barra == std::string::npos) ? ruta : ruta.substr(barra + 1);
    size_t punto = archivo.find_last_of('.');
    return (punto == std::string::npos) ? archivo : archivo.substr(0, punto);
}

Instancia cargarInstancia(const std::string& ruta) {
    std::ifstream entrada(ruta);
    if (!entrada) {
        throw std::runtime_error("No se pudo abrir el archivo: " + ruta);
    }

    Instancia inst;
    inst.nombre = nombreBase(ruta);

    // Primera linea: numero de trabajos y numero de maquinas.
    if (!(entrada >> inst.n >> inst.m) || inst.n <= 0 || inst.m <= 0) {
        throw std::runtime_error("Formato invalido en la primera linea de: " + ruta);
    }

    // Cada trabajo: m pares (indice_maquina, tiempo). El indice de maquina
    // viene en orden 0..m-1, pero se usa explicitamente por seguridad.
    inst.p.assign(inst.n, std::vector<int>(inst.m, 0));
    for (int i = 0; i < inst.n; i++) {
        for (int k = 0; k < inst.m; k++) {
            int maquina, tiempo;
            if (!(entrada >> maquina >> tiempo)) {
                throw std::runtime_error("Datos incompletos para el trabajo " +
                                         std::to_string(i + 1) + " en: " + ruta);
            }
            if (maquina < 0 || maquina >= inst.m) {
                throw std::runtime_error("Indice de maquina fuera de rango en: " + ruta);
            }
            inst.p[i][maquina] = tiempo;
        }
    }
    return inst;
}

int makespan(const Instancia& inst, const std::vector<int>& perm) {
    // C[j] guarda el tiempo de finalizacion en la maquina j del ultimo
    // trabajo procesado (fila anterior de la tabla). Se actualiza fila a fila,
    // aplicando C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j].
    std::vector<int> C(inst.m, 0);
    for (int i = 0; i < (int)perm.size(); i++) {
        int trabajo = perm[i];
        C[0] += inst.p[trabajo][0];
        for (int j = 1; j < inst.m; j++) {
            C[j] = std::max(C[j], C[j - 1]) + inst.p[trabajo][j];
        }
    }
    return C[inst.m - 1];
}

std::vector<Operacion> calcularGantt(const Instancia& inst, const std::vector<int>& perm) {
    // Igual que makespan(), pero registrando inicio y fin de cada operacion.
    std::vector<Operacion> cronograma;
    cronograma.reserve(perm.size() * inst.m);

    std::vector<int> C(inst.m, 0);  // fin del trabajo anterior en cada maquina
    for (int i = 0; i < (int)perm.size(); i++) {
        int trabajo = perm[i];
        int finPrevio = 0;  // fin del trabajo actual en la maquina anterior
        for (int j = 0; j < inst.m; j++) {
            int inicio = std::max(C[j], finPrevio);
            int fin = inicio + inst.p[trabajo][j];
            cronograma.push_back({trabajo, j, inicio, fin});
            C[j] = fin;
            finPrevio = fin;
        }
    }
    return cronograma;
}
