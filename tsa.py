import random
import re
import fourFn
import csv

# Simulation Constants
NUM_SIMULATIONS=10000
SPLIT_CHARACTERS = '[ +-/*]'
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


# container for the calculated and random values
cvs = {}
rvs = {}

# Assumptions -- Feel free to tinker with these
rvs["value_of_human_life"] = RandomValue("Value of a Human Life",
                                  "Dollars",
                                  RandomFixed(6900000),
                                  "Source: EPA 2008")

rvs["risk_vpi"] = RandomValue("Risk of Dying from a Violent Passenger Incident",
                       "Percentage",
                       RandomNormal(22.0/1000000000.0, 3.0),
                       """Source: http://www.schneier.com/blog/archives/2010/01/nate_silver_on.html.
                          Uncertainty added by me""")

rvs["risk_nvpi"] = RandomValue("Risk of Dying from a Non-Violent Passenger Incident",
                        "Percentage",
                        RandomUniform(1.0/1000000.0, 1.0/10000000.0),
                        """Source: http://www.cotf.edu/ete/modules/volcanoes/vrisk.html""")

rvs["passenger_enplanements"] = RandomValue("Number of Passengers On Commercial Flights Each Year in the US",
                                     "Persons/Year",
                                     RandomNormal(621000000, 10000000),
                                     """Source: http://www.transtats.bts.gov/ (Domestic Only)""")

rvs["flight_distance"] = RandomValue("Average Distance of a Flight that Someone Might Be Willing to Drive",
                              "Miles",
                              RandomFixed(500),
                              """Source: my own estimate""")

rvs["percentage_passengers_driving"] = RandomValue("Fraction of Passengers Choosing to Drive Rather Than Fly",
                                 "Percentage",
                                 RandomUniform(0.005, 0.05),
                                 """Source: my own estimate""")

rvs["fatalities_mile"] = RandomValue("Fatalities Per Mile Driven in the United States",
                              "Persons",
                              RandomNormal(1.13/100000000.0, 0.1/100000000.0),
                              """Source: http://www-fars.nhtsa.dot.gov/Main/index.aspx""")

rvs["ait_scanner_cost"] = RandomValue("Cost of Installing an AIT Scanner",
                               "Dollars",
                               RandomUniform(70000,200000),
                               """Source: http://www.csmonitor.com/Business/2010/1119/TSA-body-scanners-safety-upgrade-or-stimulus-boondoggle""")

# put your equations here

cvs["number_passengers_driving"]  = CalculatedValue("Number of passengers who actually choose to drive",
                                                    "Persons",
                                                    "passenger_enplanements * percentage_passengers_driving")
cvs["number_new_driving_fatalities"] = CalculatedValue("Number of additional fatalities from new drivers",
                                                       "Persons",
                                                       "number_passengers_driving * flight_distance * 2 * fatalities_mile",
                                                       "Flight distance multipled by two because people need to drive home")

# rest of this is simulation stuff, you shouldn't need to modify much here
random.seed()

for key, val in rvs.iteritems():
    print "Calculating: %s" % (key)
    val.calc()

while False in [x.calculated for x in cvs.itervalues()]:
    calculated_variables = []
    for key, val in cvs.iteritems():
        if val.calculated == False:
            print "Calculating: %s" % (key)
            calculated_variables.append(val.calc(rvs, cvs))
    if not(calculated_variables) or True not in calculated_variables:
        raise Exception("Stalemate!")

print "Dumping data to sim.csv"
f = open("sim.csv", "wb")
csvwriter = csv.writer(f, delimiter=" ")
rvkeys = rvs.keys()
keys = cvs.keys()
csvwriter.writerow(rvkeys + keys)
for x in xrange(NUM_SIMULATIONS):
    thisrow = [rvs[y].calculated_values[x] for y in rvkeys]
    thisrow = thisrow + [cvs[y].calculated_values[x] for y in keys]
    csvwriter.writerow(thisrow)
f.close()

