from cx_Freeze import setup, Executable
import sys
import os
import shutil

if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = "Console"

setup(
        name = "PESTERCHUM",
        version = "3.14",
        description = "P3ST3RCHUM",
        executables = [Executable("pesterchum.py",
                                  base=base,
                                  compress=True,
                                  icon="pesterchum.ico",
                                  )])
if sys.platform == "win32":
    os.rename("build/exe.win32-2.6", "build/pesterchum")

shutil.copytree("themes", "build/pesterchum/themes")
shutil.copytree("imageformats", "build/pesterchum/imageformats")
shutil.copytree("smilies", "build/pesterchum/smilies")
shutil.copy("pesterchum.js", "build/pesterchum/")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcm90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcp90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcr90.dll", "build/pesterchum")
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375.manifest",
            "build/pesterchum")
shutil.copy("pesterchum.nsi", "build/pesterchum/")
shutil.copy("pesterchum-update.nsi", "build/pesterchum/")
os.mkdir("build/pesterchum/profiles")
os.mkdir("build/pesterchum/logs")
shutil.copy("logs/chums.js", "build/pesterchum/logs")
shutil.copy("readme.txt", "build/pesterchum/")
