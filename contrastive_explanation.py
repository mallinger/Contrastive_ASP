"""
Contrastive Explanation Module

This modules generates contrastive explanations from a given 
explanation frame and contrastive explanation problem.
"""

from counterfactual_explanation import counterfactual_explanations


def contrastive_explanations(
    explanation_frame,
    contrastive_explanation_problem,
    number_of_counterfactual_accounts=1,
    number_of_explanations=1,
):
    """
    Returns contrastive explanations for a given explanation frame
    and contrastive explanation problem
    
    Parameters
    ----------
    explanation_frame : tuple
        Tuple (P, S, A) representing the original program (P), fixed knowledge (S),
        and assumptions (A).
    contrastive_explanation_problem : tuple
        Tuple (I, E, F) representing an answer set (I), the explanandum (E),
        and the foil (F).
    number_of_counterfactual_accounts : int, optional
        Number of counterfactual accounts to generate (default is 1).
    number_of_explanations : int, optional
        Number of counterfactual explanations to return (default is 1).
        
    Returns
    -------
    list of tuples
        List of contrastive explanations as tuples.    
        
    Raises:
    ------
    ValueError: 
        If counterfactual explanation generation fails.
    """
    (P, S, A) = explanation_frame
    try:
        CFEs = counterfactual_explanations(
            explanation_frame,
            contrastive_explanation_problem,
            number_of_counterfactual_accounts,
            number_of_explanations,
        )
    except ValueError as error:
        raise error
    CEs = []
    for Q1, Q2, Q_delta in CFEs:
        CEs.append((Q1 - Q2.add_program(S), Q2 - Q1.add_program(S), Q_delta - S))
    return CEs
