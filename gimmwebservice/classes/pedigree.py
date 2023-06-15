# Class Pedigree
# Original Author - Michael Groat
# 5/27/2023

from classes.htmlpage import HTMLPage

from classes.constants import (
    FACT_TYPES,
    MAX_GENERATIONS,
)

class Pedigree(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree
  
    def render(self, targetid, maxlevel = MAX_GENERATIONS) -> str:
        """print collaspable pedigree chart in html from tree objet for target individual"""
        linenumber = 0
        if maxlevel is None:
            maxlevel = MAX_GENERATIONS
            
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

        def render_menu(targetid) -> str:
            output = "<CENTER><B><A HREF=\"/index\">Master Index</A>\n";
            output += " | <A HREF=\"/individual/" + str(targetid) + "\">Individual Sheet</A>\n"
            if (self.tree.indi[targetid].children):
                output += " | <A HREF=\"/individual/" + str(targetid) + "/descendents\">Descendency Chart</A>\n"
            #if ($AllowGEDDownload): #Should we allow downloads of GedCom - not necessary 100% from file to memory, so not 100% from memory across network
            #    output +=  " | <a href=\"/gedcom/\"?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n"
            output += "</B></CENTER><BR>"
            output += render_collaspe_form()
            output += "<HR>\n"
            return output
            
        def render_script() -> str:
            
            def build_ancestors_line_number_var() -> str:
                output = ""
                output += "<script type=\"text/javascript\" language=\"JAVASCRIPT\"> \n"
                output += "  var ancestors_line_number={ "
                for key in ancestors_line_numbers:
                    if (ancestors_line_numbers[key][0] != 0 or ancestors_line_numbers[key][1] != 0):
                        output += str(key) + ": ["
                        output += str(ancestors_line_numbers[key][0]) + ", " + str(ancestors_line_numbers[key][1])
                        output += "],"
                output += "\"-1\": [-1,-1]};\n";
                return output

            output = ""
            output += build_ancestors_line_number_var()
            output += "   function formHandler(thisItem) {\n"
            output += "      var URL = '/Genealogy/igmped.cgi/n' + thisItem.options[thisItem.selectedIndex].value + '?$focus'; "
            output += "      if(URL != \"\"){ window.location.href = URL; } \n"
            output += "   }\n"
            output += "   function hidebranches(line_num, main,closeorexpand = 0) {\n"
            output += "      var x = document.getElementById(\"ButtonID\" + line_num ).innerHTML;\n"
            output += "      if (main === 1) {\n"
            output += "         if (x != \"+\") { \n"
            output += "            document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"+\";\n"
            output += "            closeorexpand = 0;\n"
            output += "            toggle(\"DivID\" + line_num + \"a\",0);\n"
            output += "            toggle(\"DivID\" + line_num + \"b\",1);\n"
            output += "            toggle(\"DivID\" + line_num + \"c\",0);\n"
            output += "            toggle(\"DivID\" + line_num + \"d\",1);\n"
            output += "            toggle(\"DivID\" + line_num + \"e\",0);\n"
            output += "            toggle(\"DivID\" + line_num + \"f\",1);\n"
            output += "         } else { \n"
            output += "            document.getElementById(\"ButtonID\" + line_num ).innerHTML = \"-\";\n"
            output += "            closeorexpand = 1;\n"
            output += "            toggle(\"DivID\" + line_num + \"a\",1);\n"
            output += "            toggle(\"DivID\" + line_num + \"b\",0);\n"
            output += "            toggle(\"DivID\" + line_num + \"c\",1);\n"
            output += "            toggle(\"DivID\" + line_num + \"d\",0);\n"
            output += "            toggle(\"DivID\" + line_num + \"e\",1);\n"
            output += "            toggle(\"DivID\" + line_num + \"f\",0);\n"
            output += "         }\n"
            output += "      }\n"
            output += "      var father_line_number = ancestors_line_number[line_num][0];\n"
            output += "      if (father_line_number > 0) {\n"
            output += "         toggle(\"DivID\" + father_line_number,closeorexpand);\n"
            output += "         if (father_line_number in ancestors_line_number) {\n"
            output += "            var y = document.getElementById(\"ButtonID\" + father_line_number ).innerHTML;\n"
            output += "            if (y != \"+\") {\n"
            output += "               hidebranches(father_line_number,0,closeorexpand);\n"
            output += "            }\n"
            output += "         }\n"
            output += "      }\n"
            output += "      var mother_line_number = ancestors_line_number[line_num][1];\n"
            output += "      if (mother_line_number > 0) {\n"
            output += "         toggle(\"DivID\" + mother_line_number,closeorexpand);\n"
            output += "         if (mother_line_number in ancestors_line_number) {\n"
            output += "            var z = document.getElementById(\"ButtonID\" + mother_line_number ).innerHTML;\n"
            output += "            if (z != \"+\") {\n"
            output += "               hidebranches(mother_line_number,0,closeorexpand);\n"
            output += "            }\n"
            output += "         }\n"
            output += "      }\n"
            output += "   }\n"
            output += "   function toggle(elementname,onoff) {\n"
            output += "      var x = document.getElementById(elementname);\n"
            output += "      if (x !== null) {\n"
            output += "        if (onoff === 0) {\n"
            output += "           x.style.display = 'none';\n"
            output += "        } else {\n";
            output += "           x.style.display = 'inline';\n"
            output += "        }\n"
            output += "      }\n"
            output += "   }\n"
            output += "</script>\n"
            return output

        def render_recursive(targetid, level, isTop, parities) -> (int, str):
            """recurse through tree, printing Individuals"""

            def render_individual(indi, level, linenumber, isTop, parities, has_appeared) -> str:

                def indent(level, parities):
                    # TODO Parity
                    tmp = "         "
                    #file.write("parities is " + str(parities) + "\n")
                    for x in range(level - 1):
                        tmp1 = 1 << x
                        tmp2 = 1 << x + 1
                        p = (~0) if (parities & tmp1) else 0
                        q = (~0) if (parities & tmp2) else 0
                        if (p ^ q):
                            tmp += '|'
                        else:
                            tmp += ' '
                        tmp += '       '
                    return tmp
                
                def build_fact_line(type, factstring) -> str:
                    output = ""
                    if (factstring is None or factstring == ""):
                        return output
                    output += tempIndentation
                    if (isTop):
                        output += "|"
                    else:
                        output += " "
                    output += "      "
                    if len(indi.parents) and list(indi.parents)[0][1] is not None: 
                        # mother is known (so we need an extra pipe)
                        output += " <div id='DivID" + str(linenumber)
                        # need a b c d e f divs because if divs all the same, collaspe only works on the first one.
                        # Could maybe use a class here - "DivClass + str(linenumber) + pipe|clear"
                        match type:
                            case "BIRT":
                                output += "a"
                            case "MARR":
                                output += "c"
                            case "DEAT":
                                output += "e"
                        output += "'>|</div><div id='DivID" + str(linenumber)
                        match type:
                            case "BIRT":
                                output += "b"
                            case "MARR":
                                output += "d"
                            case "DEAT":
                                output += "f"
                        output += "' style='display: none;'> </div>"
                        match (len(str(level + 1))):
                            case 1:
                                output += " "
                            case 2:
                                output += "  "
                            case 3:
                                output += "   "
                            case _:
                                output += "   "
                    elif len(indi.parents) and list(indi.parents)[0][0] is not None:
                        # father is known, but mother is not (hence button present but no need for extra pipe and so we need more spaces)
                        output += "    "
                    output += factstring + "\n"
                    return output

                output = ""
                if level != 0:
                    tempIndentation = indent(level, parities)
                    output += tempIndentation
                    if (isTop):
                        output += "/"
                    else:
                        output += "\\"
                else:
                    tempIndentation = " "
                    output += "  "
                output += "-- "
                
                if len(indi.parents):
                    output += "<button id=\"ButtonID" + str(linenumber) + "\" onclick=\"hidebranches(" + str(linenumber) + ",1)\">-</button> "
                output += str(level + 1) + " <A HREF=/individual/" + str(indi.num) + "><B>" + indi.name.pretty_print() + "</B></A>" # do we want self.fid instead of self.num later?
                if (has_appeared):
                    output += " <A HREF=\"#" + str(indi.num) + "\">(Person is repeated, click here)</A>"
                else:
                    output += "<A NAME=\"" + str(indi.num) + "\"></A>"
                # TODO: Do we want => in case of max level (to display) (Or do we want a drop down box to collaspe at a certain generation?)
                output += "\n"
                # print birth/marriage/death information
                if not has_appeared:
                    output += build_fact_line("BIRT", indi.pretty_print_birth())
                    if (isTop):
                        output += build_fact_line("MARR", indi.pretty_print_marriage_preferred(self.tree)) # need tree for family information
                    output += build_fact_line("DEAT", indi.pretty_print_death())            
                    output += "</div><div id='DivID" + str(linenumber + 1) + "'>"
                return output

            nonlocal linenumber
            nonlocal maxlevel
            output = ""
            if (level > maxlevel):   # TODO - use this in debugging to limit for now, still having trouble loading 45,000 people pedigrees
                return (0, "")
            if targetid not in self.tree.indi:
                return (0, "")
            has_appeared = targetid in appeared_in_pedigree
            appeared_in_pedigree.add(targetid)
            mother = None
            father = None
            fatherlinenumber = 0
            motherlinenumber = 0
            level += 1
            if self.tree.indi[targetid].parents:
                father, mother = list(self.tree.indi[targetid].parents)[0] # get perferred parents
            # recurse into father pedigree
            if father and not has_appeared:
                fatherlinenumber, fatheroutput = render_recursive(father, level, True, parities)
                output += fatheroutput
            # display individual
            linenumber = linenumber + 1
            templinenumber = linenumber
            output += render_individual(self.tree.indi[targetid], level, linenumber, isTop, parities, has_appeared)
            # recurse into mother pedigree
            if mother and not has_appeared:
                motherlinenumber, motheroutput = render_recursive(mother, level, False, parities|(1<<level))
                output += motheroutput
            ancestors_line_numbers[templinenumber] = [fatherlinenumber, motherlinenumber]
            return (templinenumber, output)
        
        output = self.render_header() # would this make more sense to call from an HTMLFactory object?
        output += render_menu(targetid)
        output += "<H1>Ancestors of " + self.tree.indi[targetid].name.pretty_print() + "</H1>\n"
        output += "<pre><div id='DivID1'>"
        appeared_in_pedigree = set()
        ancestors_line_numbers = dict()
        _, recursiveoutput = render_recursive(targetid, -1, False, 0)
        appeared_in_pedigree.clear()
        output += recursiveoutput
        output += "\n</div></pre>\n"
        output += "<HR>\n"
        output += render_menu(targetid)
        output += render_script()
        ancestors_line_numbers.clear()
        output += self.render_footer()
        return output
    
