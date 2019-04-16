from __future__ import division
from __future__ import print_function
import boost.std_pair
from libtbx.test_utils import Exception_expected

def run():
  boost.std_pair.exercise(( 1, 2)) == ( 2, 1.)
  boost.std_pair.exercise((-2, 4)) == (-4, 2.)

  try:
    boost.std_pair.exercise(1)
  except Exception as err:
    assert err.__class__.__name__ == 'ArgumentError'
  else:
    raise Exception_expected

  try:
    boost.std_pair.exercise((1,))
  except Exception as err:
    assert err.__class__.__name__ == 'ArgumentError'
  else:
    raise Exception_expected

  try:
    boost.std_pair.exercise((1,2,3,))
  except Exception as err:
    assert err.__class__.__name__ == 'ArgumentError'
  else:
    raise Exception_expected

  print("OK")

if __name__ == '__main__':
  run()
