# coding: utf-8

# global imports
#from __future__ import print_function
#import re
import sys
#import time
#from urllib.parse import unquote
#import getpass
#import asyncio
import argparse
import io
import os
from datetime import datetime
from flask import Flask
from flask import request

# local imports
from classes.tree import Fam, Tree
from classes.gedcom import Gedcom
#from classes.session import Session


app = Flask(__name__)
debug = True

print("Hellow World!")

parser = argparse.ArgumentParser(
    description="Create webservice from local gedcom file to serve genealogical HTML pages (May 21 2023)",
    add_help=False,
    usage="python -m flask --app gimmwebservice -g <gedcom relative path and file>",
)
try:
    parser.add_argument(
        "-g",
        "--gedcom-input-file",
        metavar="<FILE>",
        type=argparse.FileType("r", encoding="UTF-8-SIG"),
        default=False,
        help="input GEDCOM file [required]",
    )
except TypeError as e:
    sys.stderr.write("Python >= 3.4 is required to run this script\n")
    sys.stderr.write("(see https://docs.python.org/3/whatsnew/3.4.html#argparse)\n")
    if debug:
        print("An exception occurred:", e)
        traceback.print_exc()
    sys.exit(2)

returnHTML =  "<!DOCTYPE html>\n" \
    "<html lang=\"en\">\n" \
    "<meta charset=\"UTF-8\">\n" \
    "<title>Page Title</title>\n" \
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n" \
    "<link rel=\"stylesheet\" href=\"\">\n" \
    "<style>\n" \
    "</style>\n" \
    "<script src=\"\"></script>\n" +\
    "<body>\n" \
    "<img src=\"img_la.jpg\" alt=\"LA\" style=\"width:100%\">\n" \
    "<div class=\"\">\n" \
    " <h1>This is a Heading</h1>\n" \
    " <p>This is a paragraph.</p>\n " \
    " <p>This is another paragraph.</p> \n " \
    "</div>\n" \
    "</body>\n" \
    "</html>\n"

# extract arguments from the command line
try:
    parser.error = parser.exit
    args = parser.parse_args()
except SystemExit as e:
    parser.print_help(file=sys.stderr)
    if debug:
        print("An exception occurred:", e)
        traceback.print_exc()
    sys.exit(2)

# Load GedCom from file in a NonFS tree (doesn't assume FIDs exist)
if not args.gedcom_input_file:
    sys.stderr.write("A GEDCOM file is required to run this webservice\n")
    sys.exit(2)
tree = Tree()
ged = Gedcom(args.gedcom_input_file, tree)
tree.lastmodifiedtime = datetime.fromtimestamp(os.path.getmtime(args.gedcom_input_file.name)).strftime('%B %d, %Y %H:%M:%S')

fam_counter = 0
tree.indi = ged.indi
# Add parent information (to any GEDCOM (assume non FS))
for person_num in tree.indi:
    if tree.indi[person_num].famc_num:
        fam_num = list(tree.indi[person_num].famc_num)[0] # get perferred family only hence [0] (only for printing pedigrees, we aren't storing tree)
        if fam_num:
            mother, father = (ged.fam[fam_num].husb_num, ged.fam[fam_num].wife_num)
            if mother is not None or father is not None:
                tree.indi[person_num].parents.add((mother,father))
for num in ged.fam:
    husb, wife = (ged.fam[num].husb_num, ged.fam[num].wife_num)
    if (husb, wife) not in tree.fam:
        fam_counter += 1
        tree.fam[(husb, wife)] = Fam(husb, wife, tree, fam_counter)
        tree.fam[(husb, wife)].tree = tree
    tree.fam[(husb, wife)].chil_num |= ged.fam[num].chil_num
    if ged.fam[num].num:
        tree.fam[(husb, wife)].num = ged.fam[num].num
    if ged.fam[num].facts:
        tree.fam[(husb, wife)].facts = ged.fam[num].facts
    if ged.fam[num].notes:
        tree.fam[(husb, wife)].notes = ged.fam[num].notes
    if ged.fam[num].sources:
        tree.fam[(husb, wife)].sources = ged.fam[num].sources
    tree.fam[(husb, wife)].sealing_spouse = ged.fam[num].sealing_spouse
sys.stdout.write("Finished Parsing GedCom into Tree\n")
    # do we want notes - assume only read into memory, not written back to filesystem    
#tree.reset_num_no_fid(self)

@app.get('/individual/<indi_num>/pedigree')
def get_pedigree(indi_num):
   maxlevel = request.args.get('maxlevel')
   if maxlevel is None:
       maxlevel = 198 # 200 shows on chart
   else:
       maxlevel = int(maxlevel) - 2
       if maxlevel < -1:
           maxlevel = -1
   return tree.print_pedigree_html(int(indi_num), maxlevel)

@app.get('/images/background')
def get_backgroundimage():
    return app.send_static_file('background.jpg')

# start the webserver
if __name__ == "__main__":
    app.debug = True
    app.run()

