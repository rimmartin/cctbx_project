from __future__ import division, print_function

import optparse
import sys

def process_each(process, file_names, report_success=False):
  import traceback
  n_fail = 0
  n_succ = 0
  for file_name in file_names:
    try:
      process(file_names=[file_name])
    except Exception:
      n_fail += 1
      print("FAILING:", file_name)
      print(traceback.format_exc(limit=None))
    else:
      if (report_success):
        print("SUCCESS:", file_name)
      n_succ += 1
  if (n_fail != 0):
    print("Failing:", n_fail)
  if (n_succ != 0):
    print("Success:", n_succ)

def report_equivalence_clusters_with_mixed_data_types(fproc):
  for equiv_tok_cluster in fproc.equivalence_info().equiv_tok_clusters:
    data_types_list = []
    data_types_set = set()
    for equiv_tok in equiv_tok_cluster:
      for tok_seq in equiv_tok.value:
        identifier = tok_seq.value[0].value
        fdecl = fproc.fdecl_by_identifier[identifier]
        dt = fdecl.data_type
        if (dt is not None):
          data_types_list.append((identifier,dt.value))
          data_types_set.add(dt.value)
    if (len(data_types_set) > 1):
      print(equiv_tok_cluster[0].value[0].value[0].format_error(
        msg="Warning: EQUIVALENCE cluster with mixed data types: %s" %
          ", ".join(sorted(data_types_set))))
      for identifier,dtv in data_types_list:
        print("  %s: %s" % (identifier, dtv))

def run(args):
  if (len(args) == 0): args = ["--help"]
  import libtbx.load_env
  parser = optparse.OptionParser(usage="%s [options] fortran_file ..."%libtbx.env.dispatcher_name)
  parser.add_option("-?", action="help", help=optparse.SUPPRESS_HELP)
  parser.add_option("--each", action="store_true", default=False)
  parser.add_option("--report_success", action="store_true", default=False)
  parser.add_option("--report-success", action="store_true", help=optparse.SUPPRESS_HELP)
  parser.add_option("--warnings", action="store_true", default=False)
  co, files = parser.parse_args(args)

  def sorry_exclusive(opt_name):
    from libtbx.utils import Sorry
    raise Sorry(
      "%s: options are mutually exclusive: --each, --%s"
        % (libtbx.env.dispatcher_name, opt_name))
  if (co.each):
    if (co.warnings): sorry_exclusive("warnings")
  from fable.read import process
  if (co.each):
    process_each(
      process=process,
      file_names=files,
      report_success=co.report_success)
  else:
    all_fprocs = process(file_names=files)
    if (co.warnings):
      for fproc in all_fprocs.all_in_input_order:
        report_equivalence_clusters_with_mixed_data_types(fproc=fproc)

if (__name__ == "__main__"):
  run(args=sys.argv[1:])
