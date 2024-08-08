import io
from contextlib import redirect_stdout
import clingo
from program_strings import ASPRING_PREFERENCE_STR
from asprin import asprin
from utils import parse_asprin_output


def solve(programs):
    ctl = clingo.Control()
    for program in programs:
        ctl.add("base", [], program)
    ctl.ground([("base", [])])
    ctl.configuration.solve.models = "0"
    res = ctl.solve()
    return res


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


def solve_return_all_models(programs):
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


def solve_with_asprin(programs):
    with open("tmp/asprin_program.lp", "w", encoding="utf-8") as f:
        f.write(ASPRING_PREFERENCE_STR)
        for p in programs:
            f.write(str(p))

    with io.StringIO() as buf, redirect_stdout(buf):
        try:
            asprin.main(["tmp/asprin_program.lp", "-n 0", "-q 1"])
        except SystemExit:
            pass
        output = buf.getvalue()
    optimum_solutions = parse_asprin_output(output)
    return optimum_solutions

