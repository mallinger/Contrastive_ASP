dom(1..5).
1 { a(X) : dom(X) }.
#show a/1.

#preference(p,superset) { 
  a(X)
}.
#optimize(p).


