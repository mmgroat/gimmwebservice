# Class IndividualSheet
# Original Author: Michael Groat
# 5/27/2023
from  ordered_set import OrderedSet
from classes.constants import (
    FACT_TYPES,
)

from classes.htmlpage import HTMLPage

class IndividualSheet(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render(self, targetid) -> str:

        # Data structures and primatives
        superscriptindex = 0
        sources = OrderedSet() # TODO we want an ordered set and we want position in the set for repeated sources

        # rename indexed array position for shorter variable name
        targetindi = self.tree.indi[targetid]

        def handle_facts(facts_name, facts) -> str:
            output = ""
            for fact in facts:
                output += handle_fact(facts_name, fact)
            return output

        def handle_fact(fact_name, fact_object) -> str: 

            def handle_sources_superscripts(inputsources) -> str:
                nonlocal superscriptindex
                output = ""
                for source in inputsources:
                    if source in sources:
                        tempindex = sources.index(source) + 1
                    else:
                        superscriptindex += 1
                        tempindex = superscriptindex
                        sources.add(source)   
                    output += "<A HREF=\"#S" + str(tempindex) + "\"><SUP>[" + str(tempindex) + "] </SUP></A>"
                return output
            
            output = ""
            if fact_name is None:
                output += fact_object.pretty_print()
            else:
                output += "<li><em>" + fact_name + " </em> " + fact_object.pretty_print()
            output += handle_sources_superscripts(fact_object.sources)
            output += "<br>\n"
            return output        
        
        def handle_notes(notes) -> str:
            output = ""
            for note in notes:
                output += "<li><em>Notes:</em><blockquote>\n"
                output += note.text.replace("\n","<BR>\n") + "</blockquote>\n"
            return output

        def handle_sources() -> str:    
            output = ""
            if sources:
                output += "<em>Sources:</em><br><ol>\n"
                for index, source in enumerate(sources):
                    output += "<A NAME=\"S" + str(index+1) + "\"></NAME><li>" + source[0].pretty_print()
                    if source[1]:
                        output += "Page: " + str(source[1]) + "<br>"
                    output += "\n"
                output += "</ol>\n"
            return output

        def render_menu() -> str:
            output = "<CENTER><B><A HREF=\"/index\">Master Index</A>\n";
            if (self.tree.indi[targetid].parents):
                output += " | <A HREF=\"/individual/" + str(targetid) + "/pedigree\">Pedigree Chart</A>\n"
            if (self.tree.indi[targetid].children):
                output += " | <A HREF=\"/individual/" + str(targetid) + "/descendents\">Descendency Chart</A>\n"
            #if ($AllowGEDDownload): #Should we allow downloads of GedCom - not necessary 100% from file to memory, so not 100% from memory across network
            #    output +=  " | <a href=\"/gedcom/\"?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n"
            output += "</B></CENTER><BR>"
            return output

        output = self.render_header()

        # Output Header Name
        output += "<H1>" + targetindi.name.pretty_print() + "</H1><HR>\n"
      
        # Output All Names: BirthNames, AKA, Nicknames (with sources) (TODO: perhaps put all sources at the bottom?)
        output += "<ul>\n"
        output += handle_fact("Preferred Name: ", targetindi.name)
        output += handle_facts("Alternate Name: ", targetindi.birthnames)
        output += handle_facts("Nickname: ", targetindi.nicknames)
        output += handle_facts("Also Known As: ", targetindi.aka)
        output += handle_facts("Married Name: ", targetindi.married)
       
        # Output Facts
        if targetindi.gender:
            output += "<li><em>Gender: </em> " + targetindi.gender + "<br>\n"
        if targetindi.fid:
            output += "<li><em>FID: </em> " + targetindi.fid + "<br>\n"
        output += handle_facts(None, targetindi.facts)

        # Output Notes
        output += handle_notes(targetindi.notes)
     
        output += "</ul><br>\n"

        # Output Parents
        parentstouched = False
        if targetindi.parents:
           for parents in targetindi.parents:
                if not parentstouched:
                    output += "<em>Preferred Parents:</em><br>\n"
                else:
                    output += "<em>Alternate Parents:</em><br>\n"
                parentstouched = True
                for i, parent in enumerate(parents):                                
                    if parent:
                        birthline = self.tree.indi[parent].pretty_print_birth()
                        deathline = self.tree.indi[parent].pretty_print_death()                    
                        output += "<em>"
                        if (i == 0):
                            output += "Father: "
                        else:
                            output += "Mother: "
                        output += "</em><A HREF=/individual/"+ str(self.tree.indi[parent].num) + ">" 
                        output += self.tree.indi[parent].name.pretty_print() + "</A>, " 
                        output += birthline + " &nbsp;&nbsp;" + deathline + "<br>\n"
        
        output += "<BR>\n"

        # Output Families
        for i, spouseid in enumerate(targetindi.spouses):

            if spouseid in self.tree.indi:
                spouseindi = self.tree.indi[spouseid]

                # BUG? Note, may have found a bug in getmyancestors parsing GEDCOM - what if multiple spouses that are unknown. Do 
                # children get added to the same family that is indexed by (spouse_id, None)?
                output += "<em>Family " + str(i + 1) + ":</em> <A HREF=/individuals/" + str(spouseid) + ">" + spouseindi.name.pretty_print() + "</A>," 
                output += spouseindi.pretty_print_birth() + " &nbsp;&nbsp;" + spouseindi.pretty_print_death() + "<ul>\n"
                # output marriage information:
                marriage_info_set = targetindi.pretty_print_all_marriage_facts_by_spouseid(spouseid, self.tree) 
                if len(marriage_info_set):
                    for marriage_info in marriage_info_set:
                        output += "<li><em>Married:</em> " + marriage_info + "\n"
                    output += "</ul>\n<ol>\n"
                
                #Output Children:
                children_set_by_spouse_id = targetindi.get_children_set_by_spouse_id(spouseid)
                if len(children_set_by_spouse_id):
                    for childid in children_set_by_spouse_id:
                        if childid in self.tree.indi:
                            childindi = self.tree.indi[childid]
                            output += "<li><A HREF=/individual/" + str(childid) + ">" + childindi.name.pretty_print() + "</A>, " + childindi.pretty_print_birth()
                            output += " &nbsp; &nbsp; " + childindi.pretty_print_death() + "\n"
                    output += "\n</ol><br>"    

        # Output Sources
        output += handle_sources()

        # Output footer information on page
        output += "<HR>\n"
        output += render_menu()
        output += self.render_footer()
        return output
    
 
    
