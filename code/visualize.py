import matplotlib.pyplot as plt
import pickle

def plot_equity(history):

    plt.figure()
    plt.plot(history)
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Portfolio Value")
    plt.grid()
    plt.show()


if __name__ == "__main__":

    # load saved history
    with open("equity.pkl", "rb") as f:
        history = pickle.load(f)

    plot_equity(history)