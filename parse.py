import sys
import json
import matplotlib.pyplot as plt
import numpy as np
import os


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


def plot(durations, func, problems):
# Find log problems in the trace
    pxs = []
    pys = []
    if len(problems) > 0:
        pxs_temp = []
        xs = list([float(list(sample.keys())[0]) for sample in durations])
        for problem in problems:
            diff = int(problem - xs[0])
            delta = diff * 3
            pxs_temp.extend([delta, delta+1, delta+2])
        for i in pxs_temp:
            if i < 0:
                continue
            try:
                pys.append(list(durations[i].items())[0][-1]/1000)
                pxs.append(i)
            except Exception as e:
                print(i)
                print(len(durations))
    # Figure 1
    ys = list([list(sample.items())[0][-1]/1000 for sample in durations])
    max_y = max(ys)
    _, ax = plt.subplots()
    ylim_low = 0.3
    ylim_high = max_y * 5
    ax.set_xlabel("Sample")
    ax.set_ylabel("Call duration, ms")
    ax.set_title(f"{func} execution time and average")
    data, = ax.plot(np.array(ys), label='Data')
    ax.set(ylim=(ylim_low, ylim_high), yscale='log')

    avg = ax.twinx()
    avg.set(ylim=(ylim_low, ylim_high), yscale='log')
    avg_data = [sum(ys)/len(ys)] * len(ys)
    av, = avg.plot(avg_data, 'r', label='Average')

    if len(pxs)> 0:
        prob = ax.twinx()
        prob.set(ylim=(ylim_low, ylim_high), yscale='log')
        probs, = prob.plot(pxs, pys, color="orange", linewidth=3, marker="o",markersize=10, label='Problem(s)')
        ax.legend(handles=[data, probs, av])
    else:
        ax.legend(handles=[data, av])    

    # Figure 2
    _, ax2 = plt.subplots()
    ax2.hist(ys, bins=100, color="Gray")
    ax2.set_yscale('log')
    ax2.set_title(f"{func} duration histogram (logY) and CDF")
    count, _ = np.histogram(ys, bins=100)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    ax3 = ax2.twinx()
    ax3.plot(np.arange(0, max(ys), max(ys)/100)[0:100], cdf, label='CDF')
    plt.show()

def find_log_problems():
    issues = []
    files = os.listdir(".")
    for file in files:
        if "log" in file:
            with open(file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "diff -1000000000" in line or "diff -999999999" in line:
                        fields = line.split(" ")
                        ts = fields[3].split("[")[-1].split("]")[0]
                        issues.append(float(ts))
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse.py <trace file name> <function name>, for example:")
        print("python3 parse.py trace_pipe-3 ice_ptp_adjfine")
        sys.exit(0)
    file_name = sys.argv[1]
    func_name = sys.argv[2]
    durations = parse_file(file_name, func_name)
    # Uncomment to dump data to json
    with open(f"{file_name}_{func_name}.json", "w") as fw:
        json.dump(durations, fw)
    log_problems = find_log_problems()
    plot(durations, func_name, log_problems)