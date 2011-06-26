# runs pesterchum but appends stdout/err to log file
import subprocess
import datetime
f = open("debug.log", 'a')
d = datetime.datetime.now()
f.write("=== PESTERCHUM DEBUG %s ===\n" % d.strftime("%m-%d-%y %H-%M"))
f.flush()
p = subprocess.Popen("pesterchum.exe", stdout=f, stderr=subprocess.STDOUT)
p.wait()
f.close()
