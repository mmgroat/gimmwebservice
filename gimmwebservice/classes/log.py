# Class Log
# Original Author: Michael Groat
# 7/1/2023

from classes.htmlpage import HTMLPage

class Log(HTMLPage):
   
    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree
 
    def render(self) -> str:

        def render_title() -> str:
            output = "<H1>Access Log</H1>\n"
            return output
       
        output = ""
        output += self.render_header() 
        output += render_title()
        output += "<HR>\n"
        output += "Access log information goes here<BR>\n"
        output += "<A HREF=\"/index\">Return to the master index</A><BR>\n"
        output += self.render_footer()
        return output
