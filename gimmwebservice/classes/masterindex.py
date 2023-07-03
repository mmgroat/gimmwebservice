# Class MainIndex
# Original Author: Michael Groat
# 6/11/2023

from classes.htmlpage import HTMLPage
import math
import sys

class MasterIndex(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render_links(self) -> str:
        output = "<li><A HREF=\"/search\">Search the database</a>\n"
        output += "<li><A HREF=\"/surnames\">Search an index of all surnames in the database</a>\n"
        output += "<li><A HREF=\"/logs\">Look at the database access log</a>\n"
        return output

    def render_master(self) -> str:
        output = self.render_header()
        output += "<CENTER><H1>Master Index</CENTER></H1><HR>\n"
        output += "This genealogical database can be searched several ways:<br>\n"
        output += "<ul>\n"
        output += self.render_links()
        output += "<li>Search the following sub-indexes:<br>\n"
        output += "<ul>\n"
        individuallist = list(self.tree.sorted_individuals.items())
        for i in range(self.tree.magicnum):
            startperson = individuallist[self.tree.magicnum * i]
            if self.tree.magicnum * i + self.tree.magicnum - 1 >= len(individuallist):
                endperson = individuallist[len(individuallist) - 1]
            else: 
                endperson = individuallist[self.tree.magicnum * i + self.tree.magicnum - 1]
            output += "<li><A HREF=\"/index/" + str(i) + "\"><B>" + \
                startperson[1].name.surname + ", " + \
                startperson[1].name.given + " -- " + \
                endperson[1].name.surname + ", " + \
                endperson[1].name.given + "</B></A>\n"
        output += "</ul></ul>\n"        
        output += self.render_footer()
        return output
    
    def render_submaster(self, submasternum) -> str:
        output = self.render_header()
        output += "<CENTER><H2>Sub Index</H2></CENTER><HR>\n"
        output += "This genealogical database can be searched several ways:<br>\n"
        output += "<ul><li><A HREF=\"/index\">Return to the Master Index</A>\n"
        output += self.render_links()
        output += "<li>View information for the following invidivuals:<br>\n"
        output += "<ul>\n"
        startpersonindex = (self.tree.magicnum * submasternum)
        endpersonindex = (self.tree.magicnum * submasternum) + self.tree.magicnum - 1
        if startpersonindex == 0:
            previous_last_name = None
        else:
            previous_last_name = list(self.tree.sorted_individuals.items()).pop(startpersonindex - 1)[1].name.surname
        individualsublist = dict(list(self.tree.sorted_individuals.items())[startpersonindex:endpersonindex+1])
        for indi in individualsublist:
            if previous_last_name != individualsublist[indi].name.surname:
                output += "<A NAME=\"" + individualsublist[indi].name.surname + "\"></A>"
                previous_last_name = individualsublist[indi].name.surname
            output += "<li><A HREF=\"/individual/" + str(indi) + "\"><B>" + \
                individualsublist[indi].name.surname + ", " + \
                individualsublist[indi].name.given + "</B></A> " + \
                individualsublist[indi].pretty_print_birth() + \
                individualsublist[indi].pretty_print_death() + "<BR>\n"                
        output += "</ul></ul>\n"   
        if submasternum > 0:
            output += "<A HREF=\"/index/" + str(submasternum - 1) + "\">Pervious Index Page</A><BR>\n"
        if submasternum < self.tree.magicnum - 1:
            output += "<A HREF=\"/index/" + str(submasternum + 1) + "\">Next Index Page</A><BR>\n"
        output += self.render_footer()
        return output
