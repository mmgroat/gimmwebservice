# Class HTMLPage
# Original Author - Michael Groat
# 5/27/2023

from filelock import Timeout, FileLock

class HTMLPage:

    def __init__(self):
        self.backgroundcolor = "#BFBFBD" # Should come from config file?
        self.linkcolor = "#0000EE" # Should come from config file?
        self.visitedlinkcolor = "#551A8B" # Should come from config 
        self.logfilelock = "log.txt.lock"
        self.logfile = "log.txt"

    def render_header(self) -> str:
        """Prints HTML top part of page """
        # Should this go in another class like an HTMLRender class?
        title = self.tree.indi[1].name.pretty_print() + "'s Genealogical Database"
        output = "<HTML lang=\"en\">\n"
        output += "<HEAD>\n"
        output += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
        output += "<TITLE>" + title + "</TITLE>\n"
        output += "<STYLE> div { display:inline; } </STYLE\n"
        output += "</HEAD>\n"
        output += "<BODY BACKGROUND=\"/images/background\" BGCOLOR=\"" + self.backgroundcolor 
        output += "\" TEXT=\"#000000\" LINK=\"" + self.linkcolor + "\" VLINK=\"" + self.visitedlinkcolor + "\">\n"
        output += "<CENTER><H2>" + title + "</H2></CENTER>\n";
        output += "<CENTER><B>Individuals:</B> " + f"{len(self.tree.indi):,}" + "&nbsp;&nbsp;"
        output += "<B>Families:</B> " + f"{len(self.tree.fam):,}" + "&nbsp;&nbsp;"
        output += "<BR><B>Gedcom Last Modified:</B> " + str(self.tree.lastmodifiedtime) + "</CENTER>\n<HR>\n"
        #output += "<CENTER><B>Contact:</B> <A href=\"" + contact_email + "\">Michael M. Groat</A> &nbsp;&nbsp; "
        #output += "<B>Home Page:</B> <A href=\"" + home_page_url + "\">" + self.indi[1].name.pretty_print() + "'s Homepage</A></CENTER>"
        return output

    def render_footer(self) -> str:
        """Prints HTML bottom part of page """
        output = "<HR><EM>Please send genealogical corrections, additions, or comments to </EM>"
        if self.tree.contactemail:
           output += "<A HREF=\"mailto:" + self.tree.contactemail + "\">"
        output += self.tree.indi[1].name.pretty_print()
        if self.tree.contactemail:
            output += "</A>"
        output += "\n<HR>Created by GIMMWebService " + self.tree.gimmversion 
        output += ", Copyright 2023 &copy <A HREF=\"http://github.com/mmgroat\">Michael Groat</A><BR>\n"
        output += "(Web design layout and pedigree indentation subroutine) Copyright 1996 &copy; Randy Winch (gumby@edge.net) and Tim Doyle (tdoyle@doit.com)<BR>\n"
        output += "(Internal GEDCOM data structures and GEDCOM file parsing) Copyright 2014-2021 &copy; Giulio Genovese (giulio.genovese@gmail.com)<BR><BR>\n"
        output += "Like the program that you see? Any support is appreciated!<br><br>\n"
        output += "<a href=\"https://www.paypal.com/donate/?business=YLBFKLXCCKRH6&no_recurring=0&item_name=printVeryLargeTextPedigrees+-+Donations+are+appreciated%21&currency_code=USD\""
        output += "><img src=\"https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif\" alt=\"Paypal\"/></a><BR><BR>\n"
        output += "<BR><BR><BR>\n"
        output += "</BODY>\n</HTML>\n"
        return output
    
    def log(self, logmessage):
        lock = FileLock(self.logfilelock, timeout=1)
        with lock:
            with open(self.logfile, 'a') as file:
                file.write(logmessage)
