# This is a Python implementation of the following jsonLogic JS library:
# https://github.com/jwadhams/json-logic-js

import sys
from six.moves import reduce

def jsonLogic(tests, data=None):
  # You've recursed to a primitive, stop!
  if tests is None or type(tests) != dict:
    return tests

  data = data or {}

  op = list(tests.keys())[0]
  values = tests[op]
  operations = {
    "=="  : (lambda a, b: a == b),
    "===" : (lambda a, b: a is b),
    "!="  : (lambda a, b: a != b),
    "!==" : (lambda a, b: a is not b),
    ">"   : (lambda a, b: a > b),
    ">="  : (lambda a, b: a >= b),
    "<"   : (lambda a, b, c=None: 
        a < b if (c is None) else (a < b) and (b < c)
      ),
    "<="  : (lambda a, b, c=None:
        a <= b if (c is None) else (a <= b) and (b <= c)
      ),
    "!"   : (lambda a: not a),
    "%"   : (lambda a, b: a % b),
    "and" : (lambda *args: 
        reduce(lambda total, arg: total and arg, args, True)
      ),
    "or"  : (lambda *args:
        reduce(lambda total, arg: total or arg, args, False)
      ),
    "?:"  : (lambda a, b, c: b if a else c),
    "log" : (lambda a: a if sys.stdout.write(str(a)) else a),
    "in"  : (lambda a, b:
        a in b if "__contains__" in dir(b) else False
      ),
    "var" : (lambda a, not_found=None:
        reduce(lambda data, key: (data.get(key, not_found)
                                  if type(data) == dict
                                  else data[int(key)]
                                       if (type(data) in [list, tuple] and
                                           str(key).lstrip("-").isdigit())
                                       else not_found),
               str(a).split("."),
               data)
      ),
    "cat" : (lambda *args:
        "".join(args)
      ),
    "+" : (lambda *args:
        reduce(lambda total, arg: total + float(arg), args, 0.0)
      ),
    "*" : (lambda *args:
        reduce(lambda total, arg: total * float(arg), args, 1.0)
      ),
    "-" : (lambda a, b=None: -a if b is None else a - b),
    "/" : (lambda a, b=None: a if b is None else float(a) / float(b)),
    "min" : (lambda *args: min(args)),
    "max" : (lambda *args: max(args)),
    "count": (lambda *args: sum(1 if a else 0 for a in args)),
  }

  # Easy syntax for unary operators, like {"var": "x"} instead of strict
  # {"var": ["x"]}
  if type(values) not in [list, tuple]:
    values = [values]

  # Check for 'if' operation- cannot be evaluated in lambda expressions
  if op == 'if':
    '''
    'if' should be called with a odd number of parameters, 3 or greater
    This works on the pattern:
    if( 0 ){ 1 }else{ 2 };
    if( 0 ){ 1 }else if( 2 ){ 3 }else{ 4 };
    if( 0 ){ 1 }else if( 2 ){ 3 }else if( 4 ){ 5 }else{ 6 };
    The implementation is:
    For pairs of values (0,1 then 2,3 then 4,5 etc)
    If the first evaluates truthy, evaluate and return the second
    If the first evaluates falsy, jump to the next pair (e.g, 0,1 to 2,3)
    given one parameter, evaluate and return it. (it's an Else and all the If/ElseIf were false)
    given 0 parameters, return None
    '''
    i = 0
    while i < len(values) - 1:
      if jsonLogic(values[i], data) == True:
        return jsonLogic(values[i + 1], data)
      i += 2
      if len(values) == i + 1:
        return jsonLogic(values[i], data)
      else:
        return None

  if op not in operations:
    raise ValueError("Unrecognized operation %s" % op)

  # Recursion!
  values = map(lambda val: jsonLogic(val, data), values)

  return operations[op](*values)
