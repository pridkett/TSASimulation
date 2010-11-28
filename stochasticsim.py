"""
Copyright (c) 2010 Patrick Wagstrom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import random
import re
import fourFn

# Simulation Constants
NUM_SIMULATIONS=10000
SPLIT_CHARACTERS = '[ +-/*\(\)]'
NUMERIC_RE = r"[0-9]+(\.[0-9]+)?"

# Base Classes for Simulation
class SimpleValue(object):
    def __init__(self, name, units, comments=None):
        object.__init__(self)
        self.name = name
        self.units = units
        self.comments = comments
        self.calculated_values = []
        self.calculated = False

    def calc(self):
        raise Exception("no calc function defined")

class RandomValue(SimpleValue):
    def __init__(self, name, units, gen, comments=None):
        SimpleValue.__init__(self, name, units, comments)
        self.gen = gen

    def calc(self, iterations=NUM_SIMULATIONS):
        self.calculated = True
        self.calculated_values = [self.gen.get() for x in xrange(NUM_SIMULATIONS)]

class RandomNumber(object):
    def __init__(self):
        object.__init__(self)

    def get(self):
        raise Exception("no get function defined")

class RandomNormal(RandomNumber):
    def __init__(self, mean, stdev):
        RandomNumber.__init__(self)
        self.mean = mean
        self.stdev = stdev

    def get(self):
        return random.normalvariate(self.mean, self.stdev)

class RandomTriangular(RandomNumber):
    """
    Triangular distributions require python 2.6.  Unfortunately, most
    macs only have python 2.5.  Be cautious when using.
    """
    def __init__(self, low, med, high):
        RandomNumber.__init__(self)
        self.low = low
        self.med = med
        self.high = high

    def get(self):
        return random.triangular(self.low, self.med, self.high)

class RandomUniform(RandomNumber):
    def __init__(self, low, high):
        RandomNumber.__init__(self)
        self.low = low
        self.high = high

    def get(self):
        return random.uniform(self.low, self.high)

class RandomFixed(RandomNumber):
    def __init__(self, val):
        object.__init__(self)
        self.val = val

    def get(self):
        return self.val

class RandomTabular(RandomNumber):
    """
    Represents a random value that is based on a tabular outcome.  This is
    most useful for situations where there are dramatic outcomes relative
    to rare chance.  For example, periodic terrorist attacks.
    """
    # FIXME: I believe that Python may have a random routine built in that
    # could address this sort of random number generation
    def __init__(self, table):
        """
        @param table: a set of tuples of either (chance, value) or (chance, RandomNumber)
        """
        self.table = table

        totalChance = sum([x[0] for x in self.table])
        if totalChance > 1:
            raise Exception("Total chance of events is greater than 1.")

        # create the lookup table for the random number generator
        self.sumchances = []
        for val in self.table:
            if len(self.sumchances) == 0:
                self.sumchances.append(val[0])
            else:
                self.sumchances.append(val[0] + self.sumchances[-1])

    # FIXME: this is probably overly complex 
    def get(self):
        thisval = random.random()
        for key, val in enumerate(self.sumchances):
            if thisval < val:
                if isinstance(self.table[key][1], RandomNumber):
                    return self.table[key][1].get()
                return self.table[key][1]
        return 0.0

class CalculatedValue(SimpleValue):
    def __init__(self, name, units, equation, comments=None):
        SimpleValue.__init__(self, name, units, comments)
        self.equation = equation
        self.variables = None

    def calc(self, rvs, cvs):
        """
        This is horribly inefficient for calculation right now as it generates
        and reparses an equation for each calculation.  I just don't want to
        write a better calculator right now.
        """
        if self.variables == None:
            self.variables = {}
            varnames = [x for x in re.split(SPLIT_CHARACTERS, self.equation) if len(x) > 0]
            for x in varnames:
                if rvs.has_key(x):
                    self.variables[x] = rvs[x]
                elif cvs.has_key(x):
                    self.variables[x] = cvs[x]
                elif re.match(NUMERIC_RE, x):
                    pass
                else:
                    raise Exception("Variable: %s not found", x)
        if False not in [x.calculated for x in self.variables.itervalues()]:
            keys = self.variables.keys()
            keys.sort(key=lambda x: len(x), reverse=True)

            for iter in xrange(NUM_SIMULATIONS):
                tmpEquation = self.equation
                for key in keys:
                    tmpEquation = tmpEquation.replace(key, unicode(self.variables[key].calculated_values[iter]))
                self.calculated_values.append(fourFn.simpleEval(tmpEquation))
            self.calculated = True
            return True
        else:
            return False


