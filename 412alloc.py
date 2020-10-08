import sys
import getopt

from Parser import Parser
from Renamer import Renamer
from Allocator import AllocatorWithSpill
from Allocator import AllocatorWithoutSpill


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:h')
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        usage()
        sys.exit(2)

    if sys.argv[1].isdigit():
        if int(sys.argv[1]) > 64 or int(sys.argv[1]) < 3:
            print("ERROR: k must be an integer between 3 and 64.", file=sys.stderr)
        else:
            allocate(sys.argv[2], int(sys.argv[1]))
    else:
        for o, a in opts:
            if o == '-x':
                rename(a)
            elif o == '-h':
                usage()
                sys.exit()
            else:
                usage()
                sys.exit(2)


def allocate(filename, k):
    parser = Parser.Parser(filename)
    result = parser.parse_file()

    if result[0]:
        if parser.valid_operation == 0:
            print("ERROR: ILOC file contained no valid operations.\n")
            print("ERROR: Terminating.")
        else:
            # core of this allocate routine
            renamer = Renamer.Renamer(parser)
            renamer.rename_sr_2_live_range()

            allocator = AllocatorWithSpill.AllocatorWithSpill(renamer, k)
            allocator.allocate_with_spill()
            allocator.print_allocated_block()
    else:
        print('\nParser found %i syntax errors in %i lines of input.' \
                             % (parser.num_errors, parser.scanner.lineNo - 1))


def rename(filename):
    parser = Parser.Parser(filename)
    result = parser.parse_file()

    if result[0]:
        if parser.valid_operation == 0:
            print("ERROR: ILOC file contained no valid operations.\n")
            print("ERROR: Terminating.")
        else:
            # core of this routine
            renamer = Renamer.Renamer(parser)
            renamer.rename_sr_2_live_range()
            renamer.print_renamed_block()
    else:
        print('\nParser found %i syntax errors in %i lines of input.' \
                             % (parser.num_errors, parser.scanner.lineNo - 1))


def usage():
    print("COMP 412, Fall 2020 Local Register Allocation (Lab 2)", file=sys.stderr)
    print("Command Syntax:", file=sys.stderr)
    print("      412alloc k filename [-h] [-x]", file=sys.stderr)
    print("\nRequired arguments:", file=sys.stderr)
    print("       k        specifies the number of register available", file=sys.stderr)
    print("       filename the pathname (absolute or relative) to the input file", file=sys.stderr)
    print("\nOptional flags:", file=sys.stderr)
    print("       -h        prints this message", file=sys.stderr)
    print("       -x        peforms register renaming", file=sys.stderr)


if __name__ == "__main__":
    main()