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
      
        def render_title() -> str:
            output = "<H1>Descendents of " + self.tree.indi[targetid].name.pretty_print() + "</H1>\n"
            return output

        def render_collaspe_form() -> str:
            #if (AllowCollaspeAtGeneration):
            output = "<CENTER>\n"
            output += "<FORM>Collaspe or expand all branches at select generation level: \n"
            output += "<SELECT name=\"tblofContents\" onChange=\"javascript:formHandler(this)\">\n"
            output += "<OPTION>Select Depth</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=5\">5</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=10\">10</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=15\">15</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=20\">20</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=25\">25</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=30\">30</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=35\">35</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=40\">40</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=45\">45</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=50\">50</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=55\">55</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=60\">60</OPTION>\n"
            output += "<OPTION value=\"$MY_NAME=200\">200</OPTION>\n"
            output += "</SELECT></FORM>\n"
            output += "</CENTER>\n"
            return output

        def render_script() -> str:
            output = "<script type=\"text/javascript\" language=\"JAVASCRIPT\"> \n"
            output += "   function hidebranches(line_num, main, closeorexpand = 0) {\n"
            output += "      var x = document.getElementById(\"ButtonID\" + line_num ).innerHTML;\n"
            output += "      if (x != \"+\") { \n"
            output += "         document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"+\";\n"
            output += "         closeorexpand = 0;\n"
            output += "      } else { \n"
            output += "         document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"-\";\n"
            output += "         closeorexpand = 1;\n"
            output += "      }\n"
            output += "      var y = document.getElementById(\"DivID\" + line_num );\n"
            output += "      var level = parseInt(y.getAttribute(\"data-level\"));\n"
            output += "      var isMarr = parseInt(y.getAttribute(\"data-marr\"));\n"
            output += "      var z;\n"
            output += "      var next_line_num = parseInt(line_num) + 1;\n"
            output += "      while ((z = document.getElementById(\"DivID\" + next_line_num)) != null) {\n"
            output += "         next_level = parseInt(z.getAttribute(\"data-level\"));\n"
            output += "         next_marr = parseInt(z.getAttribute(\"data-marr\"));\n"
            output += "         if ((next_level > level) || (isMarr == 0 && next_level == level && next_marr == \"1\")) {\n"
            output += "            toggle(z, closeorexpand);\n"
            output += "         } else {\n"
            output += "            break;\n"
            output += "         }\n"
            output += "         next_line_num = next_line_num + 1;\n"
            output += "      }\n"
            output += "   }\n"
            output += "   function toggle(element, onoff) {\n"
            output += "      if (element !== null) {\n"
            output += "        if (onoff === 0) {\n"
            output += "           element.style.display = 'none';\n"
            output += "        } else {\n";
            output += "           element.style.display = 'inline';\n"
            output += "        }\n"
            output += "      }\n"
            output += "   }\n"
            output += "</script>\n"
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

            def render_individual(targetid, indent, level) -> str:
                output = indent + str(level) + " <A HREF=\"/individual/" + str(targetid) + "\">" + \
                    self.tree.indi[targetid].name.pretty_print() + "</A>  " 
                if not has_appeared:
                    output += self.tree.indi[targetid].pretty_print_birth() + "  "
                    output += self.tree.indi[targetid].pretty_print_death()
                else:
                    previouslinenumber = linenumberbytargetid[targetid]
                    output += " (individual has previously appeared, "
                    output += "<A HREF=\"#" + str(previouslinenumber) + "\">click here to view)</A>"
                return output
     
            output = ""
            indent = ""
            has_appeared = targetid in appeared_in_descendency
            if not has_appeared:
                appeared_in_descendency.add(targetid)
            for _ in range(level):
                indent += "    "
            nonlocal linenumber
            linenumber += 1
            output += "<div id='DivID" + str(linenumber) + "' data-level='" + str(level) + \
                    "' data-marr='0'>" 
            output += "<button id=\"ButtonID" + str(linenumber) + "\" onclick=\"hidebranches(" + \
                str(linenumber) + ",1)\">-</button> "
            if not has_appeared:
                output += "<A NAME=\"" + str(linenumber) + "\"></A>";
                linenumberbytargetid[targetid] = linenumber
            output += render_individual(targetid, indent, level)            
            output += "\n</div>"
            if has_appeared:
                return output
            spouse_num = 0
            for spouse in self.tree.indi[targetid].spouses:
                spouse_num = spouse_num + 1
                linenumber = linenumber + 1
                output += "<div id='DivID" + str(linenumber) + "' data-level='" + str(level) + \
                        "' data-marr='1'>" 
                output += "<button id=\"ButtonID" + str(linenumber) + "\" onclick=\"hidebranches(" + \
                        str(linenumber) +",1)\">-</button> "
                if spouse:
                    output += indent + "  + <A HREF=\"/individual/" + str(spouse) + "\">" + \
                        self.tree.indi[spouse].name.pretty_print() + "</A>  "
                    output += self.tree.indi[spouse].pretty_print_birth() + "  "
                    output += self.tree.indi[spouse].pretty_print_death()
                else:
                    output += indent + "  + Unknown Spouse"
                output += "\n</div>"
                for husb, wife, child in self.tree.indi[targetid].children:
                    if husb == spouse or wife == spouse:
                         output += render_recursive(child, level + 1)
            return output 

        if maxlevel is None:
            maxlevel = MAX_GENERATIONS
        output = self.render_header()
        output += render_title()
        output += "<HR>\n"
        output += render_menu()
        appeared_in_descendency = set()
        linenumberbytargetid = dict()
        linenumber = 0
        output += "<pre>\n"
        output += render_recursive(targetid,1)
        output += "</pre>\n"
        linenumberbytargetid.clear()
        appeared_in_descendency.clear()
        output += render_script()
        output += "<HR>\n"
        output += render_menu()
        output += self.render_footer()
        return output