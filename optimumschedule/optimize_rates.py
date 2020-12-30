"""
"""
from argparse import ArgumentParser

import pandas as pd
from pulp import LpVariable

from .optimizer import Optimizer
from .objective import ScheduledHoursObjective
from .constraints import LaborCategoryTotalsConstraints


PEOPLE_COLS = frozenset({'person', 'category', 'hours_max', 'hours_min', 'wage'})
CATEGORY_COLS = frozenset({'category', 'hours_total'})


def unpack_frame(x, people, categories):
    return pd.DataFrame({j: {i: x[i][j].value() for i in people}
                         for j in categories})


def rate_scheduler(df,
                   df_cats,
                   lowerbound=0.0,
                   upperbound=2000.0,
                   verbose=True):

    # do some asseritions to make sure the frames are properly formatted
    # TODO :: Add some error messages if these fail
    assert all(col in df for col in PEOPLE_COLS)
    assert all(col in df_cats for col in CATEGORY_COLS)
    assert df['person'].is_unique
    assert df_cats['category'].is_unique

    # set the indexes to `person` and `position`
    df = df.set_index('person').copy()
    df_cats = df_cats.set_index('category').copy()

    # get the people and positions series
    people = df.index.to_series().reset_index(drop=True)
    categories = df_cats.index.to_series().reset_index(drop=True)

    # get the hours min and max, and the person category
    hours_max = df['hours_max'].copy()
    hours_min = df['hours_min'].copy()
    person_category = df['category'].copy()

    # get the totals and wages
    totals = df_cats['hours_total'].copy()
    wages = df['wage'].copy()

    # initialize the variables, `x` == actual; `y` == what we bid
    x = LpVariable.dicts('actual', (people, categories), lowBound=0.0, upBound=0.0)
    y = LpVariable.dicts('bidded', (people, categories), lowBound=0.0, upBound=0.0)
    
    # set the upper and lower bounds for each person/position
    for i in people:
        for j in categories:
            if person_category.loc[i] == j:
                upper, lower = float(hours_max.loc[i]), float(hours_min.loc[i])
                # make sure that we don't exceed the over bounds
                upper = upper if upper <= upperbound else upperbound
                lower = lower if lower >= lowerbound else lowerbound
                # set the bounds
                x[i][j].bounds(lower, upper)
                y[i][j].bounds(lower, upper)

    # collect the variables and parameters/constants
    vals = dict(x=x, y=y,
                people=people,
                categories=categories,
                totals=totals,
                wages=wages)

    # instantiate the optimizer
    optim = Optimizer('optimize_rate_schedule',
                      vals,
                      ScheduledHoursObjective,
                      constraints=(LaborCategoryTotalsConstraints,),
                      verbose=verbose)

    # solve the problem
    optim.optimize()

    # collect the frames
    df_x = unpack_frame(optim.vals_dict['x'], people, categories)
    df_y = unpack_frame(optim.vals_dict['y'], people, categories)

    # calculate averages rate (explicit and implicit)
    rates_x = df_x.apply(lambda x: x * wages[x.name], axis=1).sum(0) / df_x.sum(0)
    rates_y = df_y.apply(lambda x: x * wages[x.name], axis=1).sum(0) / df_y.sum(0)

    # add categories
    df_x['category'] = df_x.index.map(person_category)
    df_y['category'] = df_y.index.map(person_category)

    # add rates
    df_x['rate'] = df_x.category.map(rates_x)
    df_y['rate'] = df_y.category.map(rates_y)

    # add total
    df_x['total'] = df_x[categories].sum(1) * df_x['rate']
    df_y['total'] = df_y[categories].sum(1) * df_y['rate']
    
    print('Fee:')
    print((df_x['total'].sum() - df_y['total'].sum()) / df_y['total'].sum())

    return {'actual_hours': df_y, 'bidded_hours': df_x}

def main():
    parser = ArgumentParser('optimize_rates')
    parser.add_argument('people_file')
    parser.add_argument('categories_file')
    parser.add_argument('out_file')

    args = parser.parse_args()

    df = pd.read_csv(args.people_file)
    df_cats = pd.read_csv(args.categories_file)

    res = rate_scheduler(df, df_cats)

    with pd.ExcelWriter(args.out_file, engine='xlsxwriter') as writer:
        for name, frame in res.items():
            frame.to_excel(writer, sheet_name=name)


if __name__ == '__main__':

    main()
