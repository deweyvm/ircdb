#!/usr/bin/env python
import subprocess
import datetime
import time
t = time.clock()
env = {'MYSQL_UNIX_PORT':'/var/run/mysqld/mysqld.sock'}
p = subprocess.Popen(["./ircdb \"MySql ODBC 5.1 Driver\" -g"],
                     stdout=subprocess.PIPE,
                     env=env,
                     shell=True)
print("Content-type: text/html\n")

print(p.stdout.read())

p.wait()
duration = time.clock() - t
print('<div id="footer">Generated by ircdb on %s in %.2f seconds.</div>' % (datetime.datetime.now(), duration))
