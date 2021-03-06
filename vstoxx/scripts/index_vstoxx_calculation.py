#
# Module to compute VSTOXX values
# given the values for the relevant sub-indexes
# as generated by the module index_subindex_calculation.py
#
# (c) The Python Quants GmbH
# Module for illustration purposes only.
# August 2014
#
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from index_date_functions import *


def calculate_vstoxx(path):
    ''' Function to calculate the VSTOXX volatility index given time series
    of the relevant sub-indexes.

    path: string
        string with path of data files
    '''
    # Constants
    seconds_year = 365 * 24 * 3600.
    seconds_30_days = 30 * 24 * 3600.

    data = pd.read_csv(path + 'vs.csv', index_col=0, parse_dates=True)
        # import historical VSTOXX data

    # Determine the settlement dates for the two underlying option series
    data["Settlement date 1"] = [first_settlement_day(a) for a in data.index]
    data["Settlement date 2"] = [second_settlement_day(a) for a in data.index]

    # Deduce the life time (in seconds) from current date to
    # final settlement Date
    data["Life time 1"] = [(data["Settlement date 1"][i] - i).days
                            * 24 * 60 * 60 for i in data.index]
    data["Life time 2"] = [(data["Settlement date 2"][i] - i).days
                            * 24 * 60 * 60 for i in data.index]

    data["Use V6I2"] = data["V6I1"].notnull()  # where V6I1 is not defined
    data["Subindex to use 1"] = [data["V6I1"][i] if data["Use V6I2"][i]
                        else data["V6I2"][i] for i in data.index]
                        # if V6I1 is defined, use V6I1 and V6I2 as data set
    data["Subindex to use 2"] = [data["V6I2"][i] if data["Use V6I2"][i]
                        else data["V6I3"][i] for i in data.index]
                        # else use V6I2 and V6I3

    #
    # The linear interpolation of the VSTOXX value
    # from the two relevant sub-indexes
    #
    data["Part 1"] = data["Life time 1"] / seconds_year \
                        * data["Subindex to use 1"] ** 2 \
                        * ((data["Life time 2"] - seconds_30_days)
                        / (data["Life time 2"] - data["Life time 1"]))

    data["Part 2"] = data["Life time 2"] / seconds_year \
                        * data["Subindex to use 2"] ** 2 \
                        *((seconds_30_days - data["Life time 1"])
                        / (data["Life time 2"] - data["Life time 1"])) \

    data["VSTOXX"] = np.sqrt((data["Part 1"] + data["Part 2"]) *
                        seconds_year / seconds_30_days)

    # Difference between original VSTOXX data and recalculated values
    data["Difference"] = data["V2TX"] - data["VSTOXX"]

    return data




