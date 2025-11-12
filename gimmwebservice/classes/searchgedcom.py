# Class SearchGedcom
# Original Author: Michael Groat
# 6/29/2023

from .htmlpage import HTMLPage
from flask import request
import time
import datetime

class SearchGedcom(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render(self) -> str:

        def render_title() -> str:
            return "<H1>Search Database</H1>\n"
 
        def render_form() -> str:
            output = "<P><FORM METHOD=\"POST\" ACTION=\"/search\">\n"
            # output += "<INPUT TYPE=\"HIDDEN\" NAME=\"Database\" VALUE=\"$DB\">\n"
            output += "Enter word(s) to search for below with a space between each word.\n<br>"
            #  print "<FONT SIZE=+3>Search for:</FONT> "
            output += "<INPUT TYPE=\"TEXT\" NAME=\"terms\" SIZE=\"50\">\n<BR><BR>"
            output += "Choose what to search.<BR>\n"
            output += "<SELECT NAME=\"searchwhat\"><OPTION>Names<OPTION>Names or Facts<OPTION>Names or Facts or Notes\n"
            output += "</SELECT>\n<P>\n"
            output += "If searching for multiple words, use boolean: \n"
            output += "<SELECT NAME=\"boolean\"><OPTION>AND<OPTION>OR</SELECT>\n<P>\n"
            output += "The search should be case: \n"
            output += "<SELECT NAME=\"case\"><OPTION>insensitive<OPTION>sensitive"
            output += "</SELECT>\n<P>\n"
            output += "Maximum Hits: "
            output += "<SELECT NAME=\"MaxHits\"><OPTION>100<OPTION>200<OPTION>500<OPTION>1000\n";
            output += "</SELECT>\n<P>\n";
            output += "<INPUT TYPE=\"submit\" VALUE=\"Begin Search\">\n";
            output += "</FORM>\n<P>\n";
            return output

        output = self.render_header() 
        if (request.method == "GET"):  
            output += render_title()
            output += "<HR>\n"
            output += render_form()
        else:

            time_start = time.time()
            output += "<H1>Search Results</H1>\n"
            output += "<HR>\n"
            # Get form data
            terms = request.form.get("terms").replace("\\","").replace(",","").replace("/","").split()
            condition = request.form.get("boolean")
            isor = condition == "OR"
            maxmatches = int(request.form.get("MaxHits"))
            case = request.form.get("case")
            searchwhat = request.form.get("searchwhat")
            islower = case == "insensitive"
            
            # Parrot search terms
            i = 0
            findthis = ""
            output += "The genealogical database is now being search for <B>"            
            for term in terms:       
                output += term + " " 
                findthis += term + " "
                i = i + 1
                if i < len(terms):
                    findthis += condition + " "
                    output += condition + " "
            output += "</B><P>The search will be case " + case + ".\n"
            
            # Perform search and give results     
            num_matched = 0
            for indiv in self.tree.indi:
                if(self.tree.indi[indiv].search(terms, isor, islower, searchwhat)):
                    num_matched += 1
                    if (num_matched > maxmatches):
                        break
                    output += "<LI><A HREF=\"/individual/" + str(indiv) + "\">" + self.tree.indi[indiv].name.pretty_print() + \
                        "</A> " + self.tree.indi[indiv].pretty_print_birth() + " " + self.tree.indi[indiv].pretty_print_death() + "<BR>\n"         
                    
            # Wrap up search, either successful or not
            if (num_matched == 0):
                output += "<HR>Search complete. There are no matches.<P>\n";
            else:
                output += "</UL>\n";
                if ( num_matched >= maxmatches ):
                    output += "<BR>The maximum match count of " + str(maxmatches) + " was reached.<BR>\n";
                    output += "Perhaps you need to make your search more restrictive.<P>\n";
            output += "<BR><A HREF=\"/search\">Perform another search.</A><BR><P>\n";

            output += "Time took was " + str(round(time.time() - time_start, 3)) + " seconds <BR>\n" # TODO: Put in log function later
            self.log(str(datetime.datetime.now()) + " Database searched for " + findthis + \
                " accessed by " + str(request.remote_addr) + " using " + str(request.user_agent) + " in " + \
                str(round(time.time() - time_start, 7)) + " seconds.<BR>\n")

        output += "<BR><A HREF=\"/index\">Return to the master index</A><BR>\n"
        output += self.render_footer()
        return output
