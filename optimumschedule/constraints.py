"""
Classes to encapsulate various kinds of constraints.
"""

from abc import ABC
from abc import abstractmethod
from pulp import LpAffineExpression, LpConstraint


class Constraints(ABC):
    """
    The abstract base class to encapsulate a set of constraints.

    Subclasses must implement the ``get_constraints()`` method.
    """

    def __add__(self, problem):
        """
        Add the constraints to the problem.

        Parameters
        ----------
        problem : LpProblem
            The LpProblem object.

        Returns
        -------
        problem : LpProblem
            The LpProblem, with constraints added.
        """
        for constraint, name in self.get_constraints():
            const = LpConstraint(LpAffineExpression(constraint))
            problem.addConstraint(const, name)
        return problem

    @abstractmethod
    def get_constraints(self):
        """
        Yield the constraints
        """

class LaborCategoryTotalsConstraints(Constraints):
    """
    Objective to optimize the scheduled hours for a given person
    in a given labor category.

    .. math::
         [ \displaystyle\sum_{p}^{P} ( pos(X_{i, p}) ) <= 1 ] for i in N

    Parameters
    ----------
    x, y : LpVariables of shape (i_people, j_categories)
        The hours per person per position matrices to optimize.
    totals : pandas Series of shape (j_positions,)
        A vector of total hours per labor category.
    people : pandas Series of shape (i_people,)
        A vector of people.
    categories : pandas Series of shape (j_positions,)
        A vector of positions.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
    """

    def __init__(self,
                 x, y,
                 totals,
                 people,
                 categories,
                 **kwargs):
        self.x, self.y = x, y
        self.totals = totals
        self.people = people
        self.cats = categories

    def get_constraints(self):

        # constraint 1
        for j in self.cats:
            yield sum(self.x[i][j] for i in self.people) == self.totals.loc[j], f'x_const_{j}'

        # constraint 2    
        for j in self.cats:
            yield sum(self.y[i][j] for i in self.people) == self.totals.loc[j], f'y_const_{j}'
