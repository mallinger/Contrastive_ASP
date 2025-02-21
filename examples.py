from grounder import ground
from program import Program


def ex0():
    prg = """crow :- bird, darkwings. bird :- feathers, beak, shape. magpie :- bird, whitewings. beak. shape. feathers. darkwings."""
    P = Program(prg)
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
                or "|" in rule
                or rule.startswith("node")
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
    prg = f"""{{ queen(1..{n}, 1..{n}) }} = {n}. 
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
    
    
    
def ex_coloring(n):
    prg = """b(X) | r(X) | g(X) :- node(X). 
        :- b(X), b(Y), edge(X, Y). 
        :- g(X), g(Y), edge(X, Y). 
        :- r(X), r(Y), edge(X, Y). """
    
    prg_facts = "" 
    for i in range(1, n + 1):
        prg_facts += f"node({i}). "
    for i in range(4, n-1):
        prg_facts += f"edge({i},{i+1}). "    
       
    prg_problem = "g(1). r(2). edge(1, 3). edge(2, 3)."   
       
    P = ground(prg + prg_facts + prg_problem)
    S = ground(prg + prg_facts)
    A = []
    I = ["b(3)"]
    E = ["b(3)"]
    F = ["g(3)"]
    return ((P, S, A), (I, E, F))

