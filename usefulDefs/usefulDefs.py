import re
#import xml.etree.ElementTree as ET
#from lxml import etree 
import urllib
import os
import subprocess
import zlib
from itertools import chain
import glob
from args import *

#args = parser.parse_args()

pipe = subprocess.Popen("""osascript -e 'tell app "finder" to get name of the startup disk'""",
                        stdout=subprocess.PIPE, shell=True)
startupDisk = (pipe.stdout.read()).split('\n', 1)[0]

def prettySep():
    print '\n' + '*'*30 + '\n'  

def fctForAllPaths(posixPaths):

    posixPaths = [re.sub('///Volumes', '/Volumes', path) for path in posixPaths]

    newList = list(set(posixPaths))
    newList.sort()
#report initial assessment of # of files
    posixPaths = newList

    posixPaths = [path.encode('utf-8') for path in posixPaths]
 
    prettySep()
    
    print "Initial assessment:"    
    if len(posixPaths) >= 2:
        print "\n%s files detected" % len(posixPaths)
    elif len(posixPaths) == 1:
        print "\n%s file detected" % len(posixPaths)
    elif len(posixPaths) == 0:
        print "\nNo files were detected. Exiting."
        exit()

    #print "\n".join(posixPaths)
    return posixPaths

    return posixPaths



def fcp7xmlParser(InputFile):

    tree = ET.parse(InputFile)
    root = tree.getroot()
    
    urlPaths = []
    posixPaths = []
    
    for elem in tree.iter(tag='pathurl'):
        urlPaths.append(elem.text)   
                           
    for path in urlPaths:
        posixPaths.append(urllib.url2pathname(path))  
    
    posixPaths = [path.replace('file://', '') for path in posixPaths]  
    posixPaths = [path.replace('localhost', '') for path in posixPaths]   
    
    posixPaths = ([("/Volumes/%s%s" % (startupDisk, path)) if "/Users" in path
                   else path for path in posixPaths])
            
    posixPaths = [os.path.normpath(path) for path in posixPaths]
    
    posixPaths = fctForAllPaths(posixPaths)


def fcpXMLParser(InputFile):
    with open(InputFile) as xmlFile:
        tree = etree.parse(xmlFile)
            
        urlPaths = []
        posixPaths = []
        
        for elem in tree.iter('asset'):
            urlPaths.append(elem.attrib['src'])
                               
        for path in urlPaths:
            
            posixPaths.append(urllib.url2pathname(path))  
        
        posixPaths = [path.replace('file://', '') for path in posixPaths]  
        posixPaths = [path.replace('localhost', '') for path in posixPaths]   
        
        posixPaths = ([("/Volumes/%s%s" % (startupDisk, path)) if not path.startswith("/Volumes")
                       else path for path in posixPaths])
        
        posixPaths = [path.encode('utf-8') for path in posixPaths] 
            
    posixPaths = fctForAllPaths(posixPaths)
    return posixPaths
    
def prprojParser(InputFile):
    print 'Parsing.....'
    with open(InputFile) as f:
        decompressed_data = zlib.decompress(f.read(), 16+zlib.MAX_WBITS)

    tree = etree.ElementTree(etree.fromstring(decompressed_data))
            
    posixPaths = []
    
    for elem in tree.iter('ActualMediaFilePath'):
        posixPaths.append(elem.text)
        
    posixPaths = ([("/Volumes/%s%s" % (startupDisk, path)) if path.startswith("/Users/")
              else path for path in posixPaths])

    posixPaths = [path for path in posixPaths if (not "PRV/Rendered" in  path) and ("Volumes" in path)]
        
    posixPaths = fctForAllPaths(posixPaths)
    return posixPaths


def fileTypeDetector(InputFile):
    print "Detecting input file type....."
    fileType = str()
    if InputFile.endswith('.xml'):
        with open(InputFile) as xmlContent:
            xmlContent = xmlContent.read().splitlines()[2]
        if "<xmeml version=\"" in xmlContent:
            fileType = 'fcp7XML'
        else:
            fileType = 'unsupported'
    elif InputFile.endswith('.prproj'):
        fileType = 'prproj'
    elif InputFile.endswith('.fcpxml'):
        fileType = 'fcpXML'
    else:
        fileType = 'other'
    print "The provided file is a %s" % fileType
    return fileType


def individualizeResolveImageSeqs(posixPaths):
    #print "Scanning the Resolve-type image sequences....."

    listofIMGs = []
    posixPathsWithoutFakeFiles = [] ##make list of files that are not involved with this process
    for path in posixPaths:
        rResolveImageSeq = re.compile(r'\[\d.*-\d.*\]\..*')
        mResolveImageSeq = re.search(rResolveImageSeq, path)
        if mResolveImageSeq:
            basepath = os.path.dirname(path)
            daFile = os.path.basename(path)
            daExt = os.path.basename(path).split('.')[-1]

            if '.[' in daFile:
                fileNoNumb = daFile.split('.[')[-2]
            elif '_[' in daFile:
                fileNoNumb = daFile.split('_[')[-2]
                
            frameIn = re.search(r"\[(\d.*)-", daFile).group(1)
            frameOut =  re.search(r".*\[\d.*-(\d.*)]", daFile).group(1)

            numofDigits = str(len(frameIn))

            numFormat = '{0:0%sd}' % numofDigits
            
            for x in range(int(frameIn), (int(frameOut)+1)):
                indivIMG = basepath + '/' + fileNoNumb + '.' + numFormat.format(x) + '.' + daExt
                listofIMGs.append(indivIMG)
        else:
            posixPathsWithoutFakeFiles.append(path)
    print "Breaking apart finished."
    return chain(listofIMGs, posixPathsWithoutFakeFiles)

def individualizeImageSeqs(posixPaths):

    listofIMGs = []
    posixPathsWithoutFakeFiles = [] ##make list of files that are not involved with this process
    for path in posixPaths:
        rImageSeq = re.compile(r'.*/(.*(_|\.))\d{1,8}\.(ari|dpx|jpg|ex3|tiff|tif|png|exr)$')
        mImageSeq = re.search(rImageSeq, path)
        if mImageSeq:
            basepath = os.path.dirname(path)
            daFile = os.path.basename(path)
            fileNoNumb = basepath + '/' + mImageSeq.group(1) + '*'
            
            if args.fullscan is True:
                for name in glob.glob(fileNoNumb):
                    listofIMGs.append(name)
            else:
                listofIMGs.append(fileNoNumb)
        else:
            posixPathsWithoutFakeFiles.append(path)
    print "Breaking apart finished."
    return chain(listofIMGs, posixPathsWithoutFakeFiles)



def findAllRedMedia(posixPaths):

    redMedia = []
    posixPathsWithoutFakeFiles = [] ##make list of files that are not involved with this process
    for path in posixPaths:
        rREDmedia = re.compile(r'.*\/(.*._)(\d{3}).R3D$', re.IGNORECASE)
        mREDmedia = re.search(rREDmedia, path)
        if rREDmedia:
            basepath = os.path.dirname(path)
            #daFile = os.path.basename(path)
            fileNoNumb = basepath + '/' + mREDmedia.group(1) + '*'
            
            if args.fullscan:
                for name in glob.glob(fileNoNumb):
                    redMedia.append(name)
            else:
                redMedia.append(fileNoNumb)
        else:
            posixPathsWithoutFakeFiles.append(path)
    print "Breaking apart finished."
    return chain(redMedia, posixPathsWithoutFakeFiles)


def doesPathExist(posixPaths):
    prettySep()
    print 'Checking for offline files.....'
    print 
    theseExist = []
    theseDontExist = []
    for path in posixPaths:
        if os.path.exists(path):
            theseExist.append(path)
        else:
            theseDontExist.append(path)
    prettySep()
    print "Final assessment:"
    print "%s files detected." % len(posixPaths)
    print "%s appear online." % len(theseExist)
    print "%s appear offline." % len(theseDontExist)
    
#     if len(theseDontExist) >= 1:
#         print "Offline file(s):"
#         print '\n'.join(theseDontExist)
    return theseDontExist

    
 


def commonprefix(l):
    cp = []
    ls = [p.split('/') for p in l]
    ml = min( len(p) for p in ls )

# if ls generates a file path (ends with .xxx), then remove the file from the list
    if re.search(r'\..{2,4}$', ls[0][-1]) is not None:
        del ls[0][-1]
        ml = min( len(p) for p in ls )
          
    for i in range(ml):
        s = set( p[i] for p in ls )         
        if len(s) != 1:
            break

        cp.append(s.pop())

    return '/'.join(cp)