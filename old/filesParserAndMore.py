from sys import argv
import xml.etree.ElementTree as ET
import urllib
import os
from os import path
import re
import subprocess
from itertools import chain
from os.path import expanduser
from usefulDefs.usefulDefs import (commonprefix, fcp7xmlParser, 
        fcpXMLParser, prprojParser, individualizeResolveImageSeqs, fileTypeDetector,
    doesPathExist)

#script, xmlFile = argv

InputFile = '/Users/jeromeraim/Desktop/XML testing/very weird chars.xml'


fileType = fileTypeDetector(InputFile)

###Figure out file type and return file paths
if fileType == 'fcp7XML':
    posixPaths = fcp7xmlParser(InputFile)
elif fileType == 'fcpXML':
    posixPaths = fcpXMLParser(InputFile)
elif fileType == 'prproj':
    posixPaths = prprojParser(InputFile)    

print '*'*30

resolveImageSeqDetected = bool()
print "Scanning for Resolve-type image sequences....."
for path in posixPaths:
    rResolveImageSeq = re.compile(r'\[\d.*-\d.*\]\..*')
    mResolveImageSeq = re.search(rResolveImageSeq, path)
    if mResolveImageSeq:
        resolveImageSeqDetected = True
        print "A Resolve-type image sequence was detected.\n"
        break
    else:
        print "No Resolve-type image sequences found."
        break
        
        
if resolveImageSeqDetected:
    print "Compiling list of individual images.\n"
    #listofIMGs = individualizeResolveImageSeqs(posixPaths)[0]
    posixPaths = list(set(individualizeResolveImageSeqs(posixPaths)))

    #print '\n'.join(posixPaths)

doesPathExist(posixPaths)

with open('/tmp/filepyFileParser.txt', 'w') as f:
    f.write('\n'.join(posixPaths))
#subprocess.call(["open", "-R", '/tmp/pyFileParser.txt'])


exit()





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

pathsWithDots = [i.replace(str(textToBeReplaced), str(withThat)) for i in posixPaths]

# print str(pathsWithDots)

filepathsReadyForCopy = '\n'.join(pathsWithDots)



#scpt = applescript.AppleScript("""choose folder""")
#destinationFolder = scpt.run()

print "You are copying this foler: %s." % startAtThisFolder
print "Into this one: %s" % destinationFolder
print "Proceed?"
choice = raw_input('> ')


rsyncScript = """xargs -J {} '/Applications/Jerome Apps/MediaFilesCollector/03 CopyWithFolderStructure v3.8.app/Contents/Resources/rsync' -tRP --perms -r --chmod=ugo=rwx --exclude= ".DS_Store" {} """ + "\'" + destinationFolder + "\'" 
#cmd = "echo %s | cat" % filepathsReadyForCopy
cmd = "echo %s | %s" % (filepathsReadyForCopy, rsyncScript)
print cmd



#subprocess.Popen(cmd, shell=True).wait()
   # return startAtThisFolder



