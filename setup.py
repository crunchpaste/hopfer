from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import sys
from pathlib import Path


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
)
