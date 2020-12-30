"""
Optimize the rate schedule
"""
from pulp import (LpProblem,
                  LpMinimize,
                  LpMaximize,
                  LpStatus,
                  value as obj_value)


class Optimizer:
    """
    Optimization class
    """

    def __init__(self,
                 name,
                 values_dict, 
                 objective,
                 constraints=None,
                 maximize=True,
                 verbose=True):

        self.obj = objective
        self.const = constraints
        self.vals_dict = values_dict

        self.maximize = maximize

        self.name = name
        self.verbose = verbose

        self.problem = None
        self.is_optimized = False

    def optimize(self):
        """
        Optimize the model.
        """
        # initialize up the problem
        problem = LpProblem(self.name, LpMaximize if self.maximize else LpMinimize)
        # add the objective
        problem = self.obj(**self.vals_dict) + problem
        # add the constraints
        if self.const is not None:
            for con in self.const:
                problem = con(**self.vals_dict) + problem

        # solve the problem
        problem.solve()

        if self.verbose:
            print('Status:', LpStatus[problem.status])
            print('Solution:', obj_value(problem.objective))

        # save results
        self.problem = problem
        self.is_optimized = problem.status == 1
