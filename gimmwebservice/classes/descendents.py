# Class Descendents
# Original Author: Michael Groat
# 5/27/2023
#from ordered_set import OrderedSet
from classes.constants import (
    FACT_TYPES,
    MAX_GENERATIONS,
)

from classes.htmlpage import HTMLPage

class Descendents(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render(self, targetid, maxlevel = MAX_GENERATIONS) -> str:
        """print collaspable descendency chart in html from tree objet for target individual"""
      
        #linenumber = 0
        if maxlevel is None:
            maxlevel = MAX_GENERATIONS

        output = self.render_header()
        output += "<H1>Descendents of " + self.tree.indi[targetid].name.pretty_print() + "</H1>\n"

        #output += render_menu()
        output += self.render_footer()
        return output