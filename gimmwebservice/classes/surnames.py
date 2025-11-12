# Class Surnames
# Original Author: Michael Groat
# 7/1/2023

from .htmlpage import HTMLPage
import math

class Surnames(HTMLPage):
   
    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree
        self.magicnum = math.ceil(math.sqrt(len(self.tree.indi)))

    def render(self) -> str:

        def render_title() -> str:
            return "<H1>Surname Index</H1>\n"
     
        output = ""
        output += self.render_header() 
        output += render_title()
        output += "<HR>\n"

        previous_surname = None
        previous_first_letter = None
        individual_num = 0
        for indiv in self.tree.sorted_individuals:
            if len(self.tree.sorted_individuals[indiv].name.surname) > 0 and \
                    self.tree.sorted_individuals[indiv].name.surname != previous_surname:
                first_letter = self.tree.sorted_individuals[indiv].name.surname[0]
                if previous_first_letter is not None and first_letter != previous_first_letter: 
                    output += "<HR>\n"
                else:
                    if previous_surname is not None:
                        output += ", "                
                index_num = (individual_num // self.tree.magicnum)
                output += "<A HREF=\"/index/" + str(index_num) + "#" + self.tree.sorted_individuals[indiv].name.surname + \
                    "\">" + self.tree.sorted_individuals[indiv].name.surname + "</A>"
                previous_surname = self.tree.sorted_individuals[indiv].name.surname        
                previous_first_letter = first_letter
            individual_num += 1
        output += "<BR><A HREF=\"/index\">Return to the master index</A><BR>\n"
        output += self.render_footer()
        return output
