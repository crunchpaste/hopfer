import subprocess
import sys
from pathlib import Path

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup
from setuptools.command.build_py import build_py


def compile_algorithms():
    compiler = (
        Path(__file__).parent / "src/hopfer/core/compiler/algorithm_compiler.py"
    )
    if compiler.exists():
        print(f"\n--- RUNNING AOT COMPILATION: {compiler} ---")
        subprocess.check_call([sys.executable, str(compiler)])
    else:
        print(f"\n--- WARNING: Compiler not found at {compiler} ---")


class BuildPyCommand(build_py):
    def run(self):
        compile_algorithms()
        super().run()


openmp_arg = "/openmp" if sys.platform.startswith("win") else "-fopenmp"
opt_args = (
    ["-O3", "-march=native", "-ffast-math"]
    if not sys.platform.startswith("win")
    else ["/O2", "/arch:AVX2"]
)

ext_modules = [
    Extension(
        "hopfer.helpers.image_utils",
        ["src/hopfer/helpers/image_utils.pyx"],
        extra_compile_args=[openmp_arg, *opt_args],
        extra_link_args=[openmp_arg],
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    ),
    Extension(
        "hopfer.core.algorithms.cython_ops.backend",
        ["src/hopfer/core/algorithms/cython_ops/cython_ops.pyx"],
        extra_compile_args=[openmp_arg, *opt_args],
        extra_link_args=[openmp_arg],
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    ),
]

try:
    from setuptools.command.editable_wheel import editable_wheel

    class EditableWheelCommand(editable_wheel):
        def run(self):
            compile_algorithms()
            super().run()

    CMD_CLASS = {
        "build_py": BuildPyCommand,
        "editable_wheel": EditableWheelCommand,
    }
except ImportError:
    CMD_CLASS = {"build_py": BuildPyCommand}

setup(
    cmdclass=CMD_CLASS,
    ext_modules=cythonize(ext_modules, annotate=True),
    compiler_directives={
        "boundscheck": False,
        "wraparound": False,
        "initializedcheck": False,
        "cdivision": True,
        "language_level": "3",
        "nonecheck": False,
    },
)
