# WINDOWS setup file!

from cx_Freeze import setup, Executable
import sys
import os
import os.path
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
os.rename("build/exe.win32-2.6", "build/pesterchum")
pcloc = "build/pesterchum"

shutil.copytree("themes", "%s/themes" % (pcloc))
shutil.copytree("imageformats", "%s/imageformats" % (pcloc))
shutil.copytree("smilies", "%s/smilies" % (pcloc))
f = open("%s/pesterchum.js" % (pcloc), 'w')
f.write("{\"tabs\":true, \"chums\":[]}")
f.close()
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcm90.dll", "%s" % (pcloc))
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcp90.dll", "%s" % (pcloc))
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/msvcr90.dll", "%s" % (pcloc))
shutil.copy("C:/Dev/Py26MSdlls-9.0.21022.8/msvc/x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375.manifest",
            "%s" % (pcloc))
shutil.copy("pesterchum.nsi", "%s/" % (pcloc))
shutil.copy("pesterchum-update.nsi", "%s/ % (pcloc)")
os.mkdir("%s/profiles" % (pcloc))
os.mkdir("%s/logs" % (pcloc))
shutil.copy("logs/chums.js", "%s/logs" % (pcloc))
shutil.copy("readme.txt", "%s/" % (pcloc))
shutil.copy("themes.txt", "%s/" % (pcloc))


