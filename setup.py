from cx_Freeze import setup, Executable
import sys
import os
import shutil

if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = "Console"

setup(
        name = "P3ST3RCHUM",
        version = "3.14",
        description = "P3ST3RCHUM",
        executables = [Executable("pesterchum.py",
                                  base=base,
                                  icon="pesterchum.ico",
                                  compress=True,
                                  )])
if sys.platform == "win32":
    os.rename("build/exe.win32-2.6", "build/pesterchum")

shutil.copytree("themes", "build/pesterchum/themes")
shutil.copytree("imageformats", "build/pesterchum/imageformats")
shutil.copy("pesterchum.js", "build/pesterchum/")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcm90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcp90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcr90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375.manifest",
            "build/pesterchum")
os.mkdir("build/pesterchum/profiles")
os.mkdir("build/pesterchum/logs")
