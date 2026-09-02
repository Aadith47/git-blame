import matplotlib.pyplot as plt


def plot_language_distribution(language_distribution):
    plt.figure(figsize=(8, 5))

    language_distribution.plot(kind="bar")

    plt.title("GitHub Language Distribution")
    plt.xlabel("Programming Language")
    plt.ylabel("Number of Repositories")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()