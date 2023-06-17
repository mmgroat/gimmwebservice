# Class MainIndex
# Original Author: Michael Groat
# 6/11/2023

from classes.htmlpage import HTMLPage
import math

class MasterIndex(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree
        self.sorted_individuals = dict(sorted(self.tree.indi.items(), key=lambda x:(x[1].name.surname, x[1].name.given)))
        self.magicnum = math.ceil(math.sqrt(len(self.tree.indi)))

    def render_master(self) -> str:
        output = self.render_header()
        output += "<CENTER><H1>Master Index</CENTER></H1><HR>\n"
        output += "This genealogical database can be searched several ways:<br>\n"
        output += "<ul><li>TODO: Search for a name in the database.\n"
        output += "<li>TODO: Search for a string in the database.\n"
        output += "<li>TODO: Search an index of all surnames in the database.\n"
        output += "<li>TODO: Look at the database access log\n"
        output += "<li>Search the following sub-indexes:<br>\n"
        output += "<ul>\n"
        individuallist = list(self.sorted_individuals.items())
        print("Individualist len is " + str(len(individuallist)) + "\n")

        for i in range(self.magicnum):
            startperson = individuallist[self.magicnum * i]
            if self.magicnum * i + self.magicnum - 1 >= len(individuallist):
                endperson = individuallist[len(individuallist) - 1]
            else: 
                endperson = individuallist[self.magicnum * i + self.magicnum - 1]
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
        output += "<li>TODO: Search for a name in the database.\n"
        output += "<li>TODO: Search for a string in the database.\n"
        output += "<li>TODO: Search an index of all surnames in the database.\n"
        output += "<li>TODO: Look at the database access log\n"
        output += "<li>View information for the following invidivuals:<br>\n"
        output += "<ul>\n"
        startpersonindex = (self.magicnum * submasternum)
        endpersonindex = (self.magicnum * submasternum) + self.magicnum - 1
        #print("Start person is " + str(startpersonindex) + " , End person is " + str(endpersonindex) + "\n")
        #print("Size of sorted_individuals is " + str(len(self.sorted_individuals)) + "\n")
        individualsublist = dict(list(self.sorted_individuals.items())[startpersonindex:endpersonindex+1])
        for indi in individualsublist:
            output += "<li><A HREF=\"/individual/" + str(indi) + "\"><B>" + \
                individualsublist[indi].name.surname + ", " + \
                individualsublist[indi].name.given + "</B></A> " + \
                individualsublist[indi].pretty_print_birth() + \
                individualsublist[indi].pretty_print_death() + "<BR>\n"                
        output += "</ul></ul>\n"        
        output += self.render_footer()
        return output
