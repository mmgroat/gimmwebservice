# Class IndividualSheet
# Original Author: Michael Groat
# 5/27/2023
# testing changes

from classes.constants import (
    FACT_TYPES,
)

from classes.htmlpage import HTMLPage

class IndividualSheet(HTMLPage):

    def __init__(self, tree):
        HTMLPage.__init__(self)
        self.tree = tree

    def render(self, targetid) -> str:
        
        # rename indexed array position for shorter variable name
        targetindi = self.tree.indi[targetid]
        output = self.render_header()

        # Output Header Name
        output += "<H1>" + targetindi.name.pretty_print() + "</H1><HR>\n"
      
        output += "<ul>\n"
        
        # Output All Names: BirthNames, AKA, Nicknames (with sources) (TODO: perhaps put all sources at the bottom?)
        output += "<li><em>Preferred Name: </em> " + targetindi.name.pretty_print() + "<br>\n"
        if targetindi.name.sources:
            output += "<ul><li>Sources:<br><ul>\n"
            for source in targetindi.name.sources:
                output += "<li>" + self.tree.sources[source[0].num].pretty_print()
                if source[1]:
                    output += "Page: " + str(source[1])
            output += "</ul></ul>\n"
        if targetindi.birthnames:
            for birthname in targetindi.birthnames:
                output += "<li><em>Althernate name: </em>" + birthname.pretty_print() + "\n"

        #for name in self.tree.indi[targetid].names:


        # Output Facts
        if targetindi.gender:
            output += "<li><em>Gender:</em> " + targetindi.gender + "\n"
        if targetindi.fid:
            ouptput += "<li><em>FID (TODO Put in link to FamilySearch.org):</em> " + targetindi.fid + "\n"
        for fact in self.tree.indi[targetid].facts:
            output += fact.pretty_print() + "\n"

        # Output Notes
        for note in targetindi.notes:
            output += "<li><em>Notes:</em><blockquote>\n"
            output += note.text.replace("\n","<BR>\n") + "</blockquote>\n"
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
        output += "Len of sources is " + str(len(targetindi.sources)) + "<BR>\n"
        if targetindi.sources:
            output += "Sources:<br>\n<ol>\n"
            for source in targetindi.sources:
                output += source.pretty_print()

        # Output footer information on page
        output += "<HR>\n"
        output += self.render_menu(targetid)
        output += "</body>\n</html>\n"
        return output
    
    def render_menu(self, targetid) -> str:
        output = "<CENTER><B><A HREF=\"/index\">Master Index</A>\n";
        if (self.tree.indi[targetid].parents):
            output += " | <A HREF=\"/individual/" + str(targetid) + "/pedigree\">Pedigree Chart</A>\n"
        if (self.tree.indi[targetid].children):
            output += " | <A HREF=\"/individual/" + str(targetid) + "/descendents\">Descendency Chart</A>\n"
        #if ($AllowGEDDownload): #Should we allow downloads of GedCom - not necessary 100% from file to memory, so not 100% from memory across network
        #    output +=  " | <a href=\"/gedcom/\"?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n"
        output += "</B></CENTER><BR>"
        return output
    