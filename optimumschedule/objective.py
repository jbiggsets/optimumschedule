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


class RateProfitObjective(Objective):
    """
    Objective to optimize the scheduled hours for a given person in a given position.

    Parameters
    ----------
    variable : LpVariable of shape (i_people, p_positions)
        The matrix of hours per person per position to optimize.
    people : array-like of shape (i_people,)
        A vector of people.
    positions : array-like of shape (p_positions,)
        A vector of positions.
    people_rates : array-like of shape (i_people,)
        An array of rates for each person.
    position_rates : array-like of shape (p_positions,)
        An array of rates for each position.

    .. math::
        \max [( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, p} \cdot C_{p} )  - 
              ( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, p} \cdot R_{i} )]

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`R_{i}` is the rate for person ``i``.
        - :math:`C_{p}` is the rate for position ``p``.
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 people_rates,
                 position_rates,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions
        self.n_rates = people_rates
        self.p_rates = position_rates

    def get_objective(self):
        """
        Get the objective function.
        """
        return (sum([self.var[i][p] * self.p_rates[p]
                     for i in self.n_vec for p in self.p_vec]) - 
                sum([self.var[i][p] * self.n_rates[i]
                     for i in self.n_vec for p in self.p_vec])), 'obj'


class RateRevenueObjective(Objective):
    """
    Objective to optimize the scheduled hours for a given person in a given position.

    Parameters
    ----------
    variable : LpVariable of shape (i_people, p_positions)
        The matrix of hours per person per position to optimize.
    people : array-like of shape (i_people,)
        A vector of people.
    positions : array-like of shape (p_positions,)
        A vector of positions.
    people_rates : array-like of shape (i_people,)
        An array of rates for each person.

    .. math::
        \max [( \displaystyle\sum_{i}^{N} \sum_{p}^{P} X_{i, p} \cdot R_{i} )]

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`R_{i}` is the rate for person ``i``.
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 people_rates,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions
        self.n_rates = people_rates

    def get_objective(self):
        """
        Get the objective function.
        """
        return sum([self.var[i][p] * self.n_rates[i]
                    for i in self.n_vec for p in self.p_vec]), 'obj'

