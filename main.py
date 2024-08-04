from contrastive_explanation import contrastive_explanations
from counterfactual_account import counterfactual_accounts
from counterfactual_explanation import counterfactual_explanations
from examples import *


if __name__ == '__main__':
    explanation_frame, contrastive_explanation_problem = ex0()

    #print(counterfactual_accounts(explanation_frame, contrastive_explanation_problem))
   
    #print(counterfactual_explanations(explanation_frame, contrastive_explanation_problem))
    print (contrastive_explanations(explanation_frame, contrastive_explanation_problem))
        
