import matplotlib.pyplot as plt
import re
import os
import glob

def parse_log(log_path):
    """
    Parses a log file to extract the best validation accuracy.
    """
    best_acc = 0.0
    with open(log_path, 'r') as f:
        for line in f:
            if "Validation Acc:" in line:
                try:
                    acc = float(line.split("Validation Acc:")[1].strip())
                    if acc > best_acc:
                        best_acc = acc
                except ValueError:
                    continue
    return best_acc

def main():
    log_dir = 'logs'
    fractions = [0.1, 0.2, 0.5, 1.0]
    accuracies = []
    
    for frac in fractions:
        log_path = os.path.join(log_dir, f"frac_{frac}.log")
        if os.path.exists(log_path):
            acc = parse_log(log_path)
            accuracies.append(acc)
            print(f"Fraction {frac}: Best Val Acc = {acc:.4f}")
        else:
            print(f"Log file not found for fraction {frac}")
            accuracies.append(0.0)
            
    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(fractions, accuracies, marker='o', linestyle='-', linewidth=2, markersize=8)
    plt.title('Data Efficiency: Validation Accuracy vs Data Fraction')
    plt.xlabel('Fraction of Training Data')
    plt.ylabel('Validation Accuracy')
    plt.grid(True)
    plt.ylim(0, 1.0)
    
    for i, txt in enumerate(accuracies):
        plt.annotate(f"{txt:.2f}", (fractions[i], accuracies[i]), textcoords="offset points", xytext=(0,10), ha='center')
        
    plt.savefig('data_efficiency_plot.png')
    print("Plot saved to data_efficiency_plot.png")

if __name__ == '__main__':
    main()
