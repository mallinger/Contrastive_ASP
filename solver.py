"""
Solver Module

This module is used to apply clingo's framework to solve answer set programs

Includes functions to add subset maximal and subset minimal heuristics. 
"""


import clingo


def solve_return_model(programs):
    """
    Solve and return a single answer set of the given input programs with clingo.
    
    Parameters
    ----------
    programs : list of str
        The answer set programs to be solved together.
        
    Returns
    -------
    list of str or str
        If there is an answer set, it is returned as a list of strings representing the atoms
        with an additional space added after each comma for predicates with several arguments.
        If there is no answer set the string 'UNSAT' is returned.
    """
    ctl = clingo.Control()
    ctl.configuration.solve.models = 1
    for program in programs:
        ctl.add("base", [], program)
    ctl.ground([("base", [])])
    models = []
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            models.append(str(m))
        solveResult = handle.get()
    if solveResult.satisfiable:
        optimum = models[-1].split(" ")
        optimum = list(map(lambda l: l.replace(",", ", "), optimum))
        return optimum
    return "UNSAT"


def solve_return_all_models(programs, n, subset_heuristic=False):
    """
    Solve and return a maximum of 'n' optimal answer sets of the given input programs with clingo.
    
    Parameters
    ----------
    programs : list of str
        The answer set programs to be solved together.
    n : int
        Maximum number of models to compute.
    subset_heuristic : bool, optional
        If True, enables Clingo's domain-based subset heuristic by setting
        solver options:
        ``--heuristic=Domain``, ``--dom-mod=5,16``, ``--enum-mod=domRec``.
        If False (default), only ``--opt-mode=optN`` is used.
    
    Returns
    -------
    list of str or str
        If there are answer sets, they are returned as a list of lists of strings representing
        the answer sets with an additional space added after each comma for predicates with
        several arguments. If there is no answer set the string 'UNSAT' is returned.
    
    """
    if subset_heuristic:
        ctl = clingo.Control(
            ["--opt-mode=optN", "--heuristic=Domain", "--dom-mod=5,16",  "--enum-mod=domRec"])
    else:
        ctl = clingo.Control(["--opt-mode=optN"])
    ctl.configuration.solve.models = n
    for program in programs:
        ctl.add("base", [], program)
    ctl.ground([("base", [])])
    models = []
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            models.append((str(m), m.cost))
        solveResult = handle.get()
    if solveResult.satisfiable:
        lowest_cost = min(list(map(lambda l: l[1], models)))
        optima = [l[0].split(" ") for l in models if l[1] == lowest_cost]
        optima = [
            [literal.replace(",", ", ") for literal in optimum] for optimum in optima
        ]
        return optima
    return "UNSAT"


def solve_return_all_subset_maximal_models(programs, n):
    """
    Solve and return a maximum of 'n' optimal answer sets of the given input programs with clingo.
    Only subset maximal answer sets in regard to the predicate "rule/2" are returned.  
    """
    programs.append("#heuristic rule(_,_). [1, true]")
    return solve_return_all_models(programs, n, True)

def solve_return_all_subset_minimal_models(programs, n):
    """
    Solve and return a maximum of 'n' optimal answer sets of the given input programs with clingo.
    Only subset minimal answer sets in regard to the predicates "active_P_prime/1" and
    "active" are returned. Minimizing "active_P_prime/1" has a higher priority.
    """
    programs.append("#heuristic active_P_prime(_). [2, false]")
    programs.append("#heuristic active(_). [1, false]")
    return solve_return_all_models(programs, n, True)
