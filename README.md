# GEDCOM in Memory Method (GIMM) Web Service

_GIMMwebservice_  A GEDCOM to WEB server that specializes in fast and efficient collapsible pedigree and descendency text charts for 50k+ individuals.  Written in Python, and using Flask, it parses large (100k+ individuals) GEDCOMs into primary memory (RAM), alleviating disk seeks in previous methods such as IGM, rendering web pages faster. 

## Advantages of GIMM

* The GEDCOM file is parsed into RAM memory when the web service loads, eliminating the need to access the disk multiple times for each web page request. For pedigree charts with tens of thousands of people, pages load quicker. This is differnt, in spirit, to IGM (Indexed GECOM Method), which heavily relies on disk usage from parsing a GEDCOM from web page requests.
* This program can be used with the http://github.com/Linekio/getmyancestors project, which crawls and pulls a GEDCOMs from the FamilySearch.org web site. This GIMM webservice can then display these downloaded GEDCOMs. 
* The larger collaspable pedigree and descendency text based charts aid in genealogy research for larger numbers of individuals. These charts can collaspe or expand any branch.
* Pedigree and descendency charts can support a variable number of generations well over 200. let me know if you need more. As a design decision, repeated individuals in charts are listed only once with links to their original apperance, to prevent unchecked exponential growth.
* No need to set up Perl CGI with you webserver (for IGM). Just run the program and Flask handles it. (You may need to install IIS with using Windows. I'll check into this).
* Minimal configuration is needed. Give the location of your GEDCOM file and an optional contact email on the command line.

## Usage

* python3 gimmwebservice.py -g ../../personaldata/mygedcom.ged -e CONTACTEMAIL
* You may need to install IIS, python, and python libraries (for example pip install flask). In the future I entend to package this repo, elivating this.
* This script requires python3 and the modules indicated in the requirements.txt file.
* This program assumes indiviual 1 is in the GEDOM as @I1@ and is used as the database owner.
* Point your browser to http://127.0.0.1:5000/. The port number is hard coded in the source and can be changed.

## Future Work

* This program is in the development phase; it is currently a work in progress, and bugs might be present. Features will be added on request. It is provided as is.
* It needs to turn it into a package.
* I need to check if IIS or apache needs to be installed.
* Image support
* Move the port number to the command line

## Support

* Submit questions, suggestions, or feature requests by opening an issue at https://github.com/mmgroat/gimmwebservice/issues.

## Webservice Endpoints:

### Main index:
* http://127.0.0.1:5000/
* http://127.0.0.1:5000/individual
* http://127.0.0.1:5000/individuals
* http://127.0.0.1:5000/index

### Individual sheet for individual {id}:
* http://127.0.0.1:5000/individual/{id}

### Pedigree chart for individual {id}:
* http://127.0.0.1:5000/individual/{id}/pedigree

### Desendency chart for individual {id}:
* http://127.0.0.1:5000/individual/{id}/descendents

## Copyrights:

* Copyrighted material from the Indexed Gedcom Method (TODO - put in the names of the IGM copyright holders) is in the indent subroutine on the pedigree chart, and the look of the rendered html pages.
* This project is forked from Linekio/getmyancestors. Some underlying data structures used in memory utilitize this copyrighted material.
* GIMMWebservice is copyrighted in 2023 by Michael M. Groat and licensed under a GNU GPL.
