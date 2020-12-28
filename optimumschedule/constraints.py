"""
Classes to encapsulate various kinds of constraints.
"""

from abc import ABC
from abc import abstractmethod


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
        for constraint in self.get_constraints():
            problem += constraint
        return problem

    @abstractmethod
    def get_constraints(self):
        """
        Yield the constraints
        """


class OnePersonPerPositionConstraints(Constraints):
    """
    Constraint ensure that each person is assigned to only one position.

    .. math::
         [ \displaystyle\sum_{p}^{P} ( pos(X_{i, p}) ) <= 1 ] for i in N

    Parameters
    ----------
    variable : LpVariable of shape (i_people, p_positions)
        The matrix of hours per person per position to optimize.
    people : array-like of shape (i_people,)
        A vector of people.
    positions : array-like of shape (p_positions,)
        A vector of positions.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions

    def get_constraints(self):
        """
        Yield the constraints
        """
        for i in self.n_vec:
            yield sum(self.var[i][p].positive() for p in self.p_vec) <= 1, f"only_one_{i}"


class HoursPerPersonPerPositionConstraints(Constraints):
    """
    Constraint to set minimum and maximum hours for each person and position.

    .. math::
         [ X_{i, p} >= npmin_{i, p} ] \text{ for p in P for i in N }

    .. math::
         [ X_{i, p} >= npmax_{i, p} ] \text{ for p in P for i in N }

    Parameters
    ----------
    variable : LpVariable of shape (i_people, p_positions)
        The matrix of hours per person per position to optimize.
    people : array-like of shape (i_people,)
        A vector of people.
    positions : array-like of shape (p_positions,)
        A vector of positions.
    min_hours_per_person_per_position : array-like of shape (i_people, p_positions) or None, default=None
        The minimum number of hours per person.
    max_hours_per_person_per_position : array-like of shape (i_people, p_positions) or None, default=None
        The maximum number of hours per person.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`np_min_{i, p}` ...
        - :math:`np_max_{i, p}` ...
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 min_hours_per_person_per_position=None,
                 max_hours_per_person_per_position=None,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions
        self.np_min = min_hours_per_person_per_position
        self.np_max = max_hours_per_person_per_position

    def get_constraints(self):
        """
        Yield the constraints
        """
        if self.np_min is not None:
            for i in self.n_vec:
                for p in self.p_vec:
                    yield self.var[i][p] >= self.np_min[i, p], f"min_for_{i},{p}"

        if self.np_max is not None:
            for i in self.n_vec:
                for p in self.p_vec:
                    yield self.var[i][p] <= self.np_max[i, p], f"max_for_{i},{p}"


class HoursPerPositionConstraints(Constraints):
    """
    Constraint to set minimum and maximum hours for each person and position.

    .. math::
         [ \displaystyle\sum_{p}^{P} ( X_{i, p} ) >= pmin_{p} ] for i in N

    .. math::
         [ \displaystyle\sum_{p}^{P} ( X_{i, p} ) >= pmax_{p} ] for i in N

    Parameters
    ----------
    variable : LpVariable of shape (i_people, p_positions)
        The matrix of hours per person per position to optimize.
    people : array-like of shape (i_people,)
        A vector of people.
    positions : array-like of shape (p_positions,)
        A vector of positions.
    min_hours_per_person : array-like of shape (i_people,) or None, default=None
        The minimum number of hours per person.
    max_hours_per_person : array-like of shape (i_people,) or None, default=None
        The maximum number of hours per person.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`pmin_{p}` ...
        - :math:`pmax_{p}` ...
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 min_hours_per_position=None,
                 max_hours_per_position=None,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions
        self.p_min = min_hours_per_position
        self.p_max = max_hours_per_position

    def get_constraints(self):
        """
        Yield the constraints
        """
        if self.p_min is not None:
            for p in self.p_vec:
                yield sum(self.var[i][p] for i in self.n_vec) >= self.p_min[p], f"min_for_{p}"

        if self.p_max is not None:
            for p in self.p_vec:
                yield sum(self.var[i][p] for i in self.n_vec) <= self.p_max[p], f"max_for_{p}"

class RatePerPositionConstraints(Constraints):
    """
    Constraint to set minimum and maximum hours for each person and position.

    .. math::
         [ \displaystyle\sum_{i}^{N} ( X_{i, p} ) >= pmin_{p} ] for p in P

    .. math::
         [ \displaystyle\sum_{i}^{N} ( X_{i, p} ) >= pmax_{p} ] for p in P

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
    min_hours_per_person : array-like of shape (i_people,) or None, default=None
        The minimum number of hours per person.
    max_hours_per_person : array-like of shape (i_people,) or None, default=None
        The maximum number of hours per person.

    Notes
    -----
        - :math:`X_{i, p}` is scheduled hours for person ``i`` in position ``p``.
        - :math:`N` is the number of people.
        - :math:`P` is the number of positions.
        - :math:`pmin_{p}` ...
        - :math:`pmax_{p}` ...
    """

    def __init__(self,
                 variable,
                 people,
                 positions,
                 people_rates,
                 min_rate_per_position=None,
                 max_rate_per_position=None,
                 **kwargs):
        self.var = variable
        self.n_vec = people
        self.p_vec = positions
        self.n_rates = people_rates
        self.p_min = min_rate_per_position
        self.p_max = max_rate_per_position

    def get_constraints(self):
        """
        Yield the constraints
        """
        if self.p_max is not None:
            for p in p_vec:
                yield (sum(self.var[i, p].positive() for i in self.n_vec) * self.p_max[p] >= 
                       sum(self.var[i, p] * self.n_rates[i] for i in N), f"max_rate_for_{p}")

        if self.p_min is not None:
            for p in p_vec:
                yield (sum(self.var[i, p].positive() for i in self.n_vec) * self.p_min[p] <= 
                       sum(self.var[i, p] * self.n_rates[i] for i in N), f"min_rate_for_{p}")
