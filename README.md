printVeryLargeTextPedigrees
==============

_printVeryLargeTextPedigrees_ is a python3 package that downloads ancestors of a targeted individual from FamilySearch and creates html, txt or PDF pedigree files. It is meant to show up to 200 generations. The html version allows collasping and expanding of any branches. To conserve apace, repeated individuals are indicated as such, and in the html version, provides a link to the first occurance.

This program is in the development phase, it is currently a work in progress, and bugs might be present. Features will be added on request. It is provided as is.

The project is maintained at https://github.com/mmgroat/printVeryLargeTextPedigrees. Visit here for the latest version and more information.

This script requires python3 and the modules indicated in the requirements.txt file. To install the modules, run in your terminal:

(Right now, invoke the script directly through command line, working on getting packaging to work: C:\python3 -m printVeryLargeTextPedigrees <options>)

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


Support
=======

Submit questions or suggestions, or feature requests by opening an Issue at https://github.com/mmgroat/printVeryLargeTextPedigrees/issues

Donation
========

If this project helps you, you can give me a tip :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?business=YLBFKLXCCKRH6&no_recurring=0&item_name=printVeryLargeTextPedigrees+-+Donations+are+appreciated%21&currency_code=USD)
