printVeryLargeTextPedigrees or GIMM (Gedcom in Memory Method) webservice
==============

_printVeryLargeTextPedigrees_ (later perhaps _gimmwebservice_) is a python3 package (TODO - package-ize it) that downloads ancestors of a targeted individual, from either the FamilySearch.org site or a local file GEDCOM, and creates html, txt, or PDF pedigree files.

Future work of this project will take a local gedcom file and create a webservice that serves genealogical inforation: pedigree charts, descendent charts, family group sheets, etc. It is a successor to IGM (Index Gedcom Method) called GIMM (Gedcom in Memory Method). It is conceptually faster because each request avoids disk reads (secondary memory accessing).

The webserive is a Python webserive using the Flask framwork. 

These programs are designed to accomodate (and run fast on) 200 plus generations and hundreds of thousands of people. (If you need more generation support, just let me know). 

These programs are based (code wise) on getmyancestors (support by Linekio), and in spirt on IGM (Indexed Gedcom Method) by --- (TODO). The only copyrighted material from Indexed Gedcom Method (IGM) is the indent subroutine on the pedigree chart. In essences I'm building a successor to IGM which I call GIMM (Gedcom in Memory Method). 

It is conceptually faster than IGM because the gedcom is proceeed into memory datastructures at the webservice load time. Preventing disk reads (secondary memory reads) each time a page (for example a pedigree chart) is called. 
This has an the effect of displaying (rendering) several tens of thousands of people on a text (html) pedigree chart in less than a second (locally on my machine). 
In addition, on the HTML pedigree charts, you can collaspe any branch for easier navigation. The futre intent of development is to create a full gedcom navigation webservie, GIMM, but currently I'm focused on pedigree charts, since I find them useful for my research (since these charts contain tens of thousands of people scrapped from the FamilySearch.org site by "getmyancestors").

For now the title of this project is printVeryLargeTextPedigree, I may call it later GIMM, but I want to keep the designation that it is degined to create large pedigree charts in text form with HTML linking and branch collasping.

To conserve apace, repeated individuals are indicated as such, and in the html version, provides a link to the first occurance.

This program is in the development phase, it is currently a work in progress, and bugs might be present. Features will be added on request. It is provided as is.

The project is maintained at https://github.com/mmgroat/printVeryLargeTextPedigrees. Visit here for the latest version and more information.

This script requires python3 and the modules indicated in the requirements.txt file. To install the modules, run in your terminal:

(Right now, invoke the scripts directly through command line, working on getting packaging to work: 
printVeryLargeTextPedigrees:
   python3 -m printVeryLargeTextPedigrees <options>)
gimwebserivce: (TODO to make a package)
   pip install Flask
   python3 gimmwebservice.py -g <path and filename of GEDCOM file>

(for the webserive run "python -m flask run --app pedigreewebervice" -- TODO and can be accesed at http://127.0.0.1:5000/individual - which can be configured, currently just displays the pedgiree of the first person in the Gedcom, given that the attribute identifier for the person is @I1@)

Support
=======

Submit questions or suggestions, or feature requests by opening an Issue at https://github.com/mmgroat/printVeryLargeTextPedigrees/issues

Donations
========

If this project helps you, you can give me a tip :) Or if you want donate to help out current development. :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?business=YLBFKLXCCKRH6&no_recurring=0&item_name=printVeryLargeTextPedigrees+-+Donations+are+appreciated%21&currency_code=USD)


Installation
============

The easiest way to install _printVeryLargeTextPedigrees__ is to use pip:

`pip install printVeryLargeTextPedigrees`

Otherwise, you can download the source package and then execute:

`python3 setup.py install`

How to use
==========

With graphical user interface:

```
fstogedcom
```

Command line examples:

Download four generations of ancestors for the main individual in your tree and output gedcom on stdout (will prompt for username and password):

```
getmyancestors
```

Download four generations of ancestors and output gedcom to a file while generating a verbode stderr (will prompt for username and password):

```
getmyancestors -o out.ged -v
```

Download four generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
getmyancestors -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download six generations of ancestors for individual LF7T-Y4C and generate a verbose log file:

```
getmyancestors -a 6 -u username -p password -i LF7T-Y4C -o out.ged -l out.log -v
```

Download four generations of ancestors for individual LF7T-Y4C including all their children and their children spouses:

```
getmyancestors -d 1 -m -u username -p password -i LF7T-Y4C -o out.ged
```

Download six generations of ancestors for individuals L4S5-9X4 and LHWG-18F including all their children, grandchildren and their spouses:

```
getmyancestors -a 6 -d 2 -m -u username -p password -i L4S5-9X4 LHWG-18F -o out.ged
```

Download four generations of ancestors for individual LF7T-Y4C including LDS ordinances (need LDS account)

```
getmyancestors -c -u username -p password -i LF7T-Y4C -o out.ged
```

Merge two Gedcom files

```
mergemyancestors -i file1.ged file2.ged -o out.ged
```


