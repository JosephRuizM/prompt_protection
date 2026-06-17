#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "FirewallEvaluator.h"

namespace py = pybind11;

bool verificar_seguridad_numpy(py::array_t<float> prompt_actual, py::array_t<float> matriz_bd) {
    FirewallEvaluator evaluador;

    py::buffer_info info_actual = prompt_actual.request();
    float* ptr_actual = static_cast<float*>(info_actual.ptr);
    int dimensiones = info_actual.shape[0]; 

    py::buffer_info info_bd = matriz_bd.request();
    float* ptr_bloque_bd = static_cast<float*>(info_bd.ptr);
    int cantidad_vectores = info_bd.shape[0]; // Cuántos ataques sospechosos trajimos


    const float** vectores_bd = new const float* [cantidad_vectores];
    for (int i = 0; i < cantidad_vectores; ++i) {
        vectores_bd[i] = ptr_bloque_bd + (i * dimensiones);
    }

    bool resultado = evaluador.evaluarSeguridad(ptr_actual, vectores_bd, dimensiones, cantidad_vectores);

    delete[] vectores_bd;

    return resultado;
}

PYBIND11_MODULE(motor_firewall, m) {
    m.doc() = "Modulo de alto rendimiento en C++ para detectar Prompt Injection";
    m.def("evaluar_prompt", &verificar_seguridad_numpy, "Recibe arrays de NumPy y calcula el coseno en C++");
}
