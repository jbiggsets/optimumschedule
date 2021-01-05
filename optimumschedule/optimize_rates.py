"""
Optimize the rate schedule.

author :: jeremy biggs
organization :: mathematica policy research
date :: 01-01-2021
"""
from argparse import ArgumentParser

import pandas as pd
from pulp import LpVariable

from .optimizer import Optimizer
from .objective import ScheduledHoursObjective
from .constraints import LaborCategoryTotals, OneCategoryPerPerson, Qualified


PEOPLE_COLS = frozenset({'person', 'category', 'hours_max', 'hours_min', 'wage'})
CATEGORY_COLS = frozenset({'category', 'hours_total'})


def unpack_frame(v, pers, cats):
    """
    Unpack the dataframe.

    Parameters
    ----------
    v : GEKKO.Array
        The GEKKO variable
    cats : list
        The categories
    pers : list
        The people

    Returns
    -------
    df : pandas DataFrame
        The unpacked dataframe
    """
    return pd.DataFrame({cat: {per: v[i, j].VALUE[0] for i, per in enumerate(pers)}
                         for j, cat in enumerate(cats)})


def preprocess_inputs(df, df_cats, df_quals):
    """
    Preprocess the input files.

    Parameters
    ----------
    df : pandas DataFrame
        The "person" dataframe
    df_cats : pandas DataFrame
        The "categories" dataframe
    df_quals : pandas DataFrame
        The "qualifications" data frame

    Returns
    -------
     df : pandas DataFrame
        The "person" dataframe, normalized
    df_cats : pandas DataFrame
        The "categories" dataframe, normalized
    df_quals : pandas DataFrame
        The "qualifications" data frame, normalized
    cats : list
        The categories
    pers : list
        The people
    """
    pers = df['person'].tolist()
    cats = df_quals.drop(columns='person').columns.tolist()

    df = df.set_index('person').copy()
    df_cats = df_cats.set_index('category').copy()
    df_quals = df_quals.set_index('person').copy()
    
    df_quals = df_quals.reindex(pers).copy()
    df_cats = df_cats.reindex(cats).copy()
    
    return df, df_cats, df_quals, pers, cats


def rate_scheduler(df,
                   df_cats,
                   df_quals,
                   verbose=True):
    """
    Optimize the rate schedule
    """

    # do some asseritions to make sure the frames are properly formatted
    # TODO :: Add some error messages if these fail
    assert all(col in df for col in PEOPLE_COLS)
    assert all(col in df_cats for col in CATEGORY_COLS)
    assert df['person'].is_unique
    assert df_cats['category'].is_unique
    assert df['person'].is_unique
    assert all(col in df_quals for col in df_cats['category'].unique())

    # set the indexes to `person` and `position`
    df, df_cats, df_quals, pers, cats = preprocess_inputs(df, df_cats, df_quals)

    # get the people and positions series
    people = df.index.to_series().reset_index(drop=True)
    categories = df_cats.index.to_series().reset_index(drop=True)

    # get the hours min and max, and the person category
    hours_max = df['hours_max'].copy()
    hours_min = df['hours_min'].copy()

    # get the totals and wages
    totals = df_cats['hours_total'].copy()
    wages = df['wage'].copy()
    n, p = len(pers), len(cats)

    # initialize the variables, x, y, b
    x, y, b = ((n, p), False), ((n, p), False), ((n, p), True)

    # collect the variables and parameters/constants
    vars_dict = dict(x=x, y=y, b=b)
    vals_dict = dict(people=pers,
                     categories=cats,
                     total=totals,
                     quals=df_quals,
                     minimum=hours_min,
                     maximum=hours_max,
                     wages=wages)

    # instantiate the optimizer
    optim = Optimizer(ScheduledHoursObjective,
                      vars_dict,
                      vals_dict,
                      constraints=(LaborCategoryTotals,
                                   OneCategoryPerPerson,
                                   Qualified,),
                      verbose=verbose)

    # solve the problem
    optim.optimize()

    # collect the frames
    df_x = unpack_frame(optim.vars['x'], people, categories)
    df_y = unpack_frame(optim.vars['y'], people, categories)
    df_b = unpack_frame(optim.vars['b'], people, categories)

    # return the results
    return {'actual_hours': (df_x * df_b), 'bidded_hours': (df_y * df_b)}

def main():

    parser = ArgumentParser('optimize_rates')
    parser.add_argument('filepath')
    parser.add_argument('outpath')
    args = parser.parse_args()

    df = pd.read_excel(args.filepath, sheet_name='person', engine='openpyxl')
    df_cats = pd.read_excel(args.filepath, sheet_name='position', engine='openpyxl')
    df_quals = pd.read_excel(args.filepath, sheet_name='qualification', engine='openpyxl')

    res = rate_scheduler(df, df_cats, df_quals)

    with pd.ExcelWriter(args.outpath, engine='xlsxwriter') as writer:
        for name, frame in res.items():
            frame.to_excel(writer, sheet_name=name)


if __name__ == '__main__':

    main()
