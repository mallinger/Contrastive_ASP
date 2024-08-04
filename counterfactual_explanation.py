import copy
from counterfactual_account import counterfactual_accounts
from utils import literals_to_define
from solver import solve_return_all_models
from program import Program, Rule


def find_minimal_programs_to_derive(P, E, P_prime):
    to_define = literals_to_define(P.rules)
    actives_dict = {}
    rules_dict = {}

    if P_prime is not None:
        P = P - P_prime
    for i, r in enumerate(P.rules):
        s = copy.deepcopy(r)
        s.add_literal(f"active({i})")
        actives_dict[f"active({i})"] = s
        rules_dict[f"active({i})"] = r

    if P_prime is not None:
        for i, r in enumerate(P_prime.rules):
            j = i + len(P.rules)
            s = copy.deepcopy(r)
            s.add_literal(f"active_P_prime({j})")
            actives_dict[f"active_P_prime({j})"] = s
            rules_dict[f"active_P_prime({j})"] = r

    to_solve = (
        " ".join([f"#defined {atom}." for atom in to_define])
        + " ".join([str(s) for s in actives_dict.values()])
        + f":- not {E[0]}. "
        + ":~ X = #count{N : active(N) }. [X@1] "
        + " ".join([f"{{{a}}}." for a in actives_dict.keys()])
    )
    if P_prime is not None:
        to_solve += ":~ X = #count{N : active_P_prime(N) }. [X@2] "

    results = solve_return_all_models([to_solve])
    programs = []
    for result in results:
        actives_chosen = [e for e in result if e.startswith("active")]
        programs.append(Program(set([rules_dict[ac] for ac in actives_chosen])))
    return programs


def counterfactual_explanations(explanation_frame, contrastive_explanation_problem):
    (P, S, A) = explanation_frame
    (I, E, F) = contrastive_explanation_problem
    CAs = counterfactual_accounts(explanation_frame, contrastive_explanation_problem)
    CFEs = []
    for P_prime, I_prime, A_prime in CAs:

        Q_delta = P - P_prime
        Q1 = find_minimal_programs_to_derive(P, E, P_prime)[0]

        A_prime_program = Program(set([Rule(f"{a}.") for a in A_prime]))
        Q2 = find_minimal_programs_to_derive(P_prime + A_prime_program, F, None)[0]

        CFEs.append((Q1, Q2, Q_delta))
    return CFEs
