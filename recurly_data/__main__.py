# pylint: disable=missing-module-docstring,invalid-name
import argparse
import os
from recurly_data.recurly_data import RecurlyData
from . import __version__


description = "Recurly Data Generator."
prog = f"recurly_data {__version__}"
parser = argparse.ArgumentParser(
    description=description,
    prog=prog
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-q",
    "--quiet",
    default=False,
    action="store_true",
    help="Silent output."
)
group.add_argument(
    "-v",
    "--verbose",
    default=False,
    action="count",
    help="Increase output verbosity.",
)

parser.add_argument(
    "--version",
    action='version',
    version=__version__,
    help="Get the package version."
)

parser.add_argument(
    "-l",
    "--limit",
    type=int,
    help="Set a limit for the number of records."
)

parser.add_argument(
    "-f",
    "--file",
    type=str,
    default="recurly_data.csv",
    help=(
        "The filename where records should be stored. "
        "A file will be created if it doesn't already exist."
    )
)

args = parser.parse_args()
abs_file_path = os.path.abspath(
    os.path.expanduser(os.path.expandvars(args.file))
)

recurly_data = RecurlyData(
    limit=args.limit,
    silence=args.quiet,
    verbose=args.verbose,
    filename=abs_file_path
)
recurly_data.make_csv()
