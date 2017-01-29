from sys import argv

import os
from os import path
import re
import subprocess
from itertools import chain
from os.path import expanduser
from usefulDefs.usefulDefs import *
from usefulDefs.JFaves import *
import applescript


from subprocess import Popen, PIPE
import errno

with open('/Users/jeromeraim/Downloads/paths.txt', 'r') as f:
    posixPaths = f.read().splitlines()

#posixPaths = getClipboardData().splitlines() 


if 'Volumes' not in posixPaths[0]:
    print "No filepaths detected. Exiting."
    exit()

#print posixPaths

##convert /Users/xxx paths to full /Volumes path
pipe = subprocess.Popen("""osascript -e 'tell app "finder" to get name of the startup disk'""",
                        stdout=subprocess.PIPE, shell=True)
startupDisk = (pipe.stdout.read()).split('\n', 1)[0]

#posixPaths = [("/Volumes/%s%s" % (startupDisk, path)) if "/Users" in path else path for path in posixPaths]


prefix = commonprefix(posixPaths)

print "\nThe common path for all files is %s" % prefix

whichFolderToCopy = prefix.split('/')[1:]

print "\nChoose the first folder to create (type its number):"


count = 1
indexMapping = {}
for i, chosenFolder in enumerate(whichFolderToCopy):
    print '{0:3d} - {1}'.format(count, chosenFolder)
    indexMapping[count] = i
    count += 1
#return indexMapping

choice = raw_input('> ')
startAtThisFolder = whichFolderToCopy[indexMapping[int(choice)]]

textToBeReplaced = whichFolderToCopy[indexMapping[int(choice)]:]

textToBeReplaced = '/'.join(textToBeReplaced)
withThat = "./" + str(textToBeReplaced)

# print "textToBeReplaced = ", textToBeReplaced
# print "withThat = ",  withThat

pathsWithDots = [i.replace(str(textToBeReplaced), str(withThat))
                 for i in posixPaths]

# print str(pathsWithDots)

filepathsReadyForCopy = b'\x00'.join(pathsWithDots)



# scpt = applescript.AppleScript("""choose folder""")
# destinationFolder = scpt.run()

destinationFolder = '/Users/jeromeraim/Downloads/dest'

# print "You are copying this foler: %s." % startAtThisFolder
# print "Into this one: %s" % destinationFolder
# print "Proceed?"
# choice = raw_input('> ')


rsyncScript = """xargs -0 -J {} '/Applications/Jerome Apps/MediaFilesCollector/03 CopyWithFolderStructure v3.8.app/Contents/Resources/rsync' -tRP --perms -r --chmod=ugo=rwx --exclude= ".DS_Store" {} """ + "\'" + destinationFolder + "\'" 
#cmd = "echo %s | cat" % filepathsReadyForCopy
# cmd = "echo %s | %s" % (filepathsReadyForCopy, rsyncScript)
# print cmd
# process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
# stdout, stderr = process.communicate()

print filepathsReadyForCopy
print rsyncScript
print '@@@@'

# p = subprocess.Popen(rsyncScript,stdout=subprocess.PIPE,stdin=subprocess.PIPE, shell=True)
# p = p.stdin.write(filepathsReadyForCopy)
# for line in iter(p.stdout.readline, ""):
#     print line,

p = Popen(rsyncScript, stdin=PIPE)

for f in 1:
    try:
        p.stdin.write(filepathsReadyForCopy)
    except IOError as e:
        if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
            # Stop loop on "Invalid pipe" or "Invalid argument".
            # No sense in continuing with broken pipe.
            break
        else:
            # Raise any other error.
            raise

p.stdin.close()
p.wait()

#print "\r" + p.communicate()[0],

#print p.stdout


#p.stdin.close()

