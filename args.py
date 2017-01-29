import argparse
import sys


parser = argparse.ArgumentParser(description='Parse file paths from documents.')
 
parser.add_argument('-b', '--basic',
    action="store_true",
    help="Extract file paths as is, without additional manipulation (no img sequence or spanned clips detection " )
 
parser.add_argument('-w', '--wildcard',
    action="store_true",
    help="Remove img sequence spanned Red media numbers and replace with an '*'")

parser.add_argument('-f', '--fullscan',
    action="store_true",
    help="Find all related content for img sequences and red media. Doesn't work if media is offline")
 
parser.add_argument('inputFile',
    help="File to be parsed for file paths within it")

parser.add_argument('--skipOffline',
    action="store_true",
    help="Find all related content for img sequences and red media. Doesn't work if media is offline") 
 
