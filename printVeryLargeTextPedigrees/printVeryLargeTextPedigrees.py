# coding: utf-8

# global imports
from __future__ import print_function
import re
import sys
import time
from urllib.parse import unquote
import getpass
import asyncio
import argparse

# local imports
from classes.tree import Indi, Fam, Tree
from classes.gedcom import Gedcom
from classes.session import Session

def main():
    debug = True
    sys.stdout.reconfigure(encoding='UTF-8-SIG')
    parser = argparse.ArgumentParser(
        description="Retrieve GEDCOM data from FamilySearch Tree (4 Jul 2016)",
        add_help=False,
        usage="getmyancestors -u username -p password [options]",
    )
    parser.add_argument(
        "-u", "--username", metavar="<STR>", type=str, help="FamilySearch username"
    )
    parser.add_argument(
        "-p", "--password", metavar="<STR>", type=str, help="FamilySearch password"
    )
    parser.add_argument(
        "-i",
        "--individuals",
        metavar="<STR>",
        nargs="+",
        type=str,
        help="List of individual FamilySearch IDs for whom to retrieve ancestors",
    )
    parser.add_argument(
        "-a",
        "--ascend",
        metavar="<INT>",
        type=int,
        default=4,
        help="Number of generations to ascend [4]",
    )
    parser.add_argument(
        "-d",
        "--descend",
        metavar="<INT>",
        type=int,
        default=0,
        help="Number of generations to descend [0]",
    )
    parser.add_argument(
        "-m",
        "--marriage",
        action="store_true",
        default=False,
        help="Add spouses and couples information [False]",
    )
    parser.add_argument(
        "-r",
        "--get-contributors",
        action="store_true",
        default=False,
        help="Add list of contributors in notes [False]",
    )
    parser.add_argument(
        "-c",
        "--get_ordinances",
        action="store_true",
        default=False,
        help="Add LDS ordinances (need LDS account) [False]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Increase output verbosity [False]",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        metavar="<INT>",
        type=int,
        default=60,
        help="Timeout in seconds [60]",
    )
    parser.add_argument(
        "--show-password",
        action="store_true",
        default=False,
        help="Show password in .settings file [False]",
    )
    parser.add_argument(
        "--save-settings",
        action="store_true",
        default=False,
        help="Save settings into file [False]",
    )
    try:
        parser.add_argument(
            "-o",
            "--outfile",
            metavar="<FILE>",
            type=argparse.FileType("w", encoding="UTF-8"),
            default="GedCom.ged",
            help="output GEDCOM file [GEDCOM.ged]",
        )
        parser.add_argument(
            "-l",
            "--logfile",
            metavar="<FILE>",
            type=argparse.FileType("w", encoding="UTF-8"),
            default=False,
            help="output log file [stderr]",
        )
        parser.add_argument(
            "-f",
            "--load-from-file",
            metavar="<FILE>",
            type=argparse.FileType("r", encoding="UTF-8-SIG"),
            default=False,
            help="load GEDCOM from file instead of from Family Search",
        )
        parser.add_argument(
            "-po",
            "--pedigreeoutfile",
            metavar="<FILE>",
            type=argparse.FileType("w", encoding="UTF-8"),
            default=sys.stdout,
            help="output pedigree file [stdout]",
        )
    except TypeError as e:
        sys.stderr.write("Python >= 3.4 is required to run this script\n")
        sys.stderr.write("(see https://docs.python.org/3/whatsnew/3.4.html#argparse)\n")
        if debug:
            print("An exception occurred:", e)
            traceback.print_exc()
        sys.exit(2)

    # extract arguments from the command line
    try:
        parser.error = parser.exit
        args = parser.parse_args()
    except SystemExit:
        parser.print_help(file=sys.stderr)
        if debug:
            print("An exception occurred:", e)
            traceback.print_exc()
        sys.exit(2)
    if args.individuals:
        for fid in args.individuals:
            if not args.load_from_file and not re.match(r"[A-Z0-9]{4}-[A-Z0-9]{3}", fid):
                sys.exit("Invalid FamilySearch ID: " + fid)

    if not args.load_from_file:
        args.username = (
            args.username if args.username else input("Enter FamilySearch username: ")
        )
        args.password = (
            args.password
            if args.password
            else getpass.getpass("Enter FamilySearch password: ")
        )

    time_count = time.time()

    # Report settings used when getmyancestors is executed
    if args.save_settings and args.outfile.name != "<stdout>":

        def parse_action(act):
            if not args.show_password and act.dest == "password":
                return "******"
            value = getattr(args, act.dest)
            return str(getattr(value, "name", value))

        formatting = "{:74}{:\t>1}\n"
        settings_name = args.outfile.name.split(".")[0] + ".settings"
        try:
            with open(settings_name, "w") as settings_file:
                settings_file.write(
                    formatting.format("time stamp: ", time.strftime("%X %x %Z"))
                )
                for action in parser._actions:
                    settings_file.write(
                        formatting.format(
                            action.option_strings[-1], parse_action(action)
                        )
                    )
        except OSError as exc:
            print(
                "Unable to write %s: %s" % (settings_name, repr(exc)), file=sys.stderr
            )

    try:
    
        tree = None
        if not args.load_from_file:
            # initialize a FamilySearch session and a family tree object
            print("Login to FamilySearch...", file=sys.stderr)
            fs = Session(args.username, args.password, args.verbose, args.logfile, args.timeout)
            if not fs.logged:
                sys.exit(2)
            _ = fs._
            tree = Tree(fs)

            # check LDS account
            if args.get_ordinances:
                test = fs.get_url(
                    "/service/tree/tree-data/reservations/person/%s/ordinances" % fs.fid, {}
                )
                if test["status"] != "OK":
                    sys.exit(2)

                # add list of starting individuals to the family tree
                todo = args.individuals if args.individuals else [fs.fid]
                print(_("Downloading starting individuals..."), file=sys.stderr)
                tree.add_indis(todo)

            # download ancestors
            todo = set(tree.indi.keys())
            done = set()
            for i in range(args.ascend):
                if not todo:
                    break
                done |= todo
                print(
                    _("Downloading %s. of generations of ancestors...") % (i + 1),
                    file=sys.stderr,
                )
                todo = tree.add_parents(todo) - done

            # download descendants
            todo = set(tree.indi.keys())
            done = set()
            for i in range(args.descend):
                if not todo:
                    break
                done |= todo
                print(
                    _("Downloading %s. of generations of descendants...") % (i + 1),
                    file=sys.stderr,
                )
                todo = tree.add_children(todo) - done

            # download spouses
            if args.marriage:
                print(_("Downloading spouses and marriage information..."), file=sys.stderr)
                todo = set(tree.indi.keys())
                tree.add_spouses(todo)

            # download ordinances, notes and contributors
            async def download_stuff(loop):
                futures = set()
                for fid, indi in tree.indi.items():
                    futures.add(loop.run_in_executor(None, indi.get_notes))
                    if args.get_ordinances:
                        futures.add(loop.run_in_executor(None, tree.add_ordinances, fid))
                    if args.get_contributors:
                        futures.add(loop.run_in_executor(None, indi.get_contributors))
                for fam in tree.fam.values():
                    futures.add(loop.run_in_executor(None, fam.get_notes))
                    if args.get_contributors:
                        futures.add(loop.run_in_executor(None, fam.get_contributors))
                for future in futures:
                    await future

            loop = asyncio.get_event_loop()
            print(
                _("Downloading notes")
                + (
                    (("," if args.get_contributors else _(" and")) + _(" ordinances"))
                    if args.get_ordinances
                    else ""
                )
                + (_(" and contributors") if args.get_contributors else "")
                + "...",
                file=sys.stderr,
            )
            loop.run_until_complete(download_stuff(loop))
        else:
            tree = Tree()
            # Load from file
            ged = Gedcom(args.load_from_file, tree)
            tree.indi = ged.indi
            
            fam_counter = 0

            for person_num in tree.indi:
                if tree.indi[person_num].famc_num:
                    fam_num = list(tree.indi[person_num].famc_num)[0] # get perferred family only (only for printing pedigrees, we aren't storing tree)
                    if fam_num:
                        mother, father = (ged.fam[fam_num].husb_num, ged.fam[fam_num].wife_num)
                        if mother is not None or father is not None:
                            tree.indi[person_num].parents.add((mother,father))

            for num in ged.fam:
                husb, wife = (ged.fam[num].husb_num, ged.fam[num].wife_num)
                if (husb, wife) not in tree.fam:
                    fam_counter += 1
                    tree.fam[(husb, wife)] = Fam(husb, wife, tree, fam_counter)
                    tree.fam[(husb, wife)].tree = tree
                tree.fam[(husb, wife)].chil_num |= ged.fam[num].chil_num
                if ged.fam[num].num:
                    tree.fam[(husb, wife)].num = ged.fam[num].num
                if ged.fam[num].facts:
                    tree.fam[(husb, wife)].facts = ged.fam[num].facts
                if ged.fam[num].notes:
                    tree.fam[(husb, wife)].notes = ged.fam[num].notes
                if ged.fam[num].sources:
                    tree.fam[(husb, wife)].sources = ged.fam[num].sources
                tree.fam[(husb, wife)].sealing_spouse = ged.fam[num].sealing_spouse
            # do we want notes - assume only read into memory, not written back to filesystem

    finally:
        # compute number for family relationships and print GEDCOM file
        if not args.load_from_file:
            tree.reset_num()
            tree.print(args.outfile)
            print(
                _(
                    "Downloaded %s individuals, %s families, %s sources and %s notes "
                    "in %s seconds with %s HTTP requests."
                )
                % (
                    str(len(tree.indi)),
                    str(len(tree.fam)),
                    str(len(tree.sources)),
                    str(len(tree.notes)),
                    str(round(time.time() - time_count)),
                    str(fs.counter),
                ),
                file=sys.stderr,
            )
        else:
            time_finished_loading = time.time() - time_count
            print(
                "Loaded %s individuals, %s families, %s sources and %s notes "
                "in %s seconds from file %s."
                % (
                    str(len(tree.indi)),
                    str(len(tree.fam)),
                    str(len(tree.sources)),
                    str(len(tree.notes)),
                    str(round(time_finished_loading)),
                    str(args.load_from_file),
                 ),
                 file=sys.stderr,
             )
        time_count2 =  time.time()
        if args.load_from_file:
            tree.print_pedigree(args.pedigreeoutfile, int(args.individuals[0]))
        else:
            tree.print_pedigree(args.pedigreeoutfile, args.individuals[0])
        print("Loaded and parsed GEDCOM in %s seconds"%(str(time_finished_loading)),file=sys.stderr,)
        print("Printed family pedigree in %s seconds" %(str(time.time() - time_count2)),file=sys.stderr,)


if __name__ == "__main__":
    main()
