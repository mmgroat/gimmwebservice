# mergemyancestors classes
#from gimmwebservices.classes.tree import (
from classes.tree import (
    Indi,
    Fact,
    Fam,
    Memorie,
    Name,
    Note,
    Ordinance,
    Source,
)
#from gimmwebservices.classes.constants import FACT_TYPES, ORDINANCES
from classes.constants import FACT_TYPES, ORDINANCES

class Gedcom:
    """Parse a GEDCOM file into a Tree"""

    def __init__(self, file, tree):
        self.f = file
        self.num = None
        self.tree = tree
        self.level = 0
        self.pointer = None
        self.tag = None
        self.data = None
        self.flag = False
        self.indi = dict()
        self.fam = dict()
        self.note = dict()
        self.sour = dict()
        self.__parse()
        self.__add_id()

    def __parse(self):
        """Parse the GEDCOM file into self.tree"""
        while self.__get_line():
            if self.tag == "INDI":
                self.num = int(self.pointer[2 : len(self.pointer) - 1])
                self.indi[self.num] = Indi(tree=self.tree, num=self.num)
                self.__get_indi()
            elif self.tag == "FAM":
                self.num = int(self.pointer[2 : len(self.pointer) - 1])
                if self.num not in self.fam:
                    self.fam[self.num] = Fam(tree=self.tree, num=self.num)
                self.__get_fam()
            elif self.tag == "NOTE":
                self.num = int(self.pointer[2 : len(self.pointer) - 1])
                if self.num not in self.note:
                    self.note[self.num] = Note(tree=self.tree, num=self.num)
                self.__get_note()
            elif self.tag == "SOUR" and self.pointer:
                self.num = int(self.pointer[2 : len(self.pointer) - 1])
                if self.num not in self.sour:
                    self.sour[self.num] = Source(num=self.num)
                self.__get_source()
            elif self.tag == "SUBM" and self.pointer:
                self.__get_subm()

    def __get_subm(self):
        while self.__get_line() and self.level > 0:
            if not self.tree.display_name or not self.tree.lang:
                if self.tag == "NAME":
                    self.tree.display_name = self.data
                elif self.tag == "LANG":
                    self.tree.lang = self.data
        self.flag = True

    def __get_line(self):
        """Parse a new line
        If the flag is set, skip reading a newline
        """
        if self.flag:
            self.flag = False
            return True
        words = self.f.readline().split()

        if not words:
            return False
        self.level = int(words[0])
        if words[1][0] == "@":
            self.pointer = words[1]
            self.tag = words[2]
            self.data = " ".join(words[3:])
        else:
            self.pointer = None
            self.tag = words[1]
            self.data = " ".join(words[2:])
        return True

    def __get_indi(self):
        """Parse an individual"""
        while self.f and self.__get_line() and self.level > 0:
            if self.tag == "NAME":
                self.__get_name()
            elif self.tag == "SEX":
                self.indi[self.num].gender = self.data
            elif self.tag in FACT_TYPES or self.tag == "EVEN":
                self.indi[self.num].facts.add(self.__get_fact())
            elif self.tag == "BAPL":
                self.indi[self.num].baptism = self.__get_ordinance()
            elif self.tag == "CONL":
                self.indi[self.num].confirmation = self.__get_ordinance()
            elif self.tag == "ENDL":
                self.indi[self.num].endowment = self.__get_ordinance()
            elif self.tag == "SLGC":
                self.indi[self.num].sealing_child = self.__get_ordinance()
            elif self.tag == "FAMS":
                self.indi[self.num].fams_num.add(int(self.data[2 : len(self.data) - 1]))
            elif self.tag == "FAMC":
                self.indi[self.num].famc_num.add(int(self.data[2 : len(self.data) - 1]))
            elif self.tag == "_FSFTID":
                self.indi[self.num].fid = self.data
            elif self.tag == "NOTE":
                num = int(self.data[2 : len(self.data) - 1])
                if num not in self.note:
                    self.note[num] = Note(tree=self.tree, num=num)
                self.indi[self.num].notes.add(self.note[num])
            elif self.tag == "SOUR":
                self.indi[self.num].sources.add(self.__get_link_source())
            elif self.tag == "OBJE":
                self.indi[self.num].memories.add(self.__get_memorie())
        self.flag = True

    def __get_fam(self):
        """Parse a family"""
        while self.__get_line() and self.level > 0:
            if self.tag == "HUSB":
                self.fam[self.num].husb_num = int(self.data[2 : len(self.data) - 1])
            elif self.tag == "WIFE":
                self.fam[self.num].wife_num = int(self.data[2 : len(self.data) - 1])
            elif self.tag == "CHIL":
                self.fam[self.num].chil_num.add(int(self.data[2 : len(self.data) - 1]))
            elif self.tag in FACT_TYPES:
                self.fam[self.num].facts.add(self.__get_fact())
            elif self.tag == "SLGS":
                self.fam[self.num].sealing_spouse = self.__get_ordinance()
            elif self.tag == "_FSFTID":
                self.fam[self.num].fid = self.data
            elif self.tag == "NOTE":
                num = int(self.data[2 : len(self.data) - 1])
                if num not in self.note:
                    self.note[num] = Note(tree=self.tree, num=num)
                self.fam[self.num].notes.add(self.note[num])
            elif self.tag == "SOUR":
                self.fam[self.num].sources.add(self.__get_link_source())
        self.flag = True

    def __get_name(self):
        """Parse a name"""
        parts = self.__get_text().split("/")
        name = Name()
        added = False
        name.given = parts[0].strip()
        if len(parts) > 1:
            name.surname = parts[1].strip()
        else: 
            name.surname = ""
        if len(parts) > 2:
            name.suffix = parts[2]
        if not self.indi[self.num].name:
            self.indi[self.num].name = name
            added = True
        while self.__get_line() and self.level > 1:
            if self.tag == "NPFX":
                name.prefix = self.data
            elif self.tag == "TYPE":
                if self.data == "aka":
                    self.indi[self.num].aka.add(name)
                    added = True
                elif self.data == "married":
                    self.indi[self.num].married.add(name)
                    added = True
            elif self.tag == "NICK":
                nick = Name()
                nick.given = self.data
                self.indi[self.num].nicknames.add(nick)
            elif self.tag == "NOTE":
                num = int(self.data[2 : len(self.data) - 1])
                if num not in self.note:
                    self.note[num] = Note(tree=self.tree, num=num)
                name.note = self.note[num]
            elif self.tag == "SOUR":
                name.sources.add(self.__get_link_source(cutoff_level = 2))
        if not added:
            self.indi[self.num].birthnames.add(name)
        self.flag = True

    def __get_fact(self):
        """Parse a fact"""
        fact = Fact()
        if self.tag != "EVEN":
            fact.type = FACT_TYPES[self.tag]
            fact.value = self.data
        while self.__get_line() and self.level > 1:
            if self.tag == "TYPE":
                fact.type = self.data
            if self.tag == "DATE":
                fact.date = self.__get_text()
            elif self.tag == "PLAC":
                fact.place = self.__get_text()
            elif self.tag == "MAP":
                fact.map = self.__get_map()
            elif self.tag == "NOTE":
                if self.data[:12] == "Description:":
                    fact.value = self.data[13:]
                    continue
                num = int(self.data[2 : len(self.data) - 1])
                if num not in self.note:
                    self.note[num] = Note(tree=self.tree, num=num)
                # MMG - Dont assume note is singular?
                fact.notes.add(self.note[num])
            # MMG CONT and CONC could be from a note that is a "Description"
            elif self.tag == "CONT":
                fact.value += "\n" + self.data
            elif self.tag == "CONC":
                if self.data is not None and fact.value is not None:
                    fact.value += self.data
            elif self.tag == "SOUR":
                fact.sources.add(self.__get_link_source(cutoff_level = 2))
        self.flag = True
        return fact

    def __get_map(self):
        """Parse map coordinates"""
        latitude = None
        longitude = None
        while self.__get_line() and self.level > 3:
            if self.tag == "LATI":
                latitude = self.data
            elif self.tag == "LONG":
                longitude = self.data
        self.flag = True
        return (latitude, longitude)

    def __get_text(self):
        """Parse a multiline text"""
        text = self.data
        while self.__get_line():
            if self.tag == "CONT":
                text += "\n" + self.data
            elif self.tag == "CONC":
                text += self.data
            else:
                break
        self.flag = True
        return text

    def __get_source(self):
        """Parse a source"""
        while self.__get_line() and self.level > 0:
            if self.tag == "TITL":
                self.sour[self.num].title = self.__get_text()
            elif self.tag == "AUTH":
                self.sour[self.num].citation = self.__get_text()
            elif self.tag == "PUBL":
                self.sour[self.num].url = self.__get_text()
            elif self.tag == "REFN":
                self.sour[self.num].fid = self.data
                if self.data in self.tree.sources:
                    self.sour[self.num] = self.tree.sources[self.data]
                else:
                    self.tree.sources[self.data] = self.sour[self.num]
            elif self.tag == "NOTE":
                try:
                    num = int(self.data[2 : len(self.data) - 1])
                except ValueError:
                    continue
                if num not in self.note:
                    self.note[num] = Note(tree=self.tree, num=num)
                self.sour[self.num].notes.add(self.note[num])
        self.flag = True

    def __get_link_source(self, cutoff_level = 1):
        """Parse a link to a source"""
        num = None
        details = ''
        if self.data[:8] == "Details:":
            details = self.data[13:]
        else: 
            try:
                num = int(self.data[2 : len(self.data) - 1])
            except ValueError:
                if num is not None:
                    print("Source Error " + str(num))
                else:
                    print("Source Error " + self.data)
                return None
        if num not in self.sour:
            self.sour[num] = Source(num=num)
        page = details
        while self.__get_line() and self.level > cutoff_level:
            if self.tag == "PAGE":
                page += self.__get_text()
            if self.tag == "_FOOT":
                page += self.__get_text()
        self.flag = True
        return (self.sour[num], page)

    def __get_memorie(self):
        """Parse a memorie"""
        memorie = Memorie()
        while self.__get_line() and self.level > 1:
            if self.tag == "TITL":
                memorie.description = self.__get_text()
            elif self.tag == "FILE":
                memorie.url = self.__get_text()
        self.flag = True
        return memorie

    def __get_note(self):
        """Parse a note"""
        self.note[self.num].text = self.__get_text()
        self.flag = True

    def __get_ordinance(self):
        """Parse an ordinance"""
        ordinance = Ordinance()
        while self.__get_line() and self.level > 1:
            if self.tag == "DATE":
                ordinance.date = self.__get_text()
            elif self.tag == "TEMP":
                ordinance.temple_code = self.data
            elif self.tag == "STAT":
                ordinance.status = ORDINANCES[self.data]
            elif self.tag == "FAMC":
                num = int(self.data[2 : len(self.data) - 1])
                if num not in self.fam:
                    self.fam[num] = Fam(tree=self.tree, num=num)
                ordinance.famc = self.fam[num]
        self.flag = True
        return ordinance

    def __add_id(self):
        """Reset GEDCOM identifiers"""
        for num in self.fam:
            if self.fam[num].husb_num:
                self.fam[num].husb_fid = self.indi[self.fam[num].husb_num].fid
            if self.fam[num].wife_num:
                self.fam[num].wife_fid = self.indi[self.fam[num].wife_num].fid
            for chil in self.fam[num].chil_num:
                self.fam[num].chil_fid.add(self.indi[chil].fid)
                # add chil to parents.children set - MMG
                if self.fam[num].husb_num in self.indi:
                    self.indi[self.fam[num].husb_num].children.add((self.fam[num].husb_num, self.fam[num].wife_num, chil))
                if self.fam[num].wife_num in self.indi:
                    self.indi[self.fam[num].wife_num].children.add((self.fam[num].husb_num, self.fam[num].wife_num, chil))
        for num in self.indi:
            for famc in self.indi[num].famc_num:
                self.indi[num].famc_fid.add(
                    (self.fam[famc].husb_fid, self.fam[famc].wife_fid)
                )
            for fams in self.indi[num].fams_num:
                # This may be a bug, what if there are multiple spouses that are unknown? May need to add fams_num as third in tuple.
                self.indi[num].fams_fid.add(
                    (self.fam[fams].husb_fid, self.fam[fams].wife_fid)
                )
                # Create new set fams_num_spouse_num, which contains the husb, wife individual nums (not fid) 
                # original fams_num just contains the spouse's family num, not an individual num. Would have to do lots 
                # of redirection to get to family in tree.fam - since that is now indexed on individual nums. - MMG
                self.indi[num].fams_num_spouses_num.add(
                    (self.fam[fams].husb_num, self.fam[fams].wife_num)
                )
                # Add spouses information for easy parsing on individual sheet
                if self.fam[fams].husb_num == num:
                    self.indi[num].spouses.add(self.fam[fams].wife_num)
                if self.fam[fams].wife_num == num:
                    self.indi[num].spouses.add(self.fam[fams].husb_num)
     