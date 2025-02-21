from counterfactual_explanation import counterfactual_explanations


def contrastive_explanations(explanation_frame, contrastive_explanation_problem, number_of_counterfactual_accounts=1, number_of_explanations=1):
    (P, S, A) = explanation_frame
    try:
        CFEs = counterfactual_explanations(explanation_frame, contrastive_explanation_problem, number_of_counterfactual_accounts, number_of_explanations)
    except ValueError as error:
        raise error
    CEs = []
    for (Q1, Q2, Q_delta) in CFEs:
        CEs.append((Q1 - Q2.add_program(S), Q2 -
                   Q1.add_program(S), Q_delta - S))
    return CEs
