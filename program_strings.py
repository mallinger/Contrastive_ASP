

META_STR = """
#defined weighted_literal_tuple/3.
conjunction(B) :- literal_tuple(B),
        hold(L) : literal_tuple(B, L), L > 0;
    not hold(L) : literal_tuple(B,-L), L > 0.

body(normal(B)) :- rule(_,normal(B)), conjunction(B).
body(sum(B,G))  :- rule(_,sum(B,G)),
    #sum { W,L :     hold(L), weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : not hold(L), weighted_literal_tuple(B,-L,W), L > 0 } >= G.

  hold(A) : atom_tuple(H,A)   :- rule(disjunction(H),B), body(B).
{ hold(A) : atom_tuple(H,A) } :- rule(     choice(H),B), body(B).

#show.
#show T : output(T,B), conjunction(B).
"""

META_STR_ALL_LITERALS = """
#defined weighted_literal_tuple/3.
conjunction(B) :- literal_tuple(B),
        hold(L) : literal_tuple(B, L), L > 0;
    not hold(L) : literal_tuple(B,-L), L > 0.

body(normal(B)) :- rule(_,normal(B)), conjunction(B).
body(sum(B,G))  :- rule(_,sum(B,G)),
    #sum { W,L :     hold(L), weighted_literal_tuple(B, L,W), L > 0 ;
           W,L : not hold(L), weighted_literal_tuple(B,-L,W), L > 0 } >= G.

  hold(A) : atom_tuple(H,A)   :- rule(disjunction(H),B), body(B).
{ hold(A) : atom_tuple(H,A) } :- rule(     choice(H),B), body(B).

"""


COUNTERFACTUAL_STR = """
        :- hold(E), output(explanandum(A),_), output(A,N), literal_tuple(N,E).
        :- not hold(F), output(foil(A),_), output(A,N), literal_tuple(N,F).
        {hold(S)} :- output(assumption(A),_), output(A,N), literal_tuple(N,S).
    """

FILTER_RULES_STR = """
#defined body_neg/2.
#defined body_pos/2.
        variable_in_rule_head(L, H):- output(L, HEO), literal_tuple(HEO, HEOL), atom_tuple(H, HEOL).
        variable_neg_in_rule_body(L, B):- output(L, BNEO), literal_tuple(BNEO, BNEOL), literal_tuple(B, -BNEOL).
        variable_pos_in_rule_body(L, B):- output(L, BNEO), literal_tuple(BNEO, BNEOL), literal_tuple(B, BNEOL).
        optional_rule(disjunction(A), normal(B)) :- optional(head(H), body_pos(BP), body_neg(BN)), 
                                variable_in_rule_head(L, A): head_elem(H, L);
                                head_elem(H, L): variable_in_rule_head(L, A);
                                variable_pos_in_rule_body(L, B): body_pos(BP, L);
                                body_pos(BP, L): variable_pos_in_rule_body(L, B);
                                variable_neg_in_rule_body(L, B): body_neg(BN, L);
                                body_neg(BN, L): variable_neg_in_rule_body(L, B);
                                rule(disjunction(A), normal(B)).   
    """
