"""
Example Module

This module provides several examples for contrastive explanations
in form of explanation frames and contrastive explanation problems.

In case of the coloring example, this module also provide auxiliary
functions to set up testing.
"""


from math import sqrt
from grounder import ground
from program import Program

def ex0():
    prg = """crow :- bird, darkwings. bird :- feathers, beak, shape.
    magpie :- bird, whitewings. beak. shape. feathers. darkwings."""
    P = Program(prg)
    S = Program(
        """crow :- bird, darkwings. magpie :- bird, whitewings. 
        bird :- feathers, beak, shape. shape. beak. feathers."""
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
    prg = """
    b(X) | r(X) | g(X) :- node(X). 
    :- b(X), b(Y), edge(X, Y).
    :- g(X), g(Y), edge(X, Y). 
    :- r(X), r(Y), edge(X, Y).
    node(one). node(two). node(three). 
    g(one). r(two). 
    edge(one, three). edge(two, three).
    """
    prg = ground(prg)
    prg_S = list(
        map(
            lambda r: r + ".",
            [
                rule
                for rule in str(prg)[:-1].split(". ")
                if rule.startswith(" :-") or "|" in rule or rule.startswith("node")
            ],
        )
    )
    P = prg
    S = Program(" ".join(set(prg_S)))
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


def ex_nqueens(n):
    prg = f"""{{ queen(1..{n}, 1..{n}) }} == {n}.
    :- queen(I,J), queen(I,JJ), J != JJ. 
    :- queen(I,J), queen(II,J), I != II. 
    :- queen(I,J), queen(II,JJ), (I,J) != (II,JJ), I-J == II-JJ. 
    :- queen(I,J), queen(II,JJ), (I,J) != (II,JJ), I+J == II+JJ. """

    P = ground(prg + "queen(1, 2).")
    S = ground(prg)
    A = []
    I = [""]
    E = ["queen(2, 4)"]
    F = ["queen(1, 3)"]
    return ((P, S, A), (I, E, F))

def ex_coloring(n, i):
    prg_rules = """b(X) | r(X) | g(X) | y(X) | c(X) :- node(X).
    :- b(X), b(Y), link(X, Y). 
    :- g(X), g(Y), link(X, Y). 
    :- y(X), y(Y), link(X, Y). 
    :- c(X), c(Y), link(X, Y). 
    :- r(X), r(Y), link(X, Y).
     """

    with open(f"coloring_graphs/{n}.txt", "r", encoding="UTF-8") as f:
        prg_graph = "".join(f.readlines())

    with open(f"coloring_graphs/{n}_solution.txt", "r", encoding="UTF-8") as f:
        prg_coloring = " ".join([f"{atom.strip()}." for atom in f.readlines()])

    P = ground(prg_rules + prg_graph + prg_coloring)

    S = ground(prg_rules + prg_graph)
    chosen_node = [node for node in prg_coloring.split(" ") if f"({i})." in node][0][
        :-1
    ]
    color_chosen_node = chosen_node[0]

    A = []
    I = prg_coloring[:-1].split(". ")
    E = [chosen_node]
    F = [f"g({i})"] if color_chosen_node == "b" else [f"b({i})"]
    return ((P, S, A), (I, E, F))


def solve_coloring():
    from solver import solve_return_model

    prg_rules = """b(X) | r(X) | g(X) | y(X) | c(X) :- node(X).
    :- b(X), b(Y), link(X, Y). 
    :- g(X), g(Y), link(X, Y). 
    :- y(X), y(Y), link(X, Y). 
    :- c(X), c(Y), link(X, Y). 
    :- r(X), r(Y), link(X, Y).
    """
    for n in range(130, 140, 5):
        with open(f"coloring_graphs/{n}.txt", "r", encoding="UTF-8") as f:
            solution_atoms = solve_return_model([prg_rules, "".join(f.readlines())])
            filtered_atoms = [
                atom
                for atom in solution_atoms
                if "node" not in atom and "link" not in atom
            ]
            with open(f"coloring_graphs/{n}_solution.txt", "w", encoding="UTF-8") as f2:
                for atom in filtered_atoms:
                    f2.write(f"{atom}\n")


def create_graphs():
    for i in range(10, 155, 5):
        with open("coloring_graphs/150.txt", "r", encoding="UTF-8") as f:
            lines = [l.strip() for l in f.readlines()]
            lines = [
                l for l in lines if not any(str(n) in l for n in range(i + 1, 151))
            ]
            with open(f"coloring_graphs/{i}.txt", "w", encoding="UTF-8") as f2:
                for l in lines:
                    f2.write(f"{l}\n")


def ex_sudoku(n):
    sudo = f"""
    x(1..{n}).
    y(1..{n}).
    n(1..{n}).
    :- sudoku(X,Y,N), sudoku(A,Y,N), X != A. 
    :- sudoku(X,Y,N), sudoku(X,B,N), Y != B. 
    :- sudoku(X,Y,V), sudoku(A,B,V), subgrid(X,Y,A,B), X != A, Y != B. 
    subgrid(X,Y,A,B) :- x(X), x(A), y(Y), y(B),(X-1)/Sqrt_n == (A-1)/Sqrt_n, (Y-1)/Sqrt_n == (B-1)/Sqrt_n, Sqrt_n * Sqrt_n == n. 
    """
    sudo += " | ".join([f"sudoku(X,Y,{N})" for N in range(1, n + 1)]) + ":- x(X), y(Y)."

    P = ground(sudo + " sudoku(1,1,1).")
    S = ground(sudo)
    A = []
    I = ["sudoku(1,1,1)", "sudoku(1,2,2)"]
    E = ["sudoku(1,2,2)"]
    F = ["sudoku(1,2,1)"]
    return ((P, S, A), (I, E, F))


def ex_sudoku_simplified(n):
    sudo = f"""
    x(1..{n}).
    y(1..{n}).
    n(1..{n}).
    :- sudoku(X,Y,N), sudoku(A,Y,N), X != A. 
    :- sudoku(X,Y,N), sudoku(X,B,N), Y != B. 
    """
    sudo += " | ".join([f"sudoku(X,Y,{N})" for N in range(1, n + 1)]) + ":- x(X), y(Y)."

    subgrids = ""
    for x in range(1, n + 1):
        for y in range(1, n + 1):
            for a in range(1, n + 1):
                for b in range(1, n + 1):
                    if (
                        int((x - 1) / sqrt(n)) == int((a - 1) / sqrt(n))
                        and int((y - 1) / sqrt(n)) == int((b - 1) / sqrt(n))
                        and x != a
                        and y != b
                    ):
                        for v in range(1, n + 1):
                            subgrids += f" :- sudoku({x},{y},{v}), sudoku({a},{b},{v})."
    sudo += " " + subgrids
    P = ground(sudo + " sudoku(1,1,1).")
    S = ground(sudo)
    A = []
    I = ["sudoku(1,1,1)", "sudoku(1,2,2)"]
    E = ["sudoku(1,2,2)"]
    F = ["sudoku(1,2,1)"]
    return ((P, S, A), (I, E, F))
