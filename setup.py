# Adapted from https://github.com/pybind/cmake_example/blob/master/setup.py
import os
import re
import sys
import platform
import subprocess
import importlib
from sysconfig import get_paths

import importlib
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from distutils.sysconfig import get_config_var
from distutils.version import LooseVersion


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class Build(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        super().run()

    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            info = get_paths()
            include_path = info["include"]
            cmake_args = [
                "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir,
            ]
            #   '-DPYTHON_INCLUDE_PATH=' + include_path]

            cfg = "Debug" if self.debug else "Release"
            build_args = ["--config", cfg]

            if platform.system() == "Windows":
                cmake_args += [
                    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(
                        cfg.upper(), extdir
                    ),
                    "-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{}={}".format(
                        cfg.upper(), extdir
                    ),
                ]
                if sys.maxsize > 2**32:
                    cmake_args += ["-A", "x64"]
                build_args += ["--", "/m"]
            else:
                cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
                build_args += ["--", "-j8"]

            env = os.environ.copy()
            env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
                env.get("CXXFLAGS", ""), self.distribution.get_version()
            )
            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)
            subprocess.check_call(
                ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env
            )
            subprocess.check_call(
                ["cmake", "--build", "."] + build_args, cwd=self.build_temp
            )
        else:
            super().build_extension(ext)


torch_spec = importlib.util.find_spec("torch")
tf_spec = importlib.util.find_spec("tensorflow")
packages = []
if torch_spec is not None:
    packages.append("pydiffvg")

if tf_spec is not None and sys.platform != "win32":
    packages.append("pydiffvg_tensorflow")

if len(packages) == 0:
    print(
        "Error: PyTorch or Tensorflow must be installed. For Windows platform only PyTorch is supported."
    )
    exit()

setup(
    name="diffvg",
    version="0.0.1",
    install_requires=[
        "torch",
        "svgpathtools",
        "scikit-image",
        "cssutils",
        "matplotlib",
    ],
    description="Differentiable Vector Graphics",
    ext_modules=[CMakeExtension("diffvg", "")],
    cmdclass=dict(build_ext=Build, install=install),
    packages=packages,
    zip_safe=False,
)
