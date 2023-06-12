# Class HTMLPage
# Original Author - Michael Groat
# 5/27/2023

class HTMLPage:

    def __init__(self):
        self.backgroundcolor = "#BFBFBD" # Should come from config file?
        self.linkcolor = "#0000EE" # Should come from config file?
        self.visitedlinkcolor = "#551A8B" # Should come from config 

    def render_header(self) -> str:
        """Prints HTML top part of page """
        # Should this go in another class like an HTMLRender class?
        title = self.tree.indi[1].name.pretty_print() + "'s Genealogical Database"
        output = "<HTML lang=\"en\">\n"
        output += "<HEAD>\n"
        output += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
        output += "<TITLE>" + title + "</TITLE>\n"
        output += "<STYLE> div { display:inline; } </STYLE\n"
        output += "</HEAD>\n"
        output += "<BODY BACKGROUND=\"/images/background\" BGCOLOR=\"" + self.backgroundcolor 
        output += "\" TEXT=\"#000000\" LINK=\"" + self.linkcolor + "\" VLINK=\"" + self.visitedlinkcolor + "\">\n"
        output += "<CENTER><H2>" + title + "</H2></CENTER>\n";
        output += "<CENTER><B>Individuals:</B> " + str(len(self.tree.indi)) + "&nbsp;&nbsp;"
        output += "<B>Families:</B> " + str(len(self.tree.fam)) + "&nbsp;&nbsp;"
        output += "<BR><B>Gedcom Last Modified:</B> " + str(self.tree.lastmodifiedtime) + "</CENTER>\n<HR>\n"
        #output += "<CENTER><B>Contact:</B> <A href=\"" + contact_email + "\">Michael M. Groat</A> &nbsp;&nbsp; "
        #output += "<B>Home Page:</B> <A href=\"" + home_page_url + "\">" + self.indi[1].name.pretty_print() + "'s Homepage</A></CENTER>"
        return output

    def render_footer(self) -> str:
        """Prints HTML bottom part of page """
        output = "<HR><EM>Please send genealogical corrections, additions, or comments to </EM>"
        if self.tree.contactemail:
           output += "<A HREF=\"mailto:" + self.tree.contactemail + "\">"
        output += self.tree.indi[1].name.pretty_print()
        if self.tree.contactemail:
            output += "</A>"
        output += "\n<HR>Created by GIMMWebService " + self.tree.gimmversion + "<BR>\n"
        output += "Copyright 2023 &copy <A HREF=\"http://github.com/mmgroat\">Michael Groat</A><BR><BR>\n"
        output += "</BODY>\n</HTML>\n"
        return output
