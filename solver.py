import clingo


def solve_return_model(programs):
    ctl = clingo.Control()
    ctl.configuration.solve.models = 0
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


def solve_return_all_models(programs, subset_heuristic=False):
    if subset_heuristic:
        ctl = clingo.Control(
            ["--opt-mode=optN", "--heuristic=Domain", "--dom-mod=5,16",  "--enum-mod=domRec"])
    else:
        ctl = clingo.Control(["--opt-mode=optN"])
    ctl.configuration.solve.models = 0
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


def solve_return_all_model_subset_heuristics(programs, heuristic):
    if heuristic == "subset-minimal":
        programs.append("#heuristic rule(_,_). [1, false]")
        return solve_return_all_models(programs, True)
    else:
        programs.append("#heuristic rule(_,_). [1, true]")
        return solve_return_all_models(programs, True)                                            