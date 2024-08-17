import logging
from program_strings import META_STR, COUNTERFACTUAL_STR, META_STR_ALL_LITERALS, FILTER_RULES_STR
from reification import optional_rule_to_reified, manual_reify, reified_to_original_rules
from solver import solve_return_model, solve_return_all_model_subset_heuristics
from program import Rule, Program
from utils import remove_optional_support_literals

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.CRITICAL)


def add_optional_rules(reified, P_options):
    # optional rules in reified form
    reified_optional_rules = Program("")
    for i, optional_rule in enumerate(P_options.rules):
        reified_optional_rules.add_program(
            optional_rule_to_reified(optional_rule, i))
    logger.debug("Optional rules self reified: %s\n", reified_optional_rules)

    # combining original and optional rules
    reified.add_program(reified_optional_rules)
    logger.debug(
        "Reified original and self reified optional rules: %s\n", reified)

    model = solve_return_model([str(reified), FILTER_RULES_STR])
    logger.debug(
        "Model of whole reified rules with optional_rule predicate: %s\n", model)
    # logger.debug(f"Model translated: {reified_to_original_rules('. '.join(model))}")
    optional_rule_literals = list(
        filter(lambda r: r.startswith("optional_rule"), model))
    logger.debug("Optional Rules of optional_rule predicate: %s",
                 optional_rule_literals)

    # mark optional rules as such
    for optional_rule_literal in optional_rule_literals:
        rule = Rule(optional_rule_literal.replace("optional_", "") + ".")
        reified.fact_to_choice(rule)

    remove_optional_support_literals(reified)
    return reified


def counterfactual_accounts(EF, CEP):
    (P, S, A) = EF
    (I, E, F) = CEP
    P_options = P - S
    assumptions = [
        f"assumption({assumption})." for assumption in A if assumption not in I
    ]

    logger.info("P: %s", P)
    logger.info("A: %s", A)
    logger.info("S: %s", S)
    logger.info("P_options: %s", P_options)
    logger.info("Explanandum: %s", E)
    logger.info("Foil: %s", F)

    foil = ""
    for f in F:
        foil += f"foil({f})."

    explanandum = ""
    for e in E:
        explanandum += f"explanandum({e})."

    to_reify = Program(
        " ".join([str(s) for s in S.rules]) + " "
        + " ".join([str(s) for s in P_options.rules]) + " "
        + " ".join(assumptions)
        + " " + foil
        + " " + explanandum
    )

    # reify
    logger.info("Original Program to reify: %s", to_reify)
    reified = manual_reify(to_reify)
    logger.debug("Original reified rules: %s\n", reified)
    logger.info("Original reified rules translated: %s\n",
                reified_to_original_rules(reified))

    reified = add_optional_rules(reified, P_options)

    logger.debug("Model with optional rules translated: %s \n",
                 reified_to_original_rules(reified))
    logger.debug("Model with optional rules reified: %s\n", reified)

    I_primes = solve_return_all_model_subset_heuristics(
        [str(reified), META_STR, COUNTERFACTUAL_STR], "subset-maximal")

    counterfactual_models_all_literals = solve_return_all_model_subset_heuristics(
        [str(reified), META_STR_ALL_LITERALS, COUNTERFACTUAL_STR], "subset-maximal")

    CA = []
    for i, counterfactual_model in enumerate(counterfactual_models_all_literals):
        counterfactual_model_all_literals = ". ".join(
            counterfactual_model) + "."
        translated_counterfactual_rules = reified_to_original_rules(
            Program(counterfactual_model_all_literals))

        logger.info("I': %s", I_primes[i])
        logger.debug("Counterfactual model with all literals: %s",
                     counterfactual_model_all_literals)
        logger.info("Translated: %s", translated_counterfactual_rules)

        P_prime = P.intersection(translated_counterfactual_rules)
        A_prime = set(A).intersection(I_primes[i])
        CA.append((P_prime, I_primes[i], A_prime))

    return CA
