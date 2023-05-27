gimmwebservice - GEDCOM in Memory Method (GIMM) Web Service
=======
_gimmwebservice_  is a python3 package that serves genealogy html pages (pedigree and descendency charts, individual sheets) from a GEDCOM on your local file system. It is designed to support and run quickly on a  GECOMM with hundreds of thousands of people. Tell the program where your GEDCOM is located, run it, then point your browser to http://127.0.0.1:5000 (TODO - see if IIS needs to be installed)

Advantages of GIMM:
=======
* The GEDCOM file is parsed into RAM memory when the web service loads. Eliminating the need to access the disk for each web page request. For a pedigree chart of tens of thousands of people, this loads pages quicker. This in spirit is a different method than IGM (Indexed GECOM Method) which heavily relies on disk usage. These are two trade-offs, GIMM needs RAM memory usage, while IGM runs slower with disk seeks, and is not designed for tens of thousands of people on its charts. To get a feel for RAM usage, on my local system, a GEDCOM of 100,000 people uses about 1 GB. However, it can quickly display a pedigree chart of 50,000 people (May need to use Firefox).
* Pedigree and descendency charts can collaspe any branch, or collaspe/expand all branchs at a certain generation level. This helps viewing charts of tens of thousands of people.
* Pedigree and descendency charts can support any number of generations. While tested with 200, this is designed to work with any number. To accompish this, repeated individuals are designated and linked as such, to prevent unchecked exponential growth.
* This program can be used with the github.com/Linekio/getmyancestors package (included with this program) to crawl and pull a GEDCOM from the FamilySearch.org site. Then, the GIMM webservice can point to the local downloaded GEDCOM to serve html pages and reports. This aids genealogy research of large numbers of people, since GIMM can easily and quickly serve and display tens of thousands of people on its pedigree or descendency charts. Instructions for getmyancesors are included below.

Usage:
=======
* <location where the repo was downloaded>/python3 gimmwebservice.py -g <relative or absolute path and filename of GEDCOM>
* for example: C:/Code/gimmwebservice/gimmwebservice/python3 gimmwebservice -g ../../personaldata/mygedcom.ged
* You may need to install libraries (TODO to package this repo to elivated this) with pip: pip install flask
* This script requires python3 and the modules indicated in the requirements.txt file. To install the modules, run in your terminal:
* Assumes indiviual 1 is in the GEDOM as @I1@. Individual 1 is used as the database owner (TODO - need the database owner's email)

Future Work:
=======
* This program is in the development phase, it is currently a work in progress, and bugs might be present. Features will be added on request. It is provided as is.
* As of 5/27/23, this still needs descendency charts, but pedigree charts are working and are almost complete
* Need to turn it into a package.
* The project is maintained at https://github.com/mmgroat/gimmwebservice. Visit here for the latest version and more information.

Support:
=======
* Submit questions or suggestions, or feature requests by opening an Issue at https://github.com/mmgroat/gimmwebservice/issues

Donations
========
If this project helps you, you can give me a tip :) Or if you want donate to help out current development. :)
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?business=YLBFKLXCCKRH6&no_recurring=0&item_name=printVeryLargeTextPedigrees+-+Donations+are+appreciated%21&currency_code=USD)

Installation
============
The easiest way to install _gimmwebservices__ is to use pip (TODO):

(TODO) `pip install printVeryLargeTextPedigrees`

Otherwise, you can download the source package and then execute:

(TODO) `python3 setup.py install`

(CURRENTLY) download the source package, navigate to the gimmwebservice directory and run python3 gimmwebservice.py -g <location and name of GEDCOM>
Then point your browser to http://127.0.0.1:5000/
Currenlty the only working URL is http://127.0.0.1:5000/individual/1/pedigree (To pull the pedigree chart of the first individual)

Webservice Endpoints:
==========
(Main index)
http://127.0.0.1:5000/ 
http://127.0.0.1:5000/individual
http://127.0.0.1:5000/individuals
http://127.0.0.1:5000/index

(Pedigree chart of individual <id>)
http://127.0.0.1:5000/individual/<id>/pedigree

(Individual sheet of individual <id>)
http://127.0.0.1:5000/individual/<id>

(Desendency chart of individual <id>)
http://127.0.0.1:5000/individual/<id>/descendents

Copyrights:
=======
* Copyrighted material from the Indexed Gedcom Method (IGM) (TODO - put in the names of the IGM copyright holders) is the indent subroutine on the pedigree chart, and the look of the rendered html pages
* GIMM copyrighted 2023 by Michael Groat and licensed under a GNU GPL.


How to use Linekio/getmyancestors
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

