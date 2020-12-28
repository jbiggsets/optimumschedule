"""
"""
from argparse import Namespace

import pandas as pd

from .utils import _collect_schedule
from .objective import RateProfitObjective
from .constraints import (OnePersonPerPositionConstraints,
                          HoursPerPersonPerPositionConstraints,
                          HoursPerPositionConstraints)


def rate_scheduler(roster,
                   position,
                   quals,
                   hours_min=0.0,
                   hours_max=2000.0):

    roster = roster.set_index('name')
    position = position.set_index('position')
    if quals is None:
        quals = pd.DataFrame(1,
                             index=roster.index.unique(),
                             columns=position.index.unique())
    else:
        quals = quals.set_index('name')

    # the hours variable
    X = LpVariable.dicts('X', (quals.index.tolist(),
                               quals.columns.tolist()),
                               lowBound=hours_min,
                               upBound=hours_max)

    vals = dict(X=X,
                N=roster.index.tolist(),
                P=position.index.tolist(),
                Q=quals,
                R_rate=roster['rate'],
                C_rate=position['rate'],
                H_hours=position['hours'])

    optim = Optimizer(vals,
                      RateProfitObjective,
                      const=(OnePersonPerPositionConstraints,
                             HoursPerPersonPerPositionConstraints,
                             HoursPerPositionConstraints))

    optim.optimize()

    return _collect_schedule(val)
