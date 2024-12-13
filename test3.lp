b(X) | r(X) | g(X) :- node(X).
:- b(X), b(Y), edge(X, Y).
:- g(X), g(Y), edge(X, Y). 
:- r(X), r(Y), edge(X, Y).
node(one). node(two). 
node(three). g(one). 
r(two). edge(one, three).
edge(two, three).