#include "bat.h"

#include <algorithm>
#include <cmath>
#include <numeric>

BatAlgorithm::BatAlgorithm(const Instancia& inst, const ParametrosBA& params)
    : inst_(inst), params_(params), rng_(params.semilla) {}

std::vector<int> BatAlgorithm::spv(const std::vector<double>& x) const {
    // Regla SPV: el trabajo con menor valor de posicion va primero.
    std::vector<int> perm(x.size());
    std::iota(perm.begin(), perm.end(), 0);
    std::sort(perm.begin(), perm.end(),
              [&x](int a, int b) { return x[a] < x[b]; });
    return perm;
}

std::vector<int> BatAlgorithm::vecino(const std::vector<int>& perm) {
    // Busqueda local sobre permutaciones: con probabilidad 0.5 se
    // intercambian dos trabajos (swap) y en caso contrario se extrae un
    // trabajo y se reinserta en otra posicion (insert). Esta perturbacion
    // reemplaza al "vuelo aleatorio" continuo del algoritmo original.
    std::vector<int> nuevo = perm;
    int n = (int)perm.size();
    std::uniform_int_distribution<int> uPos(0, n - 1);
    std::uniform_real_distribution<double> u01(0.0, 1.0);

    int a = uPos(rng_);
    int b = uPos(rng_);
    while (b == a) b = uPos(rng_);

    if (u01(rng_) < 0.5) {
        std::swap(nuevo[a], nuevo[b]);          // operador swap
    } else {
        int trabajo = nuevo[a];                  // operador insert
        nuevo.erase(nuevo.begin() + a);
        nuevo.insert(nuevo.begin() + b, trabajo);
    }
    return nuevo;
}

std::vector<double> BatAlgorithm::posicionDesdePerm(const std::vector<int>& perm) const {
    // Asigna a cada trabajo su posicion en la secuencia, de modo que al
    // aplicar SPV se recupere exactamente la misma permutacion.
    std::vector<double> x(perm.size());
    for (int i = 0; i < (int)perm.size(); i++) {
        x[perm[i]] = (double)i;
    }
    return x;
}

ResultadoBA BatAlgorithm::ejecutar() {
    const int n = inst_.n;
    const int N = params_.poblacion;
    std::uniform_real_distribution<double> u01(0.0, 1.0);
    std::uniform_real_distribution<double> uIni(0.0, (double)n);

    // ---- Inicializacion de la poblacion de murcielagos ----
    std::vector<std::vector<double>> x(N, std::vector<double>(n));   // posiciones
    std::vector<std::vector<double>> v(N, std::vector<double>(n, 0.0)); // velocidades
    std::vector<double> A(N, params_.A0);   // sonoridad de cada murcielago
    std::vector<double> r(N, params_.r0);   // tasa de emision de cada murcielago
    std::vector<std::vector<int>> perm(N);  // permutacion asociada (via SPV)
    std::vector<int> fit(N);                // makespan de cada murcielago

    for (int k = 0; k < N; k++) {
        for (int d = 0; d < n; d++) x[k][d] = uIni(rng_);
        perm[k] = spv(x[k]);
        fit[k] = makespan(inst_, perm[k]);
    }

    // Mejor solucion global inicial.
    ResultadoBA res;
    int mejorIdx = (int)(std::min_element(fit.begin(), fit.end()) - fit.begin());
    res.mejorPerm = perm[mejorIdx];
    res.mejorMakespan = fit[mejorIdx];
    std::vector<double> mejorX = x[mejorIdx];
    res.convergencia.reserve(params_.iterMax);

    // ---- Bucle principal del Bat Algorithm ----
    for (int t = 1; t <= params_.iterMax; t++) {
        for (int k = 0; k < N; k++) {
            // 1) Actualizar frecuencia, velocidad y posicion (Yang 2010):
            //    f = fmin + (fmax - fmin) * beta,  beta ~ U(0,1)
            //    v = v + (x - x_best) * f
            //    x = x + v
            double f = params_.fmin + (params_.fmax - params_.fmin) * u01(rng_);
            std::vector<double> xNuevo(n);
            for (int d = 0; d < n; d++) {
                v[k][d] += (x[k][d] - mejorX[d]) * f;
                xNuevo[d] = x[k][d] + v[k][d];
            }

            // 2) Busqueda local: si rand > r[k], generar una solucion
            //    cercana a la mejor global (swap/insert sobre la permutacion).
            std::vector<int> permCand;
            if (u01(rng_) > r[k]) {
                permCand = vecino(res.mejorPerm);
                xNuevo = posicionDesdePerm(permCand);  // mantener coherencia x <-> perm
            } else {
                permCand = spv(xNuevo);
            }

            // 3) Evaluar la solucion candidata.
            int fitCand = makespan(inst_, permCand);

            // 4) Aceptacion: si mejora al murcielago y rand < A[k], se acepta
            //    la nueva solucion; ademas se reduce la sonoridad y se
            //    incrementa la tasa de emision (el murcielago "se acerca a la presa").
            if (fitCand <= fit[k] && u01(rng_) < A[k]) {
                x[k] = xNuevo;
                perm[k] = permCand;
                fit[k] = fitCand;
                A[k] *= params_.alfa;
                r[k] = params_.r0 * (1.0 - std::exp(-params_.gamma * t));
            }

            // 5) Actualizar la mejor solucion global si corresponde.
            if (fitCand < res.mejorMakespan) {
                res.mejorMakespan = fitCand;
                res.mejorPerm = permCand;
                mejorX = xNuevo;
                // Elitismo: el murcielago adopta la nueva mejor solucion.
                x[k] = xNuevo;
                perm[k] = permCand;
                fit[k] = fitCand;
            }
        }
        // Registrar la evolucion para la curva de convergencia.
        res.convergencia.push_back(res.mejorMakespan);
    }
    return res;
}
