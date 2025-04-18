import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


df = pd.read_csv("performance_results/result.txt")
df.columns = ["Name", "n", "Time"]

def plot_nqueens():
    df_nqueens = df[df["Name"] =="nqueens"]
    boxes = [df_nqueens[df_nqueens["n"] == n]["Time"] for n in range(4, 32, 3)]
    plt.boxplot(boxes)
    plt.xticks([n for n in range(1, 11)],[n for n in range(4, 32, 3)])
    plt.xlabel("Number of Queens")
    plt.ylabel("runtime (s)")
    plt.savefig("plots/plot_nqueens.pdf", format="pdf", bbox_inches="tight")
    plt.show()

def plot_sudoku():
    df_sudoku = df[df["Name"] =="sudoku"]
    boxes = [df_sudoku[df_sudoku["n"] == n]["Time"] for n in [4, 9, 16, 25]]
    
    plt.boxplot(boxes)
    plt.xticks([1,2,3,4],[4,9,16,25])
    plt.xlabel("Length of Sudoku Row")
    plt.ylabel("runtime (s)")
    plt.savefig("plots/plot_sudoku.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    
def plot_coloring():
    df_coloring = df[df["Name"] =="coloring"]
    boxes = [df_coloring[df_coloring["n"] == n]["Time"] for n in range(10, 130,5)]
    figure(figsize=(10, 6), dpi=80)
    plt.boxplot(boxes)
    plt.xticks([n for n in range(1, 25)],[n for n in range(10, 130,5)])
   
    plt.xlabel("Number of Nodes")
    plt.ylabel("runtime (s)")
    plt.savefig("plots/plot_coloring.pdf", format="pdf", bbox_inches="tight")
    plt.show()

plot_nqueens()