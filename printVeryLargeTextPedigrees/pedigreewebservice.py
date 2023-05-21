# coding: utf-8

# global imports
#from __future__ import print_function
#import re
#import sys
#import time
#from urllib.parse import unquote
#import getpass
#import asyncio
#import argparse
import io

# local imports
from classes.tree import Fam, Tree
from classes.gedcom import Gedcom
#from classes.session import Session

from flask import Flask

app = Flask(__name__)


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

tree = Tree()
print("Hellow World!")
# Load from file

input_file = io.open("GroatFamily.large.ged","r",encoding='utf-8-sig')
ged = Gedcom(input_file, tree)
tree.indi = ged.indi

fam_counter = 0

for person_num in tree.indi:
    if tree.indi[person_num].famc_num:
        fam_num = list(tree.indi[person_num].famc_num)[0] # get perferred family only (only for printing pedigrees, we aren't storing tree)
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
    # do we want notes - assume only read into memory, not written back to filesystem    
    
@app.get('/individual')
def get_pedigree():
   return tree.print_pedigree_html(int(1))
   
   
# start the webserver
if __name__ == "__main__":
    app.debug = True
    app.run()

