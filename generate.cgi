#!/usr/bin/env python3
import subprocess
import sys
import codecs
import re
import datetime
import time
import cgitb, cgi
import os
import pwd
import pyodbc
import json
from bs4 import BeautifulSoup

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
SOCK='/var/run/mysqld/mysqld.sock'
DRIVER="MySql ODBC 5.1 Driver"
def init():
    cgitb.enable()
    print("Content-type: text/html\n")
    os.environ['MYSQL_UNIX_PORT'] = SOCK




def getDb():
    try:
        arguments = cgi.FieldStorage()
        db = arguments["name"].value
    except KeyError:
        db = ""
    return db

def getFooter(duration):
    t = "Generated by <a href=\"https://github.com/deweyvm/starstats\">starstats</a>"
    return "<div id=\"footer\"><table><tr><td><center>%s on %s in %s.</center></td></tr></table></div>" % (t, time.ctime(), duration)

def printNotFound(exc, db):
    def makeDiv(s):
        pre = "<div class=\"tribox\"><div id=\"emptyhead\">"
        post = "</div><div class=\"tritext err\"></div></div>"
        return pre + s + post

    print("<html><head><title>starstats</title><link href=\"/starstats/css.css\" rel=\"stylesheet\" type=\"text/css\"/><link href=\"/favicon.ico?v=1.1\" rel=\"shortcut icon\"/></head><body>")
    headMsg = ""

    #SqlError {seState = "[\"42S02\"]", seNativeError = -1, seErrorMsg = "execute execute: [\"1146: [MySQL][ODBC 5.1 Driver][mysqld-5.5.37-0+wheezy1]Table 'talkhaus.rans' doesn't exist\"]"}

    try:
        s = re.search('SqlError[ ]*({[^}]*})', str(exc), re.IGNORECASE)
        g = str(s.groups(1))
        errorPart = ",".join(g.split(",")[2:])
        dequoted = errorPart.decode("string-escape").decode("string-escape")
        print(makeDiv("An error occurred:<br/>" + dequoted))
    except Exception as x:
        msg = "No records for channel '#%s'<br/>" % db
        print(makeDiv(msg))


    print(getFooter("0s"))


    print("<!-- %s -->" % str(exc))
    print("</body></html>")

def runProgram(driver, db):
    p = subprocess.Popen(['time ./starstats --driver=\"%s\" --db=%s  --generate' % (driver, db)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)

    (out, err) = p.communicate()
    if err is None:
        err = ""
    return (out.decode("utf-8", 'ignore'), err.decode("utf-8", 'ignore'), p.returncode)

def sanitize(s):
    return ''.join(c for c in s if c not in "{};\"=")

def checkOdbc(driver, db):
    try:
        import pyodbc
        cstr="DSN=starstats;Driver={%s};Server=localhost;Port=3306;Database=%s;User=root;Password=password;Option=3;" % (sanitize(driver), sanitize("starstats_" + db))

        cnxn = pyodbc.connect(cstr)
    except Exception as exc:
        printNotFound(exc, db)
        sys.exit(0)

def printOutput(out, timetaken):
    s = getFooter(timetaken)
    soup = BeautifulSoup(out)
    container = soup.body.find('div', attrs={'id':'container'})
    tag = soup.new_tag("div", id="footer")
    soup2 = BeautifulSoup(s)
    container.insert(len(container.contents), soup2)
    pretty = soup.prettify(formatter="html")
    #this fixes a bug where links have an underlined space after them
    print(re.sub("(\r\n|\n)[ ]*</a", "</a", pretty))

def handleErr(err, db):
    timetaken = "???"
    if len(err) > 0:
        lines = err.split("\n")
        for l in lines:
            print("<!-- %s -->" % l)
            if re.search("real\t", l) is not None:
                timetaken = re.sub(".*real\t*(.*)", "\\1", l)
    return timetaken

init()
db = getDb()
checkOdbc(DRIVER, db)
(out, err, retval) = runProgram(DRIVER, db)
timetaken="???"
if retval != 0:
    printNotFound(err, db)
    sys.exit(0)
timetaken = handleErr(err, db)
printOutput(out, timetaken)
