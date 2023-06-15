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
      
        def render_collaspe_form() -> str:
            #if (AllowCollaspeAtGeneration):
            output = "<CENTER>"
            output += "<FORM>Collaspe or expand all branches at select generation level: "
            output += "<SELECT name=\"tblofContents\" onChange=\"javascript:formHandler(this)\">"
            output += "<OPTION>Select Depth</OPTION>"
            output += "<OPTION value=\"$MY_NAME=5\">5</OPTION>";
            output += "<OPTION value=\"$MY_NAME=10\">10</OPTION>";
            output += "<OPTION value=\"$MY_NAME=15\">15</OPTION>";
            output += "<OPTION value=\"$MY_NAME=20\">20</OPTION>";
            output += "<OPTION value=\"$MY_NAME=25\">25</OPTION>";
            output += "<OPTION value=\"$MY_NAME=30\">30</OPTION>";
            output += "<OPTION value=\"$MY_NAME=35\">35</OPTION>";
            output += "<OPTION value=\"$MY_NAME=40\">40</OPTION>";
            output += "<OPTION value=\"$MY_NAME=45\">45</OPTION>";
            output += "<OPTION value=\"$MY_NAME=50\">50</OPTION>";
            output += "<OPTION value=\"$MY_NAME=55\">55</OPTION>";
            output += "<OPTION value=\"$MY_NAME=60\">60</OPTION>";
            output += "<OPTION value=\"$MY_NAME=200\">200</OPTION>";
            output += "</SELECT></FORM>";
            output += "</CENTER>";
            return output

        def render_menu() -> str:
            output = "<CENTER><B><A HREF=\"/index\">Master Index</A>\n";
            output += " | <A HREF=\"/individual/" + str(targetid) + "\">Individual Sheet</A>\n"
            if (self.tree.indi[targetid].parents):
                output += " | <A HREF=\"/individual/" + str(targetid) + "/pedigree\">Pedigree Chart</A>\n"          
            #if ($AllowGEDDownload): #Should we allow downloads of GedCom - not necessary 100% from file to memory, so not 100% from memory across network
            #    output +=  " | <a href=\"/gedcom/\"?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n"
            output += "</B></CENTER><BR>"
            output += render_collaspe_form()
            output += "<HR>\n"
            return output

        def render_recursive(targetid, level) -> str:
            output = ""
            indent = ""
            has_appeared = targetid in appeared_in_descendency
            if not has_appeared:
                appeared_in_descendency.add(targetid)
            for _ in range(level):
                indent += "  "
            if not has_appeared:
                output += "<A NAME=\"" + str(linenumber) + "\"></A>";
                linenumberbytargetid[targetid] = linenumber
            output += indent + str(level) + " " + self.tree.indi[targetid].name.pretty_print() + "  "
            if not has_appeared:
                output += self.tree.indi[targetid].pretty_print_birth() + "  "
                output += self.tree.indi[targetid].pretty_print_death()
            else:
                previouslinenumber = linenumberbytargetid[targetid]
                output += " (individual has previously appeared, "
                output += "<A HREF=\"#" + str(previouslinenumber) + "\">click here to view)</A>"
            output += "\n"
            if has_appeared:
                return output
            for spouse in self.tree.indi[targetid].spouses:
                if spouse:
                    output += indent + " + " + self.tree.indi[spouse].name.pretty_print() + "  "
                    output += self.tree.indi[spouse].pretty_print_birth() + "  "
                    output += self.tree.indi[spouse].pretty_print_death()
                    output += "\n"
                else:
                    output += indent + "  + Unknown Spouse\n"
                for husb, wife, child in self.tree.indi[targetid].children:
                    if husb == spouse or wife == spouse:
                         output += render_recursive(child, level + 1)
            return output 

        if maxlevel is None:
            maxlevel = MAX_GENERATIONS

        output = self.render_header()
        output += "<H1>Descendents of " + self.tree.indi[targetid].name.pretty_print() + "</H1>\n"
        output += "<HR>\n"
        output += render_menu()
        appeared_in_descendency = set()
        linenumberbytargetid = dict()
        linenumber = 0
        output += "<pre>\n"
        output += render_recursive(targetid,1)
        output += "</pre>\n"
        appeared_in_descendency.clear()
        linenumberbytargetid.clear()
        output += "<HR>\n"
        output += render_menu()
        output += self.render_footer()
        return output