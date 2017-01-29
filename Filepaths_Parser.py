from sys import argv
import xml.etree.ElementTree as ET
import urllib
import os
from os import path
import re
import subprocess
from itertools import chain
from os.path import expanduser
from usefulDefs.usefulDefs import *
from usefulDefs.JFaves import *
from args import *
import Tkinter, tkFileDialog

args = parser.parse_args()

if args.basic is False and args.wildcard is False and args.fullscan is False :
    parser.print_help()
    exit()

inputFile = args.inputFile
parsedFilename = os.path.basename(inputFile).split('.')[0]

#script, xmlFile = argv

#inputFile = '/Users/jeromeraim/Desktop/XML testing/Untitled.prproj'


fileType = fileTypeDetector(inputFile)

###Figure out file type and return file paths
if fileType == 'fcp7XML':
    OrigPosixPaths = fcp7xmlParser(inputFile)
elif fileType == 'fcpXML':
    OrigPosixPaths = fcpXMLParser(inputFile)
elif fileType == 'prproj':
    OrigPosixPaths = prprojParser(inputFile)
else:
    print "Unsupported file. Exiting."

prettySep()


### check for blabla.[001-0003].dpx type sequences
resolveIMGSeqDetected = bool()
print "Scanning for Resolve-type image sequences....."
for path in OrigPosixPaths:
    rResolveImageSeq = re.compile(r'\[\d.*-\d.*\]\..*')
    mResolveImageSeq = re.search(rResolveImageSeq, path)
    if mResolveImageSeq:
        resolveIMGSeqDetected = True
        print "A Resolve-type image sequence was detected."
        print "Breaking apart individual images."
        break
    else:
        print "No Resolve-type image sequences found."
        break
        

DecompPosixPaths = []
        
if resolveIMGSeqDetected:
    print "Compiling list of individual images.\n"
    #listofIMGs = individualizeResolveImageSeqs(OrigPosixPaths)[0]
    DecompPosixPaths = list(set(individualizeResolveImageSeqs(OrigPosixPaths)))


print 

### check if any file has .digits or _digits at the end and make it wildcard


if args.wildcard or args.fullscan:
    prettySep()
    imgSeqDetected = bool()
    print "Scanning for Premiere-type image sequences....."
    print "Note: If media is offline, no images within the sequence will be detected." 
    for path in OrigPosixPaths:
        rImageSeq = re.compile(r'.*/(.*(_|\.))\d{1,8}\.(ari|dpx|jpg|ex3|tiff|tif|png|exr)$', re.IGNORECASE)
        mImageSeq = re.search(rImageSeq, path)
        if mImageSeq:
            imgSeqDetected = True
            print "A regular image sequence was detected."
            print "Breaking apart individual images....."
            break
        else:
            print "No regular image sequences found."
            break
    
    if imgSeqDetected:
        DecompPosixPaths = list(set(individualizeImageSeqs(OrigPosixPaths)))
        DecompPosixPaths.sort()
    
    prettySep()
    
    redSpannedDetected = bool()
    print "Scanning for spanned RED media....."
    print "Note: If media is offline, no RED media will be detected." 
    
    for path in OrigPosixPaths:
        rRed = re.compile(r'.*\/(.*._)(\d{3}).R3D$', re.IGNORECASE)
        mRed = re.search(rImageSeq, path)
        if mRed:
            redSpannedDetected = True
            print "Spanned RED media detected."
            print "Grabbing all spanned media....."
            break
        else:
            print "No RED media found."
            break
    
    if redSpannedDetected:
        #listofIMGs = individualizeResolveImageSeqs(OrigPosixPaths)[0]
        DecompPosixPaths = list(set(individualizeImageSeqs(OrigPosixPaths)))
        DecompPosixPaths.sort()
        #print '\n'.join(OrigPosixPaths)

if args.skipOffline is False:
    if args.basic:
        ListOfofflineFiles = doesPathExist(OrigPosixPaths)
    else:
        ListOfofflineFiles = doesPathExist(DecompPosixPaths)
    

prettySep()

####save reports
# print "Check your dock for the python spaceship. Select the folder which will house the reports."
# root = Tkinter.Tk()
# root.withdraw()
# dirname = tkFileDialog.askdirectory(parent=root,initialdir='~/Desktop/',title='A time-stamped subfolder will be created at this location.')
# if len(dirname ) > 0:
#     filepaths_ParserReportsDir = dirname + '/' + 'JRAIM_LOGS/FILEPATH_PARSER_REPORTS/' + parsedFilename + timeStampDaFucker() + '/'
#     #print filepaths_ParserReportsDir
# else:
#     print 'Exiting.'
#     exit()


filepaths_ParserReportsDir = os.path.expanduser('~/Documents/RaimApps/Filepath Parser Reports/' + parsedFilename + timeStampDaFucker() + '/')

os.makedirs(filepaths_ParserReportsDir)

print "Writing data to text files...."
initialAssessmentFile  = '%s/ListOfFiles_initialAssessment%s.txt' % (filepaths_ParserReportsDir, timeStampDaFucker())
BrokenApartFile  = '%s/ListOfFiles_BrokenApart%s.txt' % (filepaths_ParserReportsDir, timeStampDaFucker())
offlineFile = '%s/ListOfOfflineFiles%s.txt' % (filepaths_ParserReportsDir, timeStampDaFucker())

with open(initialAssessmentFile, 'w') as f:
    print "Saving %s" % initialAssessmentFile
    f.write('\n'.join(OrigPosixPaths))

if args.wildcard is True or args.fullscan is True:
    print "Saving %s" % BrokenApartFile
    with open(BrokenApartFile, 'w') as f:
        f.write('\n'.join(DecompPosixPaths))

if args.skipOffline is False:
    if len(ListOfofflineFiles) >= 1:
        with open(offlineFile, 'w') as f:
            print "Saving %s" % offlineFile
            f.write('\n'.join(ListOfofflineFiles))
    
#print "List of files - initial assessment:\n%s" % initialAssessmentFile

print """Process complete. Do you wish to open the Folder with the list of files?
Hit ENTER for YES or Ctrl+C to cancel"""
showFolder = raw_input('\n> ')

if 'y' or '' in showFolder:
    subprocess.call(["open", "-R", initialAssessmentFile])
else:
    exit()

exit()

