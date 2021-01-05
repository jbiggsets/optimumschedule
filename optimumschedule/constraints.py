"""
Classes to encapsulate various kinds of constraints.

author :: jeremy biggs
organization :: mathematica policy research
date :: 01-01-2021
"""

from abc import ABC
from abc import abstractmethod

from gekko import GEKKO


class Constraints(ABC):
    """
    The abstract base class to encapsulate a set of constraints.

    Subclasses must implement the ``add_constraints()`` method.
    """

    @abstractmethod
    def add_constraints(self, m):
        """
        Add the constraints
        """

class LaborCategoryTotals(Constraints):
    """
    Make sure the hours are met for each labor category.

    .. math::
         [ \displaystyle\sum_{i}^{N} ( X_{i, p} * B_{i, p} ) <= total[j] ] for j in P
         [ \displaystyle\sum_{i}^{N} ( Y_{i, p} * B_{i, p} ) <= total[j] ] for j in P

    Parameters
    ----------
    x, y, b : GEKKO Arrays (i_people, j_categories)
        The hours per person per position matrices to optimize.
    total : pandas Series of shape (j_positions,)
        A vector of total hours per labor category.
    people : iterable of shape (i_people,)
        A vector of people.
    categories : iterable of shape (j_positions,)
        A vector of positions.
    """

    def __init__(self,
                 x, y, b,
                 total,
                 people,
                 categories,
                 **kwargs):

        self.x, self.y, self.b = x, y, b
        self.total = total
        self.n = len(people)
        self.cats = categories

    def add_constraints(self, m):
        """
        Add the constraints
        """
        for j, cat in enumerate(self.cats):
            m.Equation(sum([self.x[i, j] * self.b[i, j] for i in range(self.n)]) == self.total.loc[cat])
            m.Equation(sum([self.y[i, j] * self.b[i, j] for i in range(self.n)]) == self.total.loc[cat])


class OneCategoryPerPerson(Constraints):
    """
    Make sure each person is in only one labor category.

    .. math::
         [ \displaystyle\sum_{p}^{P} ( B_{i, p} ) <= 1 ] for i in N

    Parameters
    ----------
    b : GEKKO Arrays (i_people, j_categories)
        The hours per person per position matrices to optimize.
    people : iterable of shape (i_people,)
        A vector of people.
    categories : iterable of shape (j_positions,)
        A vector of positions.
    """

    def __init__(self,
                 b,
                 people,
                 categories,
                 **kwargs):

        self.b = b
        self.n = len(people)
        self.p = len(categories)

    def add_constraints(self, m):
        """
        Add the constraints
        """
        # constraint 1
        for i in range(self.n):
            m.Equation(sum([self.b[i, j] for j in range(self.p)]) <= 1)


class Qualified(Constraints):
    """
    Make sure the hours are met for each labor category.

    .. math::
         [ \displaystyle\sum_{i}^{N} ( X_{i, p} * B_{i, p} ) <= total[j] ] for j in P
         [ \displaystyle\sum_{i}^{N} ( Y_{i, p} * B_{i, p} ) <= total[j] ] for j in P

    Parameters
    ----------
    x, y, b : GEKKO Arrays (i_people, j_categories)
        The hours per person per position matrices to optimize.
    quals : pandas DataFrame of shape (j_positions,)
        A matrix of qualifications.
    people : iterable of shape (i_people,)
        A vector of people.
    categories : iterable of shape (j_positions,)
        A vector of positions.
    minimum : pandas Series
        A vector of minimum hours
    maximum : pandas Series
        A vector of maximum hours
    """

    def __init__(self,
                 x, y, b,
                 quals,
                 people,
                 categories,
                 minimum,
                 maximum,
                 **kwargs):

        self.x, self.y, self.b = x, y, b
        self.quals = quals
        self.pers = people
        self.cats = categories
        self.min = minimum
        self.max = maximum

    def set_variable(self, v, integer=False):
        """
        Set the variable values
        """
        for i, per  in enumerate(self.pers):
            for j, cat in enumerate(self.cats):
                if self.quals.loc[per, cat] == 1:
                    v[i, j].value = self.min.loc[per] if not integer else 0
                    v[i, j].lower = self.min.loc[per] if not integer else 0
                    v[i, j].upper = self.max.loc[per] if not integer else 1
                else:
                    v[i, j].value = 0
                    v[i, j].lower = 0
                    v[i, j].upper = 0

    def add_constraints(self, m):
        """
        Add the constraints
        """
        self.set_variable(self.x)
        self.set_variable(self.y)
        self.set_variable(self.b, integer=True)
