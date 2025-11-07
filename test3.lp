blue(X) | red(X) | green(X) :- node(X).
:- blue(X), blue(Y), link(X, Y).
:- green(X), green(Y), link(X, Y). 
:- red(X), red(Y), link(X, Y).
node(one). node(two). 
node(three). green(one). 
red(two). link(one, three).
link(two, three).