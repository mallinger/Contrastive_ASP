import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("performance_results/result.txt")
df.columns = ["Name", "n", "Time"]

def plot_nqueens():
    df_nqueens = df[df["Name"] =="nqueens"]
    df_nqueens_mean = df_nqueens.groupby("n").Time.mean()
    plt.plot(df_nqueens_mean)
    plt.title("Runtime of Generating one Contrastive Explanations for the nqueens Problem")
    plt.xlabel("Number of Queens")
    plt.ylabel("Seconds")
    plt.show()

def plot_sudoku():
    df_sudoku = df[df["Name"] =="sudoku"]
    df_sudoku_mean = df_sudoku.groupby("n").Time.mean()
    plt.plot(df_sudoku_mean)
    plt.xticks([4,9,16,25])
    plt.title("Runtime of Generating one Contrastive Explanations for Sudoku")
    plt.xlabel("Length of Sudoku Row")
    plt.ylabel("Seconds")
    plt.show()
    
def plot_coloring():
    df_coloring = df[df["Name"] =="coloring"]
    df_coloring_mean = df_coloring.groupby("n").Time.mean()
    plt.plot(df_coloring_mean)
    plt.title("Runtime of Generating one Contrastive Explanations for the 3-Coloring Problem")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Seconds")
    plt.show()

plot_nqueens()