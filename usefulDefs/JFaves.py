import subprocess
import time


def getClipboardData():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    retcode = p.wait()
    data = p.stdout.read()
    return data

def setClipboardData(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()
    
def quoteDaFucker(element):
    element = "\"" + element + "\""
    return element

def timeStampDaFucker():
    currentTime = time.strftime('-%y%m%d_%I%M%S%p')
    return currentTime


