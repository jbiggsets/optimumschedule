"""
Classes to encapsulate various kinds of objective functions.

author :: jeremy biggs
organization :: mathematica policy research
date :: 01-01-2021
"""

from abc import ABC
from abc import abstractmethod

from gekko import GEKKO


class Objective(ABC):
    """
    The abstract base class to encapsulate an objective function.

    Subclasses must implement the ``add_objective()`` method.
    """

    @abstractmethod
    def add_objective(self):
        """
        The objective function.
        """

class ScheduledHoursObjective(Objective):
    """
    Objective to optimize the scheduled hours for a given person
    in a given labor category.

    .. math::
        \max [( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, j} \cdot C_{p} )  - 
              ( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, j} \cdot R_{i} )]

    Parameters
    ----------
    x, y, b : GEKKO Arrays (i_people, j_categories)
        The hours per person per position matrices to optimize.
    wages : pandas Series of shape (i_people,)
        A vector of wages for each person.
    people : iterable of shape (i_people,)
        A vector of people.
    categories : iterable of shape (j_positions,)
        A vector of positions.
    """

    def __init__(self,
                 x, y, b,
                 wages,
                 people,
                 categories,
                 **kwargs):

        self.x, self.y, self.b = x, y, b
        self.wages = wages
        self.n = len(people)
        self.p = len(categories)

    def add_objective(self, m):
        """
        Get the objective function.
        """
        m.Maximize(m.sum([self.x[i, j] * self.b[i, j] * self.wages.iloc[i]
                          for j in range(self.p) for i in range(self.n)]))
        m.Minimize(m.sum([self.y[i, j] * self.b[i, j] * self.wages.iloc[i]
                          for j in range(self.p) for i in range(self.n)]))
