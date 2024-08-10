from grounder import ground
from program import Program


def ex0():
    prg = """crow :- bird, darkwings. bird :- feathers, beak, shape. magpie :- bird, whitewings. beak. shape. feathers. darkwings."""
    P = Program(prg)
    # S = Program("")
    S = Program(
        "crow :- bird, darkwings. magpie :- bird, whitewings. bird :- feathers, beak, shape. shape. beak. feathers."
    )
    A = ["whitewings"]
    I = ["crow", "bird", "feathers", "beak", "shape", "darkwings"]
    E = ["crow"]
    F = ["magpie"]
    return ((P, S, A), (I, E, F))


def ex1():
    prg = "a :- not b. b :- c."
    P = Program(prg)
    S = Program("")
    A = ["c", "d"]
    I = ["a"]
    E = ["a"]
    F = ["b"]
    return ((P, S, A), (I, E, F))


def ex2():
    prg = "a | b.  b :- a."
    P = Program(prg)
    S = Program("")
    A = []
    I = ["b"]
    E = ["b"]
    F = ["a"]
    return ((P, S, A), (I, E, F))


def ex3():
    prg = "a :- c. a :- d. b :- e. c. d."
    P = Program(prg)
    S = Program("")
    A = ["e"]
    I = ["a", "c", "d"]
    E = ["a"]
    F = ["b"]
    return ((P, S, A), (I, E, F))


def ex4():
    prg = "man(d). husband(X) :- man(X), not single(X). single(X) :- man(X), not husband(X)."
    P = ground(prg)
    S = Program("man(d).")
    A = [""]
    I = ["single(d)", "man(d)"]
    E = ["single(d)"]
    F = ["husband(d)"]
    return ((P, S, A), (I, E, F))


def ex5():
    prg = """b(X) | r(X) | g(X) :- node(X). :- b(X), b(Y), edge(X, Y). :- g(X), g(Y), edge(X, Y). :- r(X), r(Y), edge(X, Y). node(one). node(two). node(three). g(one). r(two). edge(one, three). edge(two, three)."""
    prg = ground(prg)
    prg_S = list(
        map(
            lambda r: r + ".",
            [
                rule
                for rule in str(prg)[:-1].split(". ")
                if rule.startswith(" :-")
                or rule.startswith("b(")
                or rule.startswith("node")
            ],
        )
    )
    P = prg
    S = Program("".join(set(prg_S)))
    A = []
    I = ["b(three)"]
    E = ["b(three)"]
    F = ["g(three)"]
    return ((P, S, A), (I, E, F))


def ex6():
    facts = ". ".join([f"fact{i}" for i in range(100)]) + "."
    prg = (
        "nogood :- nogood_condition. good :- not nogood_condition. nogood_condition. "
        + facts
    )
    P = ground(prg)
    S = Program("nogood :- nogood_condition. good :- not nogood_condition. " + facts)
    A = []
    I = [""]
    E = ["nogood"]
    F = ["good"]
    return ((P, S, A), (I, E, F))
