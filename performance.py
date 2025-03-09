from time import perf_counter

from contrastive_explanation import contrastive_explanations

from examples import *

def test(name, example, n):
    explanation_frame, contrastive_explanation_problem = example(n)
    for i in range(3):
        time_start = perf_counter()
        print(contrastive_explanations(explanation_frame, contrastive_explanation_problem))
        time_stop = perf_counter()
            
        with open("performance_results/result.txt", "a") as result_file:
            result_file.write(f"{name}, {n}, {time_stop - time_start}\n")

if __name__ == '__main__':
    for n in range(60, 100,5):
        test("coloring", ex_coloring, n)
    for n in range(4, 16):
        test("nqueens", ex_nqueens, n)
    for n in (4, 9, 16, 25):
        test("sudoku", ex_sudoku, n)
    

   
        