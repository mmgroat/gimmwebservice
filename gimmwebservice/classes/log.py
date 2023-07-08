# Class Log
# Original Author: Michael Groat
# 7/1/2023

from classes.htmlpage import HTMLPage
from filelock import Timeout, FileLock

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
        lock = FileLock('log.txt.lock', timeout=1)
        with lock:
            try:
                with open('log.txt', 'r') as file:
                    for line in file:
                        output += line + "\n" 
            except FileNotFoundError as e:
                output += "No log information yet! Please browse the website.<BR>\n"      
        output += "<HR><A HREF=\"/index\">Return to the master index</A><BR>\n"
        output += self.render_footer()
        return output
