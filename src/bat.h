#ifndef BAT_H
#define BAT_H

#include <random>
#include <vector>

#include "pfsp.h"

// ============================================================
// Algoritmo de Murcielago (Bat Algorithm, Yang 2010) adaptado
// al PFSP mediante la regla SPV (Smallest Position Value):
// cada murcielago tiene una posicion continua en R^n que se
// convierte en una permutacion de trabajos ordenando los
// indices por valor ascendente.
// ============================================================

// Parametros del algoritmo (valores por defecto razonables,
// configurables desde la linea de comandos).
struct ParametrosBA {
    int poblacion = 30;     // numero de murcielagos
    int iterMax = 500;      // criterio de parada: iteraciones maximas
    double fmin = 0.0;      // frecuencia minima
    double fmax = 2.0;      // frecuencia maxima
    double A0 = 1.0;        // loudness (sonoridad) inicial
    double r0 = 0.5;        // pulse rate (tasa de emision) inicial
    double alfa = 0.9;      // factor de reduccion de la sonoridad
    double gamma = 0.9;     // factor de crecimiento de la tasa de emision
    unsigned int semilla = 42;  // semilla del generador aleatorio
};

// Resultado de una ejecucion del algoritmo.
struct ResultadoBA {
    std::vector<int> mejorPerm;     // mejor permutacion encontrada (0-based)
    int mejorMakespan = 0;          // makespan de la mejor permutacion
    std::vector<int> convergencia;  // mejor makespan global por iteracion
};

class BatAlgorithm {
public:
    BatAlgorithm(const Instancia& inst, const ParametrosBA& params);

    // Ejecuta el algoritmo completo y devuelve la mejor solucion.
    ResultadoBA ejecutar();

private:
    const Instancia& inst_;
    ParametrosBA params_;
    std::mt19937 rng_;

    // Convierte una posicion continua en permutacion con la regla SPV.
    std::vector<int> spv(const std::vector<double>& x) const;

    // Genera un vecino de una permutacion aplicando swap o insert aleatorio.
    std::vector<int> vecino(const std::vector<int>& perm);

    // Construye una posicion continua coherente con una permutacion dada
    // (de modo que spv(posicion) == perm). Se usa cuando la busqueda local
    // produce directamente una permutacion.
    std::vector<double> posicionDesdePerm(const std::vector<int>& perm) const;
};

#endif // BAT_H
