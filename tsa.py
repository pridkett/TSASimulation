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
import csv
from stochasticsim import RandomValue, RandomFixed, RandomNormal, RandomUniform, RandomTriangular, CalculatedValue, NUM_SIMULATIONS

# container for the calculated and random values
cvs = {}
rvs = {}

# Assumptions -- Feel free to tinker with these
rvs["value_human_life"] = RandomValue("Value of a Human Life",
                                  "Dollars",
                                  RandomFixed(6900000),
                                  "Source: EPA 2008")

rvs["risk_vpi"] = RandomValue("Risk of Dying from a Violent Passenger Incident",
                       "Percentage",
                       RandomNormal(22.0/1000000000.0, 3.0/1000000000.0),
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

rvs["ait_success_rate"] = RandomValue("Success rate of AIT scanners at preventing terrorist attacks",
                                      "Percentage",
                                      RandomUniform(0.50, 0.80),
                                      """Source: my own estimate (WAG)""")

rvs["ait_scanner_cost"] = RandomValue("Cost of Installing an AIT Scanner",
                               "Dollars",
                               RandomUniform(70000,200000),
                               """Source: http://www.csmonitor.com/Business/2010/1119/TSA-body-scanners-safety-upgrade-or-stimulus-boondoggle""")

rvs["percentage_ait_screening"] = RandomValue("Percentage of passengers experiencing AIT screening",
                                              "Percentage",
                                              # RandomTriangular(0.17, 0.25, 0.40),
                                              RandomUniform(0.17, 0.40), # I'd like to use the triangular, but Python 2.5 on my mac doesn't support it
                                              """Source: http://boardingarea.com/blogs/flyingwithfish/2010/11/23/will-you-encounter-a-tsa-whole-body-scanner-statistically-no/

                                                 This source looks strictly at the number of security lanes, not
                                                 the proportion of passengers those lanes handle.  As most of
                                                 the airports in the largest metropolitan areas already have the
                                                 scanners, I take his 17% as a lower bound.""")

rvs["percentage_ait_devices_backscatter"] = RandomValue("Percentage of AIT devices that utilize backscatter x-ray technology",
                                                        "Percentage",
                                                        # RandomTriangular(0.3, 0.5, 0.75),
                                                        RandomUniform(0.3, 0.75), # see above comment about Mac python version
                                                        """Source: http://www.flyertalk.com/forum/travel-safety-security/1138014-complete-list-airports-whole-body-imaging-advanced-imaging-technology-scanner.html

                                                           This list frequently updates and sometimes MMWD may be identified as backscatter.""")

rvs["passenger_exposure_per_screening"] = RandomValue("Passenger Exposure per Screening",
                                                      "micro Sv/screening",
                                                      RandomUniform(0.20,0.80),
                                                      """Source: http://www.public.asu.edu/~atppr/RPD-Final-Form.pdf
                                                         Mandated max is 0.25uSv/screening, however Peter Rez claims up to 0.80uSv/screening in this paper""")

rvs["risk_cancer_per_micro_sv"] = RandomValue("Risk of Fatal Cancer per Micro Sv of Exposure",
                                              "Percentage/micro Sv",
                                              RandomNormal(1/12500000, 1/125000000),
                                              """Source: http://www.slideshare.net/fovak/health-effects-of-radiation-exposure-presentation (slide 76)
                                                 other documents also indicate that there is no safe level of exposure for fatal cancers
                                                 and that they seem to follow a mostly linear response.

                                                 uncertainty added by me

                                                 FWIW, 1 hour of flying is about 0.01mSv""")

# put your equations here

cvs["number_passengers_driving"]  = CalculatedValue("Number of passengers who actually choose to drive",
                                                    "Persons/Year",
                                                    "passenger_enplanements * percentage_passengers_driving")
cvs["number_new_driving_fatalities"] = CalculatedValue("Number of additional fatalities from new drivers",
                                                       "Persons/Year",
                                                       "number_passengers_driving * flight_distance * 2 * fatalities_mile",
                                                       "Flight distance multipled by two because people need to drive home")
cvs["cost_new_driving_fatalities"] = CalculatedValue("Expected code of a new driving fatalities in a year",
                                                     "Dollars/Year",
                                                     "number_new_driving_fatalities * value_human_life")

cvs["expected_nvpi_fatalities"] = CalculatedValue("Expected number of fatalities from Non-Violent Passenger Incidences in a Year",
                                                  "Persons/Year",
                                                  "risk_nvpi * passenger_enplanements")
cvs["cost_nvpi_fatalities"] = CalculatedValue("Expected cost of NVPI in a year",
                                              "Dollars/Year",
                                              "expected_nvpi_fatalities * value_human_life")

cvs["expected_vpi_fatalities"] = CalculatedValue("Expected number of fatalities from Violent Passenger Incidents in a year",
                                                 "Persons",
                                                 "risk_vpi * passenger_enplanements")
cvs["cost_vpi_fatalities"] = CalculatedValue("Expected cost of a VPI in a year",
                                             "Dollars/Year",
                                             "expected_vpi_fatalities * value_human_life")

cvs["expected_cancer_fatalities"] = CalculatedValue("Expected number of fatal cancers caused by scanning in a year",
                                                    "Persons/Year",
                                                    "passenger_enplanements * passenger_exposure_per_screening * percentage_ait_screening * percentage_ait_devices_backscatter * risk_cancer_per_micro_sv",
                                                    """In this case only a small percentage of individuals are actually
                                                       exposed to x-ray radiation through backscatter devices.  First
                                                       they need to be exposed to AIT, then they need to be exposed
                                                       backscatter""")

cvs["expected_ait_vpi_fatalities"] = CalculatedValue("Expected number of fatalities from Violent Passenger Incidences in a year with AIT",
                                                     "Persons/Year",
                                                     "risk_vpi * ( 1 - ait_success_rate ) * passenger_enplanements * percentage_ait_screening + risk_vpi * passenger_enplanements * ( 1 - percentage_ait_screening )",
                                                     """The official line is that for those airports without AIT screening,
                                                        nothing has changed.  I can confirm this based on my experiences at
                                                        HPN, LGA, and MSP (lanes without security) as of November 2010.""")

cvs["increase_ait_fatalities"] = CalculatedValue("Increase in fatalities as a result of AIT",
                                                 "Persons/Year",
                                                 "number_new_driving_fatalities + expected_cancer_fatalities - (expected_vpi_fatalities - expected_ait_vpi_fatalities)",
                                                 """As of right now this does not take into account the decrease in cancer from passengers
                                                    choosing not to fly or opting out.""")

cvs["net_cost_ait"] = CalculatedValue("Net cost of AIT devices",
                                      "Dollars/Year",
                                      "increase_ait_fatalities * value_human_life")


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
