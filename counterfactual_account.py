"""
Counterfactual Account Module

This modules generates counterfactual accounts for contrastive explanations.
"""

import logging
from program_strings import META_STR, COUNTERFACTUAL_STR, META_STR_ALL_LITERALS
from reification import manual_reify, reified_to_original_rules
from solver import solve_return_all_subset_maximal_models
from program import Rule, Program
from utils import remove_meta_atoms, remove_reification_atoms, clean_atom

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)


def counterfactual_accounts(
    explanation_frame,
    contrastive_explanation_problem,
    number_of_counterfactual_accounts,
):
    """
    Generate counterfactual accounts for a given explanation frame and
    contrastive explanation problem

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

    Returns
    -------
    list of tuples
        List of counterfactual accounts as tuples.


    Raises
    ------
    ValueError
        If the explanandum or foil is empty, not found in the program,
        or if the foil cannot be derived (unsatisfiable problem).
    """

    (P, S, A) = explanation_frame
    (I, E, F) = contrastive_explanation_problem

    if E == [""]:
        raise ValueError("Explanandum must not be empty.")
    if F == [""]:
        raise ValueError("Foil must not be empty.")

    for e in E:
        if not P.contains_atom(e):
            raise ValueError(f"Explanandum {e} does not appear in the program.")

    for f in F:
        if not P.contains_atom(f):
            raise ValueError(f"Foil {f} does not appear in the program.")

    A = set([clean_atom(a) for a in A])

    P_options = P - S
    assumptions = [
        f"assumption({assumption})."
        for assumption in A
        if assumption not in I and assumption.strip() != ""
    ]

    logger.debug("P: %s", P)
    logger.debug("A: %s", A)
    logger.debug("S: %s", S)
    logger.debug("P_options: %s", P_options)
    logger.info("Explanandum: %s", E)
    logger.info("Foil: %s", F)

    foil = []
    for f in F:
        foil.append(f"foil({f}).")

    explanandum = []
    for e in E:
        explanandum.append(f"explanandum({e}).")

    to_reify = Program(
        " ".join([str(r) for r in P.rules])
        + " "
        + " ".join(assumptions)
        + " "
        + " ".join(foil)
        + " "
        + " ".join(explanandum)
    )

    # reify
    logger.debug("Original Program to reify: %s", to_reify)
    meta_atoms = [Rule(r) for r in assumptions + foil + explanandum]
    reified = manual_reify(to_reify, S, meta_atoms)

    logger.debug("Original reified rules: %s\n", reified)
    logger.debug(
        "Original reified rules translated: %s\n", reified_to_original_rules(reified)
    )

    reified = " ".join(sorted([str(rule) for rule in reified.rules]))
    I_primes = solve_return_all_subset_maximal_models(
        [reified, META_STR, COUNTERFACTUAL_STR], number_of_counterfactual_accounts
    )

    if I_primes == "UNSAT":
        raise ValueError("Impossible to derive the foil.")
    counterfactual_models_all_literals = solve_return_all_subset_maximal_models(
        [reified, META_STR_ALL_LITERALS, COUNTERFACTUAL_STR],
        number_of_counterfactual_accounts,
    )

    I_primes = remove_meta_atoms(I_primes)
    I_primes = remove_reification_atoms(I_primes)
    CA = []
    for i, I_prime in enumerate(I_primes):
        counterfactual_model = counterfactual_models_all_literals[i]
        counterfactual_model_all_literals = ". ".join(counterfactual_model) + "."
        translated_counterfactual_rules = reified_to_original_rules(
            Program(counterfactual_model_all_literals)
        )

        logger.debug("I': %s", I_prime)
        logger.debug(
            "Counterfactual model with all literals: %s",
            counterfactual_model_all_literals,
        )
        logger.debug("Translated: %s", translated_counterfactual_rules)

        P_prime = P.intersection(translated_counterfactual_rules)
        A_prime = set(A).intersection(I_prime)
        CA.append((P_prime, I_prime, A_prime))

    return CA
