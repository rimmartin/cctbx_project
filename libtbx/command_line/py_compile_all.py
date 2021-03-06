from __future__ import absolute_import, division, print_function

import argparse
import compileall
import os

def run():
  # parser with subset of flags
  parser = argparse.ArgumentParser(description='Compiles .py files into .pyc.')
  parser.add_argument('-f', action='store_true', dest='force',
                      help='force rebuild even if timestamps are up to date')
  parser.add_argument('-v', action='count', dest='quiet', default=0,
                      help=('default is no output, -v is error messages only, '
                            '-vv is all output'))
  # parser.add_argument('-j', '--workers', default=1,
  #                     type=int, help='Run compileall with multiple cores')
  parser.add_argument('compile_dest', metavar='DIR', nargs='*',
                      help=('zero or more directory names to compile; '
                            'if no arguments given, defaults '
                            'to the current working directory'))
  args = parser.parse_args()

  if (len(args.compile_dest) == 0):
    args.compile_dest = [os.getcwd()]

  args.quiet = 2 - args.quiet
  if (args.quiet < 0):
    args.quiet = 0

  for dest in args.compile_dest:
    compileall.compile_dir(dest, 100, force=args.force, quiet=args.quiet)

if (__name__ == "__main__"):
  run()
