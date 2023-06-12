# coding: utf-8

# App: gimmwebservice
# Original Author - Michael Groat
# 5/27/2023

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
import time
import traceback
from datetime import datetime
from flask import Flask
from flask import request

# local imports
from classes.tree import Fam, Tree
from classes.pedigree import Pedigree
from classes.individualsheet import IndividualSheet
from classes.gedcom import Gedcom
from classes.masterindex import MasterIndex
#from classes.subindexes import SubIndexes
#from classes.session import Session

app = Flask(__name__)
debug = True

print("Starting parsing of GEDCOM")

parser = argparse.ArgumentParser(
    description="Create webservice from local gedcom file to serve genealogical HTML pages (May 21 2023)",
    add_help=False,
    usage="python -m flask --app gimmwebservice -g <gedcom relative path and file>",
)
parser.add_argument(
    "-e", 
    "--email", 
    metavar="<STR>", 
    type=str, 
    default=False,
    help="Contact Email",
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
time_count = time.time()
if not args.gedcom_input_file:
    sys.stderr.write("A GEDCOM file is required to run this webservice\n")
    sys.exit(2)
    
tree = Tree()
ged = Gedcom(args.gedcom_input_file, tree)
tree.lastmodifiedtime = datetime.fromtimestamp(os.path.getmtime(args.gedcom_input_file.name)).strftime('%B %d, %Y %H:%M:%S')
tree.contactemail = args.email
tree.gimmversion = "Version 0.01 (<A HREF=\"http://github.com/mmgroat/gimmwebservice\">Program Information</A>)"
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
tree.sources = ged.sour
tree.notes = ged.note
# tree.reset_num_no_fid(self)
pedigrees = Pedigree(tree)
individualsheets = IndividualSheet(tree)
masterindex = MasterIndex(tree)
masterindexoutput = masterindex.render()
#TODO: Question - Do we want to remove birth and death information for living individuals
# I've had people contact me in the past requesting this info not be posted.
# Perhaps an option for public/private tree viewing?
#if args.public == True:
#    tree = tree.privatize()

#TODO: Do we want to be able to put photos here? How does a photo work in a text pedigree?

print("Finished parsing GEDCOM into memory in %s seconds." % str(round(time.time() - time_count)))
sys.stdout.flush()

@app.get('/images/background')
def get_backgroundimage():
    return app.send_static_file('background.jpg')

@app.get('/individual/<indi_num>/pedigree')
def get_pedigree(indi_num):
   maxlevel = request.args.get('maxlevel')
   if maxlevel is None:
       maxlevel = 198 # 200 shows on chart
   else:
       maxlevel = int(maxlevel) - 2
       if maxlevel < -1:
           maxlevel = -1
   return pedigrees.render(int(indi_num), maxlevel)

@app.get('/individual/<indi_num>')
def get_individual_sheet(indi_num):
   return individualsheets.render(int(indi_num))

@app.get('/')
@app.get('/index')
@app.get('/index/')
def get_main_index():
    # Since this is more or less a static page - generate a string of the page when parsing GEDCOM and just send it on request, 
    # don't regenerate the string 
    return masterindexoutput # testing

@app.get('/index/<index_num>')
def get_sub_index(index_num):
    # Since these are more or less static pages - generate strings for each sub index page when parsing GEDCOM and just send each on request, 
    # don't regenerate any strings, 
    return masterindexoutput # testing

@app.get('/accesslog')
def get_access_log():
    # TODO: Need to record accesses (Are there going to be persistent?)
    return individualsheets.render(int(indi_num)) #testing

@app.get('/counters')
def get_counters():
    # maybe put these somewhere else in another page?
    return individualsheets.render(int(indi_num)) #testing

@app.get('/guestbook')
def get_guestbook():
    # Do we want to have a guestbook, and perhaps make it persistent?
    return individualsheets.render(int(indi_num)) #testing

@app.get('/search')
def search():
    # Do we want all searches to go here? String search and name seach?
    return individualsheets.render(int(indi_num)) #testing

@app.get('/download')
def get_gedcom():
    # Do we want to download seperate branchs?
    return individualsheets.render(int(indi_num)) #testing

@app.get('/createlink')
def put_link():
    # Do we even want to allow links? Seems dangerous nowadays, unless monitored before publish.
    # Could be the start of a wiki tree? How about adding/changing individuals? (WikiTree???)
    return individualsheets.render(int(indi_num)) #testing


# start the webserver
if __name__ == "__main__":
    app.debug = True
    app.run()
