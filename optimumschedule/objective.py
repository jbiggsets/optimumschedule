"""
Classes to encapsulate various kinds of objective functions.
"""

from abc import ABC
from abc import abstractmethod


class Objective(ABC):
    """
    The abstract base class to encapsulate an objective function.

    Subclasses must implement the ``get_objective()`` method.
    """

    def __add__(self, problem):
        """
        Add the objective to the problem.

        Parameters
        ----------
        problem : LpProblem
            The LpProblem object.

        Returns
        -------
        problem : LpProblem
            The LpProblem, with objective added.
        """
        problem += self.get_objective()
        return problem

    @abstractmethod
    def get_objective(self):
        """
        The objective function.
        """


class ScheduledHoursObjective(Objective):
    """
    Objective to optimize the scheduled hours for a given person
    in a given labor category.

    Parameters
    ----------
    x, y : LpVariables of shape (i_people, j_categories)
        The hours per person per position matrices to optimize.
    wages : pandas Series of shape (i_people,)
        A vector of wages for each person.
    people : pandas Series of shape (i_people,)
        A vector of people.
    categories : pandas Series of shape (j_positions,)
        A vector of positions.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.

    .. math::
        \max [( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, j} \cdot C_{p} )  - 
              ( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, j} \cdot R_{i} )]

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`R_{i}` is the rate for person ``i``.
        - :math:`C_{p}` is the rate for position ``p``.
    """

    def __init__(self,
                 x, y,
                 wages,
                 people,
                 categories,
                 **kwargs):
        self.x, self.y = x, y
        self.wages = wages
        self.people = people
        self.cats = categories

    def get_objective(self):
        """
        Get the objective function.
        """
        obj = (sum(self.x[i][j] * self.wages.loc[i] for i in self.people for j in self.cats) -
               sum(self.y[i][j] * self.wages.loc[i] for i in self.people for j in self.cats))
        return obj, 'obj'
