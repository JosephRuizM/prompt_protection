from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'motor_firewall',
        ['evaluador_firewall/FirewallEvaluator.cpp', 'evaluador_firewall/binding.cpp'],
        include_dirs=[
            pybind11.get_include(),
            'evaluador_firewall'
        ],
        language='c++',
        extra_compile_args=['-O3', '-std=c++17'],
    ),
]

setup(
    name='motor_firewall',
    version='0.1',
    author='JosephRuizM',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.10', 'numpy'],
)
