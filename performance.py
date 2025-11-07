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

def test_coloring():
    for n in range(120, 126, 5):
        for i in range(1,4):
            explanation_frame, contrastive_explanation_problem = ex_coloring(n, i)
            time_start = perf_counter()
            contrastive_explanations(explanation_frame, contrastive_explanation_problem)
            time_stop = perf_counter()   
            with open("performance_results/result.txt", "a") as result_file:
                result_file.write(f"coloring, {n}-{i}, {round(time_stop - time_start, 4)}\n")

if __name__ == '__main__':
    test_coloring()
    for n in range(4, 35):
        test("nqueens", ex_nqueens, n)
    for n in  (4, 9, 16, 25):
        test("sudoku", ex_sudoku_simplified, n)
   
        