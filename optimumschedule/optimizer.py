"""
Optimize the rate schedule.

author :: jeremy biggs
organization :: mathematica policy research
date :: 01-01-2021
"""

from gekko import GEKKO


class Optimizer:
    """
    Optimization class

    Parameters
    ----------
    objective : Objective subclass
        The objective function
    vars_dict : dict
        The variables dictionary
    vals_dict : dict, optional
        The values dictionary
        Default None
    constraints tuple of Constraints subclasses, optional
        A tuple of constraints
        Default ()
    solver : int, optional
        The solver to use
        Default 1
    solver_options : list, optional
        A list of options
        Default None
    verbose : bool, optional
        Whether to print results
        Default True
    """

    _DEFAULT_OPTIONS = ['minlp_maximum_iterations 5000',
                        'minlp_max_iter_with_int_sol 10',
                        'minlp_as_nlp 0',
                        'nlp_maximum_iterations 500',
                        'minlp_branch_method 1',
                        'minlp_integer_tol 0.05',
                        'minlp_gap_tol 0.01']

    def __init__(self,
                 objective,
                 vars_dict,
                 vals_dict=None, 
                 constraints=(),
                 solver=None,
                 solver_options=None,
                 verbose=True):

        self.obj = objective
        self.const = constraints
        self.vars_dict = vars_dict
        self.vals_dict = vals_dict
        self.verbose = verbose

        self.solver = solver
        self.solver_options = solver_options

        self._vars = None
        self._model = None
        self._result = None
        self._is_optimized = False

    @property
    def vars(self):
        return self._vars

    @property
    def model(self):
        return self._model

    @property
    def result(self):
        return self._result

    @property
    def is_optimized(self):
        return self._is_optimized

    def optimize(self):
        """
        Optimize the model.
        """
        m = GEKKO()

        # add the solver options
        m.options.SOLVER = 1 if self.solver is None else self.solver
        m.solver_options = (list(self._DEFAULT_OPTIONS) if self.solver_options is None
                            else self.solver_options)

        # create the variables
        for name, variable in self.vars_dict.items():
            shape, integer = variable
            self.vars_dict[name] =  m.Array(m.Var, shape, integer=integer)

        # combine the variables and values dictionaries
        kwargs = {**self.vars_dict, **self.vals_dict}

        # add the objective
        self.obj(**kwargs).add_objective(m)

        # add the constraints
        for con in self.const:
            con(**kwargs).add_constraints(m)

        # solve the problem
        m.solve()

        # save results
        self._vars = kwargs
        self._model = m
        self._result = m.options.OBJFCNVAL
        self._is_optimized = m.options.SOLVESTATUS == 1

        if self.verbose:
            print('Status:', self._is_optimized)
            print('Solution:', self._result)
