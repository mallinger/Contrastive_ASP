from time import perf_counter

from contrastive_explanation import contrastive_explanations

from examples import *


if __name__ == '__main__':
    examples = [ex0(), ex2(), ex3(), ex4(), ex5(), ex6()]
    for example in examples:
        explanation_frame, contrastive_explanation_problem = example
        for i in range(3):
            time_start = perf_counter()
            contrastive_explanations(explanation_frame, contrastive_explanation_problem)
            time_stop = perf_counter()
            
            with open("performance_results/result.txt", "a") as result_file:
                result_file.write(f"name, {time_stop - time_start}\n")
    

   
        