// ============================================================
// PFSP resuelto con el Algoritmo de Murcielago (Bat Algorithm)
// Curso: Analisis y Disenio de Algoritmos - Proyecto Eval 3
//
// Uso:
//   pfsp.exe <instancia.txt> [opciones]
//
// Opciones:
//   --iter N    iteraciones maximas        (defecto: 500)
//   --pob N     tamanio de la poblacion    (defecto: 30)
//   --runs N    numero de ejecuciones      (defecto: 1)
//   --seed S    semilla base               (defecto: 42)
//   --fmin X    frecuencia minima          (defecto: 0.0)
//   --fmax X    frecuencia maxima          (defecto: 2.0)
//   --A0 X      sonoridad inicial          (defecto: 1.0)
//   --r0 X      tasa de emision inicial    (defecto: 0.5)
//   --alfa X    reduccion de sonoridad     (defecto: 0.9)
//   --gamma X   crecimiento de emision     (defecto: 0.9)
//   --out DIR   carpeta de salida          (defecto: resultados)
//   --eval "1 2 3 ..."  evalua una secuencia dada (1-based) y termina
// ============================================================

#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "bat.h"
#include "pfsp.h"

namespace fs = std::filesystem;

// Formatea una permutacion 0-based como "[J3, J1, ...]" (1-based para mostrar).
static std::string formatearSecuencia(const std::vector<int>& perm) {
    std::ostringstream os;
    os << "[";
    for (size_t i = 0; i < perm.size(); i++) {
        os << "J" << (perm[i] + 1);
        if (i + 1 < perm.size()) os << ", ";
    }
    os << "]";
    return os.str();
}

// Escribe la curva de convergencia: iteracion, mejor makespan global.
static void escribirConvergencia(const std::string& ruta, const std::vector<int>& conv) {
    std::ofstream out(ruta);
    out << "iteracion,mejor_makespan\n";
    for (size_t t = 0; t < conv.size(); t++) {
        out << (t + 1) << "," << conv[t] << "\n";
    }
}

// Escribe el cronograma de la mejor solucion (datos del diagrama de Gantt).
static void escribirGantt(const std::string& ruta, const Instancia& inst,
                          const std::vector<int>& perm) {
    std::ofstream out(ruta);
    out << "trabajo,maquina,inicio,fin\n";
    for (const Operacion& op : calcularGantt(inst, perm)) {
        out << (op.trabajo + 1) << "," << (op.maquina + 1) << ","
            << op.inicio << "," << op.fin << "\n";
    }
}

// Parsea una secuencia 1-based dada por el usuario ("3 1 4 2 5" o "3,1,4,2,5")
// y la valida como permutacion de 1..n.
static std::vector<int> parsearSecuencia(std::string texto, int n) {
    for (char& c : texto) {
        if (c == ',') c = ' ';
    }
    std::istringstream is(texto);
    std::vector<int> perm;
    int valor;
    while (is >> valor) perm.push_back(valor - 1);

    std::vector<bool> visto(n, false);
    if ((int)perm.size() != n) {
        throw std::runtime_error("La secuencia debe tener exactamente " +
                                 std::to_string(n) + " trabajos.");
    }
    for (int t : perm) {
        if (t < 0 || t >= n || visto[t]) {
            throw std::runtime_error("La secuencia no es una permutacion valida de 1.." +
                                     std::to_string(n));
        }
        visto[t] = true;
    }
    return perm;
}

static void imprimirUso() {
    std::cout << "Uso: pfsp.exe <instancia.txt> [--iter N] [--pob N] "
                 "[--runs N] [--seed S] [--fmin X] [--fmax X] [--A0 X] "
                 "[--r0 X] [--alfa X] [--gamma X] [--out DIR] "
                 "[--eval \"1 2 3 ...\"]\n";
}

static void validarParametros(const ParametrosBA& params, int runs) {
    if (params.poblacion <= 0) {
        throw std::runtime_error("La poblacion debe ser mayor que 0.");
    }
    if (params.iterMax <= 0) {
        throw std::runtime_error("Las iteraciones deben ser mayores que 0.");
    }
    if (runs <= 0) {
        throw std::runtime_error("El numero de ejecuciones debe ser mayor que 0.");
    }
    if (params.fmin < 0.0) {
        throw std::runtime_error("fmin debe ser mayor o igual que 0.");
    }
    if (params.fmax < params.fmin) {
        throw std::runtime_error("fmax debe ser mayor o igual que fmin.");
    }
    if (params.A0 <= 0.0 || params.A0 > 1.0) {
        throw std::runtime_error("A0 debe estar en el intervalo (0, 1].");
    }
    if (params.r0 < 0.0 || params.r0 > 1.0) {
        throw std::runtime_error("r0 debe estar en el intervalo [0, 1].");
    }
    if (params.alfa <= 0.0 || params.alfa > 1.0) {
        throw std::runtime_error("alfa debe estar en el intervalo (0, 1].");
    }
    if (params.gamma <= 0.0) {
        throw std::runtime_error("gamma debe ser mayor que 0.");
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        imprimirUso();
        return 1;
    }

    // ---- Lectura de argumentos ----
    std::string rutaInstancia = argv[1];
    ParametrosBA params;
    int runs = 1;
    std::string dirSalida = "resultados";
    std::string secuenciaEval;

    try {
        for (int i = 2; i < argc; i++) {
            std::string arg = argv[i];
            auto siguiente = [&]() -> std::string {
                if (i + 1 >= argc) throw std::runtime_error("Falta el valor de " + arg);
                return argv[++i];
            };
            if (arg == "--iter")      params.iterMax = std::stoi(siguiente());
            else if (arg == "--pob")  params.poblacion = std::stoi(siguiente());
            else if (arg == "--runs") runs = std::stoi(siguiente());
            else if (arg == "--seed") params.semilla = (unsigned int)std::stoul(siguiente());
            else if (arg == "--fmin") params.fmin = std::stod(siguiente());
            else if (arg == "--fmax") params.fmax = std::stod(siguiente());
            else if (arg == "--A0")   params.A0 = std::stod(siguiente());
            else if (arg == "--r0")   params.r0 = std::stod(siguiente());
            else if (arg == "--alfa") params.alfa = std::stod(siguiente());
            else if (arg == "--gamma") params.gamma = std::stod(siguiente());
            else if (arg == "--out")  dirSalida = siguiente();
            else if (arg == "--eval") secuenciaEval = siguiente();
            else throw std::runtime_error("Argumento desconocido: " + arg);
        }
        validarParametros(params, runs);

        Instancia inst = cargarInstancia(rutaInstancia);
        std::cout << "Instancia: " << inst.nombre << " (" << inst.n
                  << " trabajos x " << inst.m << " maquinas)\n";

        // ---- Modo evaluacion: calcular el makespan de una secuencia dada ----
        if (!secuenciaEval.empty()) {
            std::vector<int> perm = parsearSecuencia(secuenciaEval, inst.n);
            std::cout << "Secuencia: " << formatearSecuencia(perm) << "\n";
            std::cout << "Makespan:  " << makespan(inst, perm) << "\n";
            return 0;
        }

        fs::create_directories(dirSalida);
        std::cout << "Parametros: poblacion=" << params.poblacion
                  << ", iteraciones=" << params.iterMax
                  << ", fmin=" << params.fmin << ", fmax=" << params.fmax
                  << ", A0=" << params.A0 << ", r0=" << params.r0
                  << ", alfa=" << params.alfa << ", gamma=" << params.gamma
                  << ", semilla base=" << params.semilla
                  << ", ejecuciones=" << runs << "\n\n";

        // ---- Ejecuciones del algoritmo ----
        std::vector<ResultadoBA> resultados;
        std::vector<double> tiemposMs;
        for (int e = 0; e < runs; e++) {
            ParametrosBA p = params;
            p.semilla = params.semilla + (unsigned int)e;  // semillas reproducibles

            auto ini = std::chrono::steady_clock::now();
            BatAlgorithm ba(inst, p);
            ResultadoBA res = ba.ejecutar();
            auto fin = std::chrono::steady_clock::now();
            double ms = std::chrono::duration<double, std::milli>(fin - ini).count();

            resultados.push_back(res);
            tiemposMs.push_back(ms);

            std::cout << "Ejecucion " << std::setw(2) << (e + 1)
                      << " | semilla=" << std::setw(4) << p.semilla
                      << " | makespan=" << std::setw(6) << res.mejorMakespan
                      << " | tiempo=" << std::fixed << std::setprecision(2)
                      << std::setw(8) << ms << " ms"
                      << " | " << formatearSecuencia(res.mejorPerm) << "\n";
        }

        // ---- Mejor ejecucion y estadisticas ----
        int mejorRun = 0, peorRun = 0;
        for (int e = 1; e < runs; e++) {
            if (resultados[e].mejorMakespan < resultados[mejorRun].mejorMakespan) mejorRun = e;
            if (resultados[e].mejorMakespan > resultados[peorRun].mejorMakespan) peorRun = e;
        }
        const ResultadoBA& mejor = resultados[mejorRun];

        double suma = 0, sumaT = 0;
        for (int e = 0; e < runs; e++) {
            suma += resultados[e].mejorMakespan;
            sumaT += tiemposMs[e];
        }
        double promedio = suma / runs;
        double promedioT = sumaT / runs;
        double varianza = 0;
        for (int e = 0; e < runs; e++) {
            double d = resultados[e].mejorMakespan - promedio;
            varianza += d * d;
        }
        // Desviacion estandar muestral (n-1) cuando hay mas de una ejecucion.
        double desviacion = (runs > 1) ? std::sqrt(varianza / (runs - 1)) : 0.0;

        std::cout << "\n========== RESUMEN ==========\n";
        std::cout << "Mejor makespan:      " << mejor.mejorMakespan << "\n";
        std::cout << "Peor makespan:       " << resultados[peorRun].mejorMakespan << "\n";
        std::cout << "Makespan promedio:   " << std::fixed << std::setprecision(2) << promedio << "\n";
        std::cout << "Desviacion estandar: " << desviacion << "\n";
        std::cout << "Tiempo promedio:     " << promedioT << " ms\n";
        std::cout << "Mejor secuencia:     " << formatearSecuencia(mejor.mejorPerm) << "\n";

        // ---- Archivos de salida ----
        std::string base = dirSalida + "/";
        escribirConvergencia(base + "convergencia_" + inst.nombre + ".csv", mejor.convergencia);
        escribirGantt(base + "gantt_" + inst.nombre + ".csv", inst, mejor.mejorPerm);

        if (runs > 1) {
            std::ofstream out(base + "resumen_" + inst.nombre + ".csv");
            out << "ejecucion,semilla,makespan,tiempo_ms,secuencia\n";
            for (int e = 0; e < runs; e++) {
                out << (e + 1) << "," << (params.semilla + e) << ","
                    << resultados[e].mejorMakespan << ","
                    << std::fixed << std::setprecision(2) << tiemposMs[e] << ","
                    << "\"" << formatearSecuencia(resultados[e].mejorPerm) << "\"\n";
            }
        }
        std::cout << "\nArchivos CSV generados en: " << dirSalida << "/\n";
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
}
