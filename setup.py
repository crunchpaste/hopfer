from setuptools import setup, Extension
from setuptools.command.build_py import build_py
import numpy as np
import subprocess
import sys
from pathlib import Path

from Cython.Build import cythonize


def compile_algorithms():
    compiler = Path(__file__).parent / "src/hopfer/core/compiler/algorithm_compiler.py"
    if compiler.exists():
        print(f"\n--- RUNNING AOT COMPILATION: {compiler} ---")
        subprocess.check_call([sys.executable, str(compiler)])
    else:
        print(f"\n--- WARNING: Compiler not found at {compiler} ---")


class BuildPyCommand(build_py):
    def run(self):
        compile_algorithms()
        super().run()


# Setup OpenMP flags
openmp_arg = "/openmp" if sys.platform.startswith("win") else "-fopenmp"

# Define the Cython extensions
# Note the name is the full package path 'hopfer.helpers.image_utils'
ext_modules = [
    Extension(
        "hopfer.helpers.image_utils",
        ["src/hopfer/helpers/image_utils.pyx"],
        extra_compile_args=[openmp_arg, "-O3", "-march=native", "-ffast-math"],
        extra_link_args=[openmp_arg],
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

try:
    from setuptools.command.editable_wheel import editable_wheel

    class EditableWheelCommand(editable_wheel):
        def run(self):
            compile_algorithms()
            super().run()

    CMD_CLASS = {"build_py": BuildPyCommand, "editable_wheel": EditableWheelCommand}
except ImportError:
    CMD_CLASS = {"build_py": BuildPyCommand}

setup(
    cmdclass=CMD_CLASS,
    ext_modules=cythonize(ext_modules, annotate=True),
)
