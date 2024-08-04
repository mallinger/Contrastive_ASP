
#preference(p,superset) { 
  rule(X,Y)
}.
#optimize(p).
output(feathers, 12). literal_tuple(20). atom_tuple(8, 19). output(bird, 14). output(darkwings, 15). literal_tuple(20, 20). literal_tuple(4). atom_tuple(0). literal_tuple(17). atom_tuple(5, 14). literal_tuple(3). atom_tuple(5). literal_tuple(16, 16). atom_tuple(1, 12). literal_tuple(18). literal_tuple(15, 15). literal_tuple(18, 18). atom_tuple(0, 11). literal_tuple(5). output(whitewings, 17). atom_tuple(2). output(explanandum(crow), 11). literal_tuple(5, 12). atom_tuple(8). literal_tuple(9). literal_tuple(21, 21). atom_tuple(4, 18). rule(disjunction(2), normal(2)). literal_tuple(3, 17). atom_tuple(6, 15). literal_tuple(14, 14). atom_tuple(2, 13). output(crow, 13). atom_tuple(9, 21). atom_tuple(7, 20). literal_tuple(11, 11). atom_tuple(7). rule(disjunction(3), normal(3)). literal_tuple(16). rule(disjunction(1), normal(1)). output(magpie, 16). literal_tuple(19, 19). literal_tuple(14). output(beak, 19). rule(disjunction(7), normal(7)). atom_tuple(3). literal_tuple(21). literal_tuple(6). literal_tuple(1). literal_tuple(5, 20). rule(disjunction(5), normal(5)). literal_tuple(13, 13). literal_tuple(11). atom_tuple(6). rule(disjunction(0), normal(0)). literal_tuple(0). literal_tuple(2, 15). literal_tuple(15). output(foil(magpie), 18). literal_tuple(2, 14). atom_tuple(1). atom_tuple(9). literal_tuple(13). output(shape, 20). literal_tuple(3, 14). literal_tuple(17, 17). literal_tuple(5, 19). rule(disjunction(8), normal(8)). literal_tuple(19). literal_tuple(7). literal_tuple(12, 12). literal_tuple(12). output(assumption(whitewings), 21). literal_tuple(8). rule(disjunction(9), normal(9)). atom_tuple(3, 16). rule(disjunction(4), normal(4)). literal_tuple(2). atom_tuple(4). {rule(disjunction(6), normal(6))}.
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


        :- hold(E), output(explanandum(A),_), output(A,N), literal_tuple(N,E).
        :- not hold(F), output(foil(A),_), output(A,N), literal_tuple(N,F).
        {hold(S)} :- output(assumption(A),_), output(A,N), literal_tuple(N,S).
    