"""
Counterfactual Explanation Module

This module generates counterfactual explanations for contrastive explanations.
"""

import copy
from counterfactual_account import counterfactual_accounts
from utils import literals_to_define
from solver import solve_return_all_subset_minimal_models
from program import Program, Rule


def find_minimal_programs_to_derive(P, goals, P_prime, number_of_explanations):
    """
    Find minimal subset of rules that derive a given set of goal atoms, i.e. explanandum or foil.
    
    Parameters
    ----------
    P : Program
        The program from which to derive the goals.
    goals : list of str
        Either explanandum or foil
    P_prime : Program or None
        In case of Q1, these rules should be excluded first,
        for Q2 this input is None
    number_of_explanations : int
        Maximum number of minimal subset of rules to return.

    Returns
    -------
    list of Program
        List of minimal programs, each containing the smallest set of rules from P
        (and optionally P_prime) sufficient to derive the given goals.
    """
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
        + " ".join(f":- not {g}. " for g in goals)
        + " ".join([f"{{{a}}}." for a in actives_dict])
    )
    results = solve_return_all_subset_minimal_models([to_solve], number_of_explanations)
    programs = []
    for result in results:
        actives_chosen = [e for e in result if e.startswith("active")]
        programs.append(Program(set([rules_dict[ac] for ac in actives_chosen])))
    return programs


def counterfactual_explanations(
    explanation_frame,
    contrastive_explanation_problem,
    number_of_counterfactual_accounts,
    number_of_explanations,
):
    """
    Generate counterfactual explanations from a given explanation frame and 
    contrastive explanation problem.
    
    Parameters
    ----------
    explanation_frame : tuple
        Tuple (P, S, A) representing the original program (P), fixed knowledge (S),
        and assumptions (A).
    contrastive_explanation_problem : tuple
        Tuple (I, E, F) representing an answer set (I), the explanandum (E),
        and the foil (F).
    number_of_counterfactual_accounts : int
        Number of counterfactual accounts to generate.
    number_of_explanations : int
        Number of counterfactual explanations to return.

    Returns
    -------
    set of tuples
        A set of counterfactual explanations. 

    Raises
    ------
    ValueError
        If counterfactual account generation fails.
    """


    (P, S, A) = explanation_frame
    (I, E, F) = contrastive_explanation_problem
    try:
        CAs = counterfactual_accounts(
            explanation_frame,
            contrastive_explanation_problem,
            number_of_counterfactual_accounts,
        )
    except ValueError as error:
        raise error
    CFEs = []

    for P_prime, I_prime, A_prime in CAs:
        Q1s = find_minimal_programs_to_derive(P, E, P_prime, number_of_explanations)
        A_prime_program = Program(set([Rule(f"{a}.") for a in A_prime]))
        Q2s = find_minimal_programs_to_derive(
            P_prime + A_prime_program, F, None, number_of_explanations
        )
        Q_delta = P - P_prime
        for Q1 in set(Q1s):
            for Q2 in set(Q2s):
                CFEs.append((Q1, Q2, Q_delta))
    return set(CFEs)
