from __future__ import division
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional,
                       ZeroOrMore, Forward, nums, alphas, oneOf)
import math
import operator

__author__ = 'Paul McGuire'
__version__ = '$Revision: 0.0 $'
__date__ = '$Date: 2009-03-20 $'
__source__ = '''http://pyparsing.wikispaces.com/file/view/fourFn.py
http://pyparsing.wikispaces.com/message/view/home/15549426
'''
__note__ = '''
All I've done is rewrap Paul McGuire's fourFn.py as a class, so I can use it
more easily in other places.
'''


class NumericStringParser(object):
  '''
  Most of this code comes from the fourFn.py pyparsing example

  '''

  def pushFirst(self, strg, loc, toks):
    self.exprStack.append(toks[0])

  def pushUMinus(self, strg, loc, toks):
    if toks and toks[0] == '-':
      self.exprStack.append('unary -')

  def __init__(self):
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    point = Literal(".")
    e = CaselessLiteral("E")
    fnumber = Combine(Word("+-" + nums, nums) +
                      Optional(point + Optional(Word(nums))) +
                      Optional(e + Word("+-" + nums, nums)))
    ident = Word(alphas, alphas + nums + "_$")
    plus = Literal("+")
    minus = Literal("-")
    mult = Literal("*")
    div = Literal("/")
    lpar = Literal("(").suppress()
    rpar = Literal(")").suppress()
    addop = plus | minus
    multop = mult | div
    expop = Literal("^")
    pi = CaselessLiteral("PI")
    expr = Forward()
    atom = ((Optional(oneOf("- +")) +
             (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
            | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
            ).setParseAction(self.pushUMinus)
    # by defining exponentiation as "atom [ ^ factor ]..." instead of
    # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
    # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
    factor = Forward()
    factor << atom + \
    ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
    term = factor + \
           ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
    expr << term + \
    ZeroOrMore((addop + term).setParseAction(self.pushFirst))
    # addop_term = ( addop + term ).setParseAction( self.pushFirst )
    # general_term = term + ZeroOrMore( addop_term ) | OneOrMore( addop_term)
    # expr <<  general_term
    self.bnf = expr
    # map operator symbols to corresponding arithmetic operations
    epsilon = 1e-12
    self.opn = {"+": operator.add,
                "-": operator.sub,
                "*": operator.mul,
                "/": operator.truediv,
                "^": operator.pow}
    self.fn = {"sin": math.sin,
               "cos": math.cos,
               "tan": math.tan,
               "exp": math.exp,
               "abs": abs,
               "trunc": lambda a: int(a),
               "round": round,
               "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}

  def evaluateStack(self, s):
    op = s.pop()
    if op == 'unary -':
      return -self.evaluateStack(s)
    if op in "+-*/^":
      op2 = self.evaluateStack(s)
      op1 = self.evaluateStack(s)
      return self.opn[op](op1, op2)
    elif op == "PI":
      return math.pi  # 3.1415926535
    elif op == "E":
      return math.e  # 2.718281828
    elif op in self.fn:
      return self.fn[op](self.evaluateStack(s))
    elif op[0].isalpha():
      return 0
    else:
      return float(op)

  def eval(self, num_string, parseAll=True):
    self.exprStack = []
    results = self.bnf.parseString(num_string, parseAll)
    val = self.evaluateStack(self.exprStack[:])
    return val

#==========================================================================

import itertools
import numpy as np

# operations = np.array(['p','p','p','p','m','m','m','m','t','t','t','t','d','d','d','d'])
# operations = np.array(['+','+','+','-','-','-','*','*','*','/','/','/'])
operations = np.array(['+','-','*','/'])

# _73s = np.array([7, 7, 3, 3])
num_73s = list(set(itertools.permutations([7,7,3,3])))
# num_73s = list(itertools.product([3,7], repeat=4))

# num_opers = list(itertools.permutations(operations,3))
num_opers = list(itertools.product(operations, repeat=3))
nsp = NumericStringParser()

def calc_arith( _73, opers):
  last = _73[0]
  for k in range(0,len(opers)):
    # result = nsp.eval('2^4')
    eq = str(last) + opers[k] + str(_73[k+1])
    last = nsp.eval(eq)
  return last

solutions = {}
for s,_73 in enumerate(num_73s):
  # _73 = _73s[list(k73)]
  for n,opers in enumerate(num_opers):
    val = calc_arith(_73,opers)
    if val==24:
      k = len(solutions.keys())
      solutions[k] = (s,n)

print(solutions)

#=================================================================
