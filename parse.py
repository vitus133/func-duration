import sys
import json
import matplotlib.pyplot as plt
import numpy as np


def parse_file (fn, func):
    durations = []
    with open(fn) as f:
        lines = f.readlines()
    state = -1
    for line in lines:
        if func in line and "/*" not in line:
            state = 0
        if state >= 0:
            if "{" in line:
                state += 1
            if "}" in line:
                state -= 1
            if state == 0:
                ts = float(line.split("|")[0].strip(" "))
                duration = float(line.split("|")[-2].split("us")[-2].strip(" ").split(" ")[-1])
                state = -1
                durations.append({ts: duration})
    return durations


def plot(durations, func):
    _, ax = plt.subplots()
    ys = list([list(sample.items())[0][-1] for sample in durations])
    ax.set_xlabel("Sample")
    ax.set_ylabel("Call duration, usec")
    ax.set_title(f"{func} execution time and average")
    ax.plot(np.array(ys))
    avg = ax.twinx()
    avg_data = [sum(ys)/len(ys)] * len(ys)
    avg.plot(avg_data, 'r', label='AVG')
    avg.set_ybound(0, max(ys))
    
    _, ax2 = plt.subplots()
    ax2.hist(ys, bins=100, color="Gray")
    ax2.set_yscale('log')
    ax2.set_title(f"{func} duration histogram (logY) and CDF")
    count, _ = np.histogram(ys, bins=100)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    ax3 = ax2.twinx()
    ax3.plot(np.arange(0, max(ys), max(ys)/100), cdf, label='CDF')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse.py <trace file name> <function name>, for example:")
        print("python3 parse.py trace_pipe-3 ice_ptp_adjfine")
        sys.exit(0)
    file_name = sys.argv[1]
    func_name = sys.argv[2]
    durations = parse_file(file_name, func_name)
    # Uncomment to dump data to json
    # with open(f"{file_name}_{func_name}.json", "w") as fw:
    #     json.dump(durations, fw)
    plot(durations, func_name)