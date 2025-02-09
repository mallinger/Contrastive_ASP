import logging
from program_strings import META_STR, COUNTERFACTUAL_STR, META_STR_ALL_LITERALS
from reification import manual_reify, reified_to_original_rules
from solver import solve_return_all_model_subset_heuristics
from program import Rule, Program
from utils import remove_meta_atoms

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)


def counterfactual_accounts(EF, CEP, number_of_counterfactual_accounts):
    (P, S, A) = EF
    (I, E, F) = CEP

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

    P_options = P - S
    assumptions = [
        f"assumption({assumption})."
        for assumption in A
        if assumption not in I and assumption.strip() != ""
    ]

    logger.info("P: %s", P)
    logger.info("A: %s", A)
    logger.info("S: %s", S)
    logger.info("P_options: %s", P_options)
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
    logger.info("Original Program to reify: %s", to_reify)
    meta_atoms = [Rule(r) for r in assumptions + foil + explanandum]
    reified = manual_reify(to_reify, S, meta_atoms)

    logger.debug("Original reified rules: %s\n", reified)
    logger.info(
        "Original reified rules translated: %s\n", reified_to_original_rules(reified)
    )

    I_primes = solve_return_all_model_subset_heuristics(
        [str(reified), META_STR, COUNTERFACTUAL_STR], "subset-maximal", number_of_counterfactual_accounts
    )

    if I_primes == "UNSAT":
        raise ValueError("Impossible to derive the foil.")
    counterfactual_models_all_literals = solve_return_all_model_subset_heuristics(
        [str(reified), META_STR_ALL_LITERALS, COUNTERFACTUAL_STR], "subset-maximal", number_of_counterfactual_accounts
    )

    I_primes = remove_meta_atoms(I_primes)
    CA = []
    for i, I_prime in enumerate(I_primes):
        counterfactual_model = counterfactual_models_all_literals[i]
        counterfactual_model_all_literals = ". ".join(counterfactual_model) + "."
        translated_counterfactual_rules = reified_to_original_rules(
            Program(counterfactual_model_all_literals)
        )

        logger.info("I': %s", I_prime)
        logger.debug(
            "Counterfactual model with all literals: %s",
            counterfactual_model_all_literals,
        )
        logger.info("Translated: %s", translated_counterfactual_rules)

        P_prime = P.intersection(translated_counterfactual_rules)
        A_prime = set(A).intersection(I_prime)
        CA.append((P_prime, I_prime, A_prime))

    return CA
