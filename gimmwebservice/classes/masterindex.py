# Class MainIndex
# Original Author: Michael Groat
# 6/11/2023

from classes.htmlpage import HTMLPage
import math

class MasterIndex(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render(self) -> str:

        output = self.render_header()

        # Output Header Name
        output += "<CENTER><H1>Master Index</CENTER></H1><HR>\n"
     
        output += "This genealogical database can be searched several ways:<br>\n"
        output += "<ul><li>TODO: Search for a name in the database.\n"
        output += "<li>TODO: Search for a string in the database.\n"
        output += "<li>TODO: Search an index of all surnames in the database.\n"
        output += "<li>TODO: Look at the database access log\n"
        output += "<li>Search the following sub-indexes:<br>\n"
        output += "<ul>\n"
        
        magicnum = str(math.ceil(math.sqrt(len(self.tree.indi))))
        output += "<li>" + magicnum + " pages of " + magicnum + " individuals<BR>\n"
        
        # TODO: Need to sort self.tree.indi based on surname, given name.

        output += "</ul></ul>\n"        

        output += self.render_footer()
        return output