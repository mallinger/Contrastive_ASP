from counterfactual_explanation import counterfactual_explanations


def contrastive_explanations(explanation_frame, contrastive_explanation_problem):
    (P, S, A) = explanation_frame
    CFEs = counterfactual_explanations(explanation_frame, contrastive_explanation_problem)
    CEs = []
    for (Q1, Q2, Q_delta) in CFEs:
        CEs.append((Q1 - Q2.add_program(S), Q2 -
                   Q1.add_program(S), Q_delta - S))
    return CEs
