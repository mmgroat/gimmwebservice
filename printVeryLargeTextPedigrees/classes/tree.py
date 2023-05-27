import sys
import re
import time
import asyncio
from urllib.parse import unquote

# global imports
import babelfish

# local imports
#import printverylargetextpedigrees
from classes.constants import (
    MAX_PERSONS,
    FACT_EVEN,
    FACT_TAGS,
    FACT_TYPES,
    ORDINANCES_STATUS,
)

# getmyancestors classes and functions
def cont(string):
    """parse a GEDCOM line adding CONT and CONT tags if necessary"""
    level = int(string[:1]) + 1
    lines = string.splitlines()
    res = list()
    max_len = 255
    for line in lines:
        c_line = line
        to_conc = list()
        while len(c_line.encode("utf-8")) > max_len:
            index = min(max_len, len(c_line) - 2)
            while (
                len(c_line[:index].encode("utf-8")) > max_len
                or re.search(r"[ \t\v]", c_line[index - 1 : index + 1])
            ) and index > 1:
                index -= 1
            to_conc.append(c_line[:index])
            c_line = c_line[index:]
            max_len = 248
        to_conc.append(c_line)
        res.append(("\n%s CONC " % level).join(to_conc))
        max_len = 248
    return ("\n%s CONT " % level).join(res) + "\n"


class Note:
    """GEDCOM Note class
    :param text: the Note content
    :param tree: a Tree object
    :param num: the GEDCOM identifier
    """

    counter = 0

    def __init__(self, text="", tree=None, num=None):
        if num:
            self.num = num
        else:
            Note.counter += 1
            self.num = Note.counter
        self.text = text.strip()

        if tree:
            tree.notes.append(self)

    def print(self, file=sys.stdout):
        """print Note in GEDCOM format"""
        file.write(cont("0 @N%s@ NOTE %s" % (self.num, self.text)))

    def link(self, file=sys.stdout, level=1):
        """print the reference in GEDCOM format"""
        file.write("%s NOTE @N%s@\n" % (level, self.num))


class Source:
    """GEDCOM Source class
    :param data: FS Source data
    :param tree: a Tree object
    :param num: the GEDCOM identifier
    """

    counter = 0

    def __init__(self, data=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Source.counter += 1
            self.num = Source.counter

        self.tree = tree
        self.url = self.citation = self.title = self.fid = None
        self.notes = set()
        if data:
            self.fid = data["id"]
            if "about" in data:
                self.url = data["about"].replace(
                    "familysearch.org/platform/memories/memories",
                    "www.familysearch.org/photos/artifacts",
                )
            if "citations" in data:
                self.citation = data["citations"][0]["value"]
            if "titles" in data:
                self.title = data["titles"][0]["value"]
            if "notes" in data:
                for n in data["notes"]:
                    if n["text"]:
                        self.notes.add(Note(n["text"], self.tree))

    def print(self, file=sys.stdout):
        """print Source in GEDCOM format"""
        file.write("0 @S%s@ SOUR \n" % self.num)
        if self.title:
            file.write(cont("1 TITL " + self.title))
        if self.citation:
            file.write(cont("1 AUTH " + self.citation))
        if self.url:
            file.write(cont("1 PUBL " + self.url))
        for n in self.notes:
            n.link(file, 1)
        file.write("1 REFN %s\n" % self.fid)

    def link(self, file=sys.stdout, level=1):
        """print the reference in GEDCOM format"""
        file.write("%s SOUR @S%s@\n" % (level, self.num))


class Fact:
    """GEDCOM Fact class
    :param data: FS Fact data
    :param tree: a tree object
    """

    def __init__(self, data=None, tree=None):
        self.value = self.type = self.date = self.place = self.note = self.map = None
        if data:
            if "value" in data:
                self.value = data["value"]
            if "type" in data:
                self.type = data["type"]
                if self.type in FACT_EVEN:
                    self.type = tree.fs._(FACT_EVEN[self.type])
                elif self.type[:6] == "data:,":
                    self.type = unquote(self.type[6:])
                elif self.type not in FACT_TAGS:
                    self.type = None
            if "date" in data:
                self.date = data["date"]["original"]
            if "place" in data:
                place = data["place"]
                self.place = place["original"]
                if "description" in place and place["description"][1:] in tree.places:
                    self.map = tree.places[place["description"][1:]]
            if "changeMessage" in data["attribution"]:
                self.note = Note(data["attribution"]["changeMessage"], tree)
            if self.type == "http://gedcomx.org/Death" and not (
                self.date or self.place
            ):
                self.value = "Y"

    def print(self, file=sys.stdout):
        """print Fact in GEDCOM format
        the GEDCOM TAG depends on the type, defined in FACT_TAGS
        """
        if self.type in FACT_TAGS:
            tmp = "1 " + FACT_TAGS[self.type]
            if self.value:
                tmp += " " + self.value
            file.write(cont(tmp))
        elif self.type:
            file.write("1 EVEN\n2 TYPE %s\n" % self.type)
            if self.value:
                file.write(cont("2 NOTE Description: " + self.value))
        else:
            return
        if self.date:
            file.write(cont("2 DATE " + self.date))
        if self.place:
            file.write(cont("2 PLAC " + self.place))
        if self.map:
            latitude, longitude = self.map
            file.write("3 MAP\n4 LATI %s\n4 LONG %s\n" % (latitude, longitude))
        if self.note:
            self.note.link(file, 2)


class Memorie:
    """GEDCOM Memorie class
    :param data: FS Memorie data
    """

    def __init__(self, data=None):
        self.description = self.url = None
        if data and "links" in data:
            self.url = data["about"]
            if "titles" in data:
                self.description = data["titles"][0]["value"]
            if "descriptions" in data:
                self.description = (
                    "" if not self.description else self.description + "\n"
                ) + data["descriptions"][0]["value"]

    def print(self, file=sys.stdout):
        """print Memorie in GEDCOM format"""
        file.write("1 OBJE\n2 FORM URL\n")
        if self.description:
            file.write(cont("2 TITL " + self.description))
        if self.url:
            file.write(cont("2 FILE " + self.url))


class Name:
    """GEDCOM Name class
    :param data: FS Name data
    :param tree: a Tree object
    """

    def __init__(self, data=None, tree=None):
        self.given = ""
        self.surname = ""
        self.prefix = None
        self.suffix = None
        self.note = None
        if data:
            if "parts" in data["nameForms"][0]:
                for z in data["nameForms"][0]["parts"]:
                    if z["type"] == "http://gedcomx.org/Given":
                        self.given = z["value"]
                    if z["type"] == "http://gedcomx.org/Surname":
                        self.surname = z["value"]
                    if z["type"] == "http://gedcomx.org/Prefix":
                        self.prefix = z["value"]
                    if z["type"] == "http://gedcomx.org/Suffix":
                        self.suffix = z["value"]
            if "changeMessage" in data["attribution"]:
                self.note = Note(data["attribution"]["changeMessage"], tree)

    def print(self, file=sys.stdout, typ=None):
        """print Name in GEDCOM format
        :param typ: type for additional names
        """
        tmp = "1 NAME %s /%s/" % (self.given, self.surname)
        if self.suffix:
            tmp += " " + self.suffix
        file.write(cont(tmp))
        if typ:
            file.write("2 TYPE %s\n" % typ)
        if self.prefix:
            file.write("2 NPFX %s\n" % self.prefix)
        if self.note:
            self.note.link(file, 2)

    def pretty_print(self) -> str:
        """print a presentation ready name
        :param typ: type for additional names
        """
        tmp = self.surname.strip()
        if self.given:
            tmp = self.given.strip() + " " + tmp
        if self.suffix:
            tmp += " " + self.suffix.strip()
        if self.prefix:
            tmp = self.prefix.strip() + " " + tmp
        return tmp


class Ordinance:
    """GEDCOM Ordinance class
    :param data: FS Ordinance data
    """

    def __init__(self, data=None):
        self.date = self.temple_code = self.status = self.famc = None
        if data:
            if "completedDate" in data:
                self.date = data["completedDate"]
            if "completedTemple" in data:
                self.temple_code = data["completedTemple"]["code"]
            self.status = data["status"]

    def print(self, file=sys.stdout):
        """print Ordinance in Gecom format"""
        if self.date:
            file.write(cont("2 DATE " + self.date))
        if self.temple_code:
            file.write("2 TEMP %s\n" % self.temple_code)
        if self.status in ORDINANCES_STATUS:
            file.write("2 STAT %s\n" % ORDINANCES_STATUS[self.status])
        if self.famc:
            file.write("2 FAMC @F%s@\n" % self.famc.num)


class Indi:
    """GEDCOM individual class
    :param fid' FamilySearch id
    :param tree: a tree object
    :param num: the GEDCOM identifier
    """

    counter = 0

    def __init__(self, fid=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Indi.counter += 1
            self.num = Indi.counter
        self.fid = fid
        self.tree = tree
        self.famc_fid = set()
        self.fams_fid = set()
        self.famc_num = set()
        self.fams_num = set()
        self.fams_num_spouses_num = set()
        self.name = None
        self.gender = None
        self.living = None
        self.parents = set()
        self.spouses = set()
        self.children = set()
        self.baptism = self.confirmation = self.initiatory = None
        self.endowment = self.sealing_child = None
        self.nicknames = set()
        self.facts = set()
        self.birthnames = set()
        self.married = set()
        self.aka = set()
        self.notes = set()
        self.sources = set()
        self.memories = set()

    def add_data(self, data):
        """add FS individual data"""
        if data:
            self.living = data["living"]
            for x in data["names"]:
                if x["preferred"]:
                    self.name = Name(x, self.tree)
                else:
                    if x["type"] == "http://gedcomx.org/Nickname":
                        self.nicknames.add(Name(x, self.tree))
                    if x["type"] == "http://gedcomx.org/BirthName":
                        self.birthnames.add(Name(x, self.tree))
                    if x["type"] == "http://gedcomx.org/AlsoKnownAs":
                        self.aka.add(Name(x, self.tree))
                    if x["type"] == "http://gedcomx.org/MarriedName":
                        self.married.add(Name(x, self.tree))
            if "gender" in data:
                if data["gender"]["type"] == "http://gedcomx.org/Male":
                    self.gender = "M"
                elif data["gender"]["type"] == "http://gedcomx.org/Female":
                    self.gender = "F"
                elif data["gender"]["type"] == "http://gedcomx.org/Unknown":
                    self.gender = "U"
            if "facts" in data:
                for x in data["facts"]:
                    if x["type"] == "http://familysearch.org/v1/LifeSketch":
                        self.notes.add(
                            Note(
                                "=== %s ===\n%s"
                                % (self.tree.fs._("Life Sketch"), x.get("value", "")),
                                self.tree,
                            )
                        )
                    else:
                        self.facts.add(Fact(x, self.tree))
            if "sources" in data:
                sources = self.tree.fs.get_url(
                    "/platform/tree/persons/%s/sources" % self.fid
                )
                if sources:
                    quotes = dict()
                    for quote in sources["persons"][0]["sources"]:
                        quotes[quote["descriptionId"]] = (
                            quote["attribution"]["changeMessage"]
                            if "changeMessage" in quote["attribution"]
                            else None
                        )
                    for source in sources["sourceDescriptions"]:
                        if source["id"] not in self.tree.sources:
                            self.tree.sources[source["id"]] = Source(source, self.tree)
                        self.sources.add(
                            (self.tree.sources[source["id"]], quotes[source["id"]])
                        )
            if "evidence" in data:
                url = "/platform/tree/persons/%s/memories" % self.fid
                memorie = self.tree.fs.get_url(url)
                if memorie and "sourceDescriptions" in memorie:
                    for x in memorie["sourceDescriptions"]:
                        if x["mediaType"] == "text/plain":
                            text = "\n".join(
                                val.get("value", "")
                                for val in x.get("titles", [])
                                + x.get("descriptions", [])
                            )
                            self.notes.add(Note(text, self.tree))
                        else:
                            self.memories.add(Memorie(x))

    def add_fams(self, fams):
        """add family fid (for spouse or parent)"""
        self.fams_fid.add(fams)

    def add_famc(self, famc):
        """add family fid (for child)"""
        self.famc_fid.add(famc)

    def get_notes(self):
        """retrieve individual notes"""
        notes = self.tree.fs.get_url("/platform/tree/persons/%s/notes" % self.fid)
        if notes:
            for n in notes["persons"][0]["notes"]:
                text_note = "=== %s ===\n" % n["subject"] if "subject" in n else ""
                text_note += n["text"] + "\n" if "text" in n else ""
                self.notes.add(Note(text_note, self.tree))

    def get_ordinances(self):
        """retrieve LDS ordinances
        need a LDS account
        """
        res = []
        famc = False
        if self.living:
            return res, famc
        url = "/service/tree/tree-data/reservations/person/%s/ordinances" % self.fid
        data = self.tree.fs.get_url(url, {})
        if data:
            for key, o in data["data"].items():
                if key == "baptism":
                    self.baptism = Ordinance(o)
                elif key == "confirmation":
                    self.confirmation = Ordinance(o)
                elif key == "initiatory":
                    self.initiatory = Ordinance(o)
                elif key == "endowment":
                    self.endowment = Ordinance(o)
                elif key == "sealingsToParents":
                    for subo in o:
                        self.sealing_child = Ordinance(subo)
                        relationships = subo.get("relationships", {})
                        father = relationships.get("parent1Id")
                        mother = relationships.get("parent2Id")
                        if father and mother:
                            famc = father, mother
                elif key == "sealingsToSpouses":
                    res += o
        return res, famc

    def get_contributors(self):
        """retrieve contributors"""
        temp = set()
        url = "/platform/tree/persons/%s/changes" % self.fid
        data = self.tree.fs.get_url(url, {"Accept": "application/x-gedcomx-atom+json"})
        if data:
            for entries in data["entries"]:
                for contributors in entries["contributors"]:
                    temp.add(contributors["name"])
        if temp:
            text = "=== %s ===\n%s" % (
                self.tree.fs._("Contributors"),
                "\n".join(sorted(temp)),
            )
            for n in self.tree.notes:
                if n.text == text:
                    self.notes.add(n)
                    return
            self.notes.add(Note(text, self.tree))

    def print(self, file=sys.stdout):
        """print individual in GEDCOM format"""
        file.write("0 @I%s@ INDI\n" % self.num)
        if self.name:
            self.name.print(file)
        for o in self.nicknames:
            file.write(cont("2 NICK %s %s" % (o.given, o.surname)))
        for o in self.birthnames:
            o.print(file)
        for o in self.aka:
            o.print(file, "aka")
        for o in self.married:
            o.print(file, "married")
        if self.gender:
            file.write("1 SEX %s\n" % self.gender)
        for o in self.facts:
            o.print(file)
        for o in self.memories:
            o.print(file)
        if self.baptism:
            file.write("1 BAPL\n")
            self.baptism.print(file)
        if self.confirmation:
            file.write("1 CONL\n")
            self.confirmation.print(file)
        if self.initiatory:
            file.write("1 WAC\n")
            self.initiatory.print(file)
        if self.endowment:
            file.write("1 ENDL\n")
            self.endowment.print(file)
        if self.sealing_child:
            file.write("1 SLGC\n")
            self.sealing_child.print(file)
        for num in self.fams_num:
            file.write("1 FAMS @F%s@\n" % num)
        for num in self.famc_num:
            file.write("1 FAMC @F%s@\n" % num)
        file.write("1 _FSFTID %s\n" % self.fid)
        for o in self.notes:
            o.link(file)
        for source, quote in self.sources:
            source.link(file, 1)
            if quote:
                file.write(cont("2 PAGE " + quote))

    def print_pedigree(self, file, level, linenumber, topOrBottom, parities, has_appeared):
        #file.write(str(linenumber))
        if level != 0:
            file.write(self.pedigree_indent(file, level, parities))
            if (topOrBottom == 1):
                file.write("/")
            else:
                file.write("\\")
            file.write("------")
            file.write(" " + str(level + 1) + " ")
        else:
            file.write("  -- " + str(level + 1) + " ")
        file.write(self.name.pretty_print())
        if (has_appeared):
            file.write(" (Individual has previously appeared)")
        file.write("\n")

    def print_pedigree_html(self, level, linenumber, isTop, parities, has_appeared, family) -> str:
        def build_fact_line(type, date, place) -> str:
            output = ""
            if (date is None and place is None):
                return output
            #if (level > 1):
            #    output += "     "
            output += tempIndentation
            if (isTop):
                output += "|"
            else:
                output += " "
                
            output += "      "
            if len(self.parents) and list(self.parents)[0][1] is not None: 
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
            elif len(self.parents) and list(self.parents)[0][0] is not None:
                # father is known, but mother is not (hence button present but no need for extra pipe and so we need more spaces)
                output += "    "
            match type:
                case "BIRT":
                    output += "<B>b.</B> "
                case "MARR":
                    output += "<B>m.</B> "
                case "DEAT":
                    output += "<B>d.</B> "
            if date is not None:
                output += str(date) + " "
            if place is not None:
                output += "in " + str(place)
            output += "\n"
            return output

        output = ""
        if level != 0:
            tempIndentation = self.pedigree_indent(level, parities)
            output += tempIndentation
            if (isTop):
                output += "/"
            else:
                output += "\\"
        else:
            tempIndentation = " "
            output += "  "
        output += "-- "
        
        if len(self.parents):
            output += "<button id=\"ButtonID" + str(linenumber) + "\" onclick=\"hidebranches(" + str(linenumber) + ",1)\">-</button> "
        output += str(level + 1) + " <A HREF=/individual/" + str(self.num) + "><B>" + self.name.pretty_print() + "</B></A>" # do we want self.fid instead of self.num later?
        if (has_appeared):
            output += " <A HREF=\"#" + str(self.num) + "\">(Person is repeated, click here)</A>"
        else:
            output += "<A NAME=\"" + str(self.num) + "\"></A>"
        # TODO: Do we want => in case of max level (to display) (Or do we want a drop down box to collaspe at a certain generation?)
        output += "\n"
        # print birth/marriage/death information
        if not has_appeared:
            birthline = ""
            marriageline = ""
            deathline = ""
            birthtouched = False
            marriagetouched = False
            deathtouched = False
            for fact in self.facts:
                #sys.stderr.write("Fact is " + str(fact.type) + "\n")
                # GET BIRTH
                if fact.type == FACT_TYPES["BIRT"]:
                    if (not birthtouched):
                        birthtouched = True
                        birthline = build_fact_line("BIRT", fact.date, fact.place)
                # GET DEATH
                if fact.type == FACT_TYPES["DEAT"]:
                    if (not deathtouched):
                        deathtouched = True
                        deathline = build_fact_line("DEAT", fact.date, fact.place)
            #GET MARRIAGE
            if (isTop):
                if len(self.fams_num): # Has a spouse -- error if we don't
                    spouse = list(self.fams_num)[0]
                    # if isTop spouse is always female (but not safe to assume these days, will have to change)
                    # Need the tree object below (Is there a way to pass this call it cleanly???
                    if family:
                        for fact in family.facts:
                            if fact.type == FACT_TYPES["MARR"]:
                                if (not marriagetouched):
                                    marriagetouched = True
                                    marriageline = build_fact_line("MARR", fact.date, fact.place)
            output += birthline
            output += marriageline
            output += deathline
            output += "</div><div id='DivID" + str(linenumber + 1) + "'>"
        return output

    def pedigree_indent(self, level, parities):
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

class Fam:
    """GEDCOM family class
    :param husb: husbant fid
    :param wife: wife fid
    :param tree: a Tree object
    :param num: a GEDCOM identifier
    """

    counter = 0

    def __init__(self, husb=None, wife=None, tree=None, num=None):
        if num:
            self.num = num
        else:
            Fam.counter += 1
            self.num = Fam.counter
        self.husb_fid = husb if husb else None
        self.wife_fid = wife if wife else None
        self.tree = tree
        self.husb_num = self.wife_num = self.fid = None
        self.facts = set()
        self.sealing_spouse = None
        self.chil_fid = set()
        self.chil_num = set()
        self.notes = set()
        self.sources = set()

    def add_child(self, child):
        """add a child fid to the family"""
        if child not in self.chil_fid:
            self.chil_fid.add(child)

    def add_marriage(self, fid):
        """retrieve and add marriage information
        :param fid: the marriage fid
        """
        if not self.fid:
            self.fid = fid
            url = "/platform/tree/couple-relationships/%s" % self.fid
            data = self.tree.fs.get_url(url)
            if data:
                if "facts" in data["relationships"][0]:
                    for x in data["relationships"][0]["facts"]:
                        self.facts.add(Fact(x, self.tree))
                if "sources" in data["relationships"][0]:
                    quotes = dict()
                    for x in data["relationships"][0]["sources"]:
                        quotes[x["descriptionId"]] = (
                            x["attribution"]["changeMessage"]
                            if "changeMessage" in x["attribution"]
                            else None
                        )
                    new_sources = quotes.keys() - self.tree.sources.keys()
                    if new_sources:
                        sources = self.tree.fs.get_url(
                            "/platform/tree/couple-relationships/%s/sources" % self.fid
                        )
                        for source in sources["sourceDescriptions"]:
                            if (
                                source["id"] in new_sources
                                and source["id"] not in self.tree.sources
                            ):
                                self.tree.sources[source["id"]] = Source(
                                    source, self.tree
                                )
                    for source_fid in quotes:
                        self.sources.add(
                            (self.tree.sources[source_fid], quotes[source_fid])
                        )

    def get_notes(self):
        """retrieve marriage notes"""
        if self.fid:
            notes = self.tree.fs.get_url(
                "/platform/tree/couple-relationships/%s/notes" % self.fid
            )
            if notes:
                for n in notes["relationships"][0]["notes"]:
                    text_note = "=== %s ===\n" % n["subject"] if "subject" in n else ""
                    text_note += n["text"] + "\n" if "text" in n else ""
                    self.notes.add(Note(text_note, self.tree))

    def get_contributors(self):
        """retrieve contributors"""
        if self.fid:
            temp = set()
            url = "/platform/tree/couple-relationships/%s/changes" % self.fid
            data = self.tree.fs.get_url(
                url, {"Accept": "application/x-gedcomx-atom+json"}
            )
            if data:
                for entries in data["entries"]:
                    for contributors in entries["contributors"]:
                        temp.add(contributors["name"])
            if temp:
                text = "=== %s ===\n%s" % (
                    self.tree.fs._("Contributors"),
                    "\n".join(sorted(temp)),
                )
                for n in self.tree.notes:
                    if n.text == text:
                        self.notes.add(n)
                        return
                self.notes.add(Note(text, self.tree))

    def print(self, file=sys.stdout):
        """print family information in GEDCOM format"""
        file.write("0 @F%s@ FAM\n" % self.num)
        if self.husb_num:
            file.write("1 HUSB @I%s@\n" % self.husb_num)
        if self.wife_num:
            file.write("1 WIFE @I%s@\n" % self.wife_num)
        for num in self.chil_num:
            file.write("1 CHIL @I%s@\n" % num)
        for o in self.facts:
            o.print(file)
        if self.sealing_spouse:
            file.write("1 SLGS\n")
            self.sealing_spouse.print(file)
        if self.fid:
            file.write("1 _FSFTID %s\n" % self.fid)
        for o in self.notes:
            o.link(file)
        for source, quote in self.sources:
            source.link(file, 1)
            if quote:
                file.write(cont("2 PAGE " + quote))


class Tree:
    """family tree class
    :param fs: a Session object
    """

    def __init__(self, fs=None):
        self.fs = fs
        self.indi = dict()
        self.fam = dict()
        self.notes = list()
        self.sources = dict()
        self.places = dict()
        self.display_name = self.lang = None
        self.backgroundcolor = "#BFBFBD" # Should go in HTML Render class?
        self.linkcolor = "#0000EE" # Should go in HTML Render class?
        self.visitedlinkcolor = "#551A8B" # Should go in HTML Render class?
        self.lastmodifiedtime = None
        if fs:
            self.display_name = fs.display_name
            self.lang = babelfish.Language.fromalpha2(fs.lang).name

    def add_indis(self, fids):
        """add individuals to the family tree
        :param fids: an iterable of fid
        """

        async def add_datas(loop, data):
            futures = set()
            for person in data["persons"]:
                self.indi[person["id"]] = Indi(person["id"], self)
                futures.add(
                    loop.run_in_executor(None, self.indi[person["id"]].add_data, person)
                )
            for future in futures:
                await future

        new_fids = [fid for fid in fids if fid and fid not in self.indi]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while new_fids:
            data = self.fs.get_url(
                "/platform/tree/persons?pids=" + ",".join(new_fids[:MAX_PERSONS])
            )
            if data:
                if "places" in data:
                    for place in data["places"]:
                        if place["id"] not in self.places:
                            self.places[place["id"]] = (
                                str(place["latitude"]),
                                str(place["longitude"]),
                            )
                loop.run_until_complete(add_datas(loop, data))
                if "childAndParentsRelationships" in data:
                    for rel in data["childAndParentsRelationships"]:
                        father = (
                            rel["parent1"]["resourceId"] if "parent1" in rel else None
                        )
                        mother = (
                            rel["parent2"]["resourceId"] if "parent2" in rel else None
                        )
                        child = rel["child"]["resourceId"] if "child" in rel else None
                        if child in self.indi:
                            self.indi[child].parents.add((father, mother))
                        if father in self.indi:
                            self.indi[father].children.add((father, mother, child))
                        if mother in self.indi:
                            self.indi[mother].children.add((father, mother, child))
                if "relationships" in data:
                    for rel in data["relationships"]:
                        if rel["type"] == "http://gedcomx.org/Couple":
                            person1 = rel["person1"]["resourceId"]
                            person2 = rel["person2"]["resourceId"]
                            relfid = rel["id"]
                            if person1 in self.indi:
                                self.indi[person1].spouses.add(
                                    (person1, person2, relfid)
                                )
                            if person2 in self.indi:
                                self.indi[person2].spouses.add(
                                    (person1, person2, relfid)
                                )
            new_fids = new_fids[MAX_PERSONS:]

    def add_fam(self, father, mother):
        """add a family to the family tree
        :param father: the father fid or None
        :param mother: the mother fid or None
        """
        if (father, mother) not in self.fam:
            self.fam[(father, mother)] = Fam(father, mother, self)

    def add_trio(self, father, mother, child):
        """add a children relationship to the family tree
        :param father: the father fid or None
        :param mother: the mother fid or None
        :param child: the child fid or None
        """
        if father in self.indi:
            self.indi[father].add_fams((father, mother))
        if mother in self.indi:
            self.indi[mother].add_fams((father, mother))
        if child in self.indi and (father in self.indi or mother in self.indi):
            self.indi[child].add_famc((father, mother))
            self.add_fam(father, mother)
            self.fam[(father, mother)].add_child(child)

    def add_parents(self, fids):
        """add parents relationships
        :param fids: a set of fids
        """
        parents = set()
        for fid in fids & self.indi.keys():
            for couple in self.indi[fid].parents:
                parents |= set(couple)
        if parents:
            self.add_indis(parents)
        for fid in fids & self.indi.keys():
            for father, mother in self.indi[fid].parents:
                if (
                    mother in self.indi
                    and father in self.indi
                    or not father
                    and mother in self.indi
                    or not mother
                    and father in self.indi
                ):
                    self.add_trio(father, mother, fid)
        return set(filter(None, parents))

    def add_spouses(self, fids):
        """add spouse relationships
        :param fids: a set of fid
        """

        async def add(loop, rels):
            futures = set()
            for father, mother, relfid in rels:
                if (father, mother) in self.fam:
                    futures.add(
                        loop.run_in_executor(
                            None, self.fam[(father, mother)].add_marriage, relfid
                        )
                    )
            for future in futures:
                await future

        rels = set()
        for fid in fids & self.indi.keys():
            rels |= self.indi[fid].spouses
        loop = asyncio.get_event_loop()
        if rels:
            self.add_indis(
                set.union(*({father, mother} for father, mother, relfid in rels))
            )
            for father, mother, _ in rels:
                if father in self.indi and mother in self.indi:
                    self.indi[father].add_fams((father, mother))
                    self.indi[mother].add_fams((father, mother))
                    self.add_fam(father, mother)
            loop.run_until_complete(add(loop, rels))

    def add_children(self, fids):
        """add children relationships
        :param fids: a set of fid
        """
        rels = set()
        for fid in fids & self.indi.keys():
            rels |= self.indi[fid].children if fid in self.indi else set()
        children = set()
        if rels:
            self.add_indis(set.union(*(set(rel) for rel in rels)))
            for father, mother, child in rels:
                if child in self.indi and (
                    mother in self.indi
                    and father in self.indi
                    or not father
                    and mother in self.indi
                    or not mother
                    and father in self.indi
                ):
                    self.add_trio(father, mother, child)
                    children.add(child)
        return children

    def add_ordinances(self, fid):
        """retrieve ordinances
        :param fid: an individual fid
        """
        if fid in self.indi:
            ret, famc = self.indi[fid].get_ordinances()
            if famc and famc in self.fam:
                self.indi[fid].sealing_child.famc = self.fam[famc]
            for o in ret:
                spouse_id = o["relationships"]["spouseId"]
                if (fid, spouse_id) in self.fam:
                    self.fam[fid, spouse_id].sealing_spouse = Ordinance(o)
                elif (spouse_id, fid) in self.fam:
                    self.fam[spouse_id, fid].sealing_spouse = Ordinance(o)

    def reset_num(self):
        """reset all GEDCOM identifiers"""
        for husb, wife in self.fam:
            self.fam[(husb, wife)].husb_num = self.indi[husb].num if husb else None
            self.fam[(husb, wife)].wife_num = self.indi[wife].num if wife else None
            self.fam[(husb, wife)].chil_num = set(
                self.indi[chil].num for chil in self.fam[(husb, wife)].chil_fid
            )
        for fid in self.indi:
            self.indi[fid].famc_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[fid].famc_fid
            )
            self.indi[fid].fams_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[fid].fams_fid
            )

    def reset_num_no_fid(self):
        """reset all GEDCOM identifiers"""
        for husb, wife in self.fam:
            self.fam[(husb, wife)].husb_num = self.indi[husb].num if husb else None
            self.fam[(husb, wife)].wife_num = self.indi[wife].num if wife else None
            self.fam[(husb, wife)].chil_num = set(
                self.indi[chil].num for chil in self.fam[(husb, wife)].chil_num
            )
        for num in self.indi:
            self.indi[num].famc_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[num].famc_num
            )
            self.indi[num].fams_num = set(
                self.fam[(husb, wife)].num for husb, wife in self.indi[num].fams_num
            )

    def print(self, file):
        """print family tree in GEDCOM format"""
        file.write("0 HEAD\n")
        file.write("1 CHAR UTF-8\n")
        file.write("1 GEDC\n")
        file.write("2 VERS 5.1.1\n")
        file.write("2 FORM LINEAGE-LINKED\n")
        file.write("1 SOUR printverylargetextpedigrees\n")
        #file.write("2 VERS %s\n" % printverylargetextpedigrees.__version__)
        file.write("2 VERS 0.0.1\n")
        file.write("2 NAME printverylargetextpedigrees\n")
        file.write("1 DATE %s\n" % time.strftime("%d %b %Y"))
        file.write("2 TIME %s\n" % time.strftime("%H:%M:%S"))
        file.write("1 SUBM @SUBM@\n")
        file.write("0 @SUBM@ SUBM\n")
        file.write("1 NAME %s\n" % self.display_name)
        file.write("1 LANG %s\n" % self.lang)

        for fid in sorted(self.indi, key=lambda x: self.indi.__getitem__(x).num):
            self.indi[fid].print(file)
        for husb, wife in sorted(self.fam, key=lambda x: self.fam.__getitem__(x).num):
            self.fam[(husb, wife)].print(file)
        sources = sorted(self.sources.values(), key=lambda x: x.num)
        for s in sources:
            s.print(file)
        notes = sorted(self.notes, key=lambda x: x.num)
        for i, n in enumerate(notes):
            if i > 0:
                if n.num == notes[i - 1].num:
                    continue
            n.print(file)
        file.write("0 TRLR\n")
        
    def print_pedigree(self, file, targetid):
        """print pedigree chart in text from tree objet"""

        def print_pedigree_recursive(file, targetid, level, linenumber, topOrBottom, parities) -> int:
            """recurse through tree, printing Individuals"""
            if targetid not in self.indi:
                return linenumber
            has_appeared = targetid in appeared_in_pedigree
            appeared_in_pedigree.add(targetid)
            mother = None
            father = None
            level += 1
            if self.indi[targetid].parents:
                father, mother = list(self.indi[targetid].parents)[0] # get perferred parents
            if father and not has_appeared:
                linenumber = print_pedigree_recursive(file, father, level, linenumber, 1, parities)
            linenumber += 1
            self.indi[targetid].print_pedigree(file, level, linenumber, topOrBottom, parities, has_appeared)
            if mother and not has_appeared:
                linenumber = print_pedigree_recursive(file, mother, level, linenumber, 0, parities|(1<<level))
            return linenumber

        file.write("\n\n\n")
        file.write("  Ancestors of ")
        self.indi[targetid].name.pretty_print(file)
        file.write("\n\n")
        appeared_in_pedigree = set()
        print_pedigree_recursive(file, targetid, -1, 0, 0, 0)
        appeared_in_pedigree.clear()
        
    def print_pedigree_html(self, targetid, maxlevel = 200) -> str:
        """print pedigree chart in html from tree objet"""
        linenumber = 0
        if maxlevel is None:
            maxlevel = 200
            
        def print_pedigree_collaspe_form() -> str:
            #if (AllowCollaspeAtGeneration):
            output = "<CENTER>"
            output += "<FORM>Collaspe all branches at select generation level: "
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

        def print_pedigree_html_menu() -> str:
            output = "<CENTER><B><A HREF=\"/index\">Master Index</A>\n";
            output += " | <A HREF=\"/individual/" + str(targetid) + "\">Individual Sheet</A>\n"
            output += " | <A HREF=\"/individual/" + str(targetid) + "/descendents\">Descendency Chart</A>\n"
            #if ($AllowGEDDownload): #Should we allow downloads of GedCom - not necessary 100% from file to memory, so not 100% from memory across network
            #    output +=  " | <a href=\"/gedcom/\"?Database=$DB&Subject=$focus&Name=$EncodeName&type=descendants>Extract GEDCOM</a>\n"
            output += "</B></CENTER><BR>"
            output += print_pedigree_collaspe_form()
            output += "<HR>\n"
            return output
            
        def print_pedigree_html_script() -> str:
            
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

        def print_pedigree_recursive_html(targetid, level, isTop, parities) -> (int, str):
            """recurse through tree, printing Individuals"""
            nonlocal linenumber
            nonlocal maxlevel
            output = ""
            if (level > maxlevel):   # TODO - use this in debugging to limit for now, still having trouble loading 45,000 people pedigrees
                return (0, "")
            if targetid not in self.indi:
                return (0, "")
            has_appeared = targetid in appeared_in_pedigree
            appeared_in_pedigree.add(targetid)
            mother = None
            father = None
            fatherlinenumber = 0
            motherlinenumber = 0
            level += 1
            if self.indi[targetid].parents:
                father, mother = list(self.indi[targetid].parents)[0] # get perferred parents
            # recurse into father pedigree
            if father and not has_appeared:
                fatherlinenumber, fatheroutput = print_pedigree_recursive_html(father, level, True, parities)
                output += fatheroutput
            # get family/marriage information (to display marriage information on top tree branches)
            family = None
            if (isTop):
                if self.indi[targetid].fams_num_spouses_num:
                    husb, wife = list(self.indi[targetid].fams_num_spouses_num)[0] # get perferred spouse family for now
                    if (husb, wife) in self.fam:
                        family = self.fam[(husb, wife)]
            # display individual
            linenumber = linenumber + 1
            mytemplinenumber = linenumber
            output += self.indi[targetid].print_pedigree_html(level, mytemplinenumber, isTop, parities, has_appeared, family)
            # recurse into mother pedigree
            if mother and not has_appeared:
                motherlinenumber, motheroutput = print_pedigree_recursive_html(mother, level, False, parities|(1<<level))
                output += motheroutput
            ancestors_line_numbers[mytemplinenumber] = [fatherlinenumber,motherlinenumber]
            return (mytemplinenumber, output)
        output = self.print_html_header() # would this make more sense to call from an HTMLFactory object?
        output += print_pedigree_html_menu()
        output += "<H1>Ancestors of " + self.indi[targetid].name.pretty_print() + "</H1>\n"
        output += "<pre><div id='DivID1'>"
        appeared_in_pedigree = set()
        ancestors_line_numbers = dict()
        _, recursiveoutput = print_pedigree_recursive_html(targetid, -1, False, 0)
        appeared_in_pedigree.clear()
        output += recursiveoutput
        output += "\n</div></pre>\n"
        output += "<HR>\n"
        output += print_pedigree_html_menu()
        output += print_pedigree_html_script()
        ancestors_line_numbers.clear()
        output += "</body>\n</html>\n"
        return output

    def print_html_header(self) -> str:
        """Prints HTML top part of page """
        # Should this go in another class like an HTMLRender class?
        title = self.indi[1].name.pretty_print() + "'s Genealogical Database"
        output = "<HTML lang=\"en\">\n"
        output += "<HEAD>\n"
        output += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
        output += "<TITLE>" + title + "</TITLE>\n"
        output += "<STYLE> div { display:inline; } </STYLE\n"
        output += "</HEAD>\n"
        output += "<BODY BACKGROUND=\"/images/background\" BGCOLOR=\"" + self.backgroundcolor 
        output += "\" TEXT=\"#000000\" LINK=\"" + self.linkcolor + "\" VLINK=\"" + self.visitedlinkcolor + "\">\n"
        output += "<CENTER><H2>" + title + "</H2></CENTER>\n";
        output += "<CENTER><B>Individuals:</B> " + str(len(self.indi)) + "&nbsp;&nbsp;"
        output += "<B>Families:</B> " + str(len(self.fam)) + "&nbsp;&nbsp;"
        output += "<BR><B>Gedcom Last Modified:</B> " + str(self.lastmodifiedtime) + "</CENTER>\n<HR>\n"
        #output += "<CENTER><B>Contact:</B> <A href=\"" + contact_email + "\">Michael M. Groat</A> &nbsp;&nbsp; "
        #output += "<B>Home Page:</B> <A href=\"" + home_page_url + "\">" + self.indi[1].name.pretty_print() + "'s Homepage</A></CENTER>"
        return output
        
