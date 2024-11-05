import os
import json
import time
from datetime import datetime
import subprocess
import matplotlib.pyplot as plt

HERE = "/home/gustavo/Documents/REmatch-datasets/"

with open(
    os.path.join(HERE, "scripts", "config", "test_correctness-config.json"),
    encoding="utf-8",
) as jsonFile:
    EXPERIMENT_CONFIG = json.load(jsonFile)

CHOSEN_EXPERIMENTS = EXPERIMENT_CONFIG["experimentsToRun"]


def save_boxplot(data, title, output_directory):
    plt.boxplot(data)
    plt.title(title)
    plt.savefig(os.path.join(output_directory))


def get_regex(rgx_path):
    with open(rgx_path, "r", encoding="utf-8") as file_path:
        rgx = file_path.read()
    return rgx


def execute_query(regex_path, document_path):
    initial_time = time.perf_counter()

    command_list = ["build/test-performance", regex_path, document_path]

    try:
        subprocess.run(
            command_list,
            cwd=HERE,
            check=True,
            capture_output=True,
            timeout=EXPERIMENT_CONFIG["timeoutInSeconds"],
        )

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print(e.stderr)
        return 0

    return round(time.perf_counter() - initial_time, 2)


def run_experiments():
    for suite in CHOSEN_EXPERIMENTS:
        print(f"\n\tOn dataset: {suite}\n")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        # define the paths
        experiment_paths = EXPERIMENT_CONFIG["experiments"][suite]
        queries_path = os.path.join(HERE, experiment_paths["queries"])
        document_path = os.path.join(HERE, experiment_paths["document"])
        results_path = os.path.join(
            HERE, EXPERIMENT_CONFIG["performanceOutputDirectory"], suite, timestamp
        )

        os.makedirs(results_path, exist_ok=True)

        output_file = open(
            os.path.join(results_path, "summary.csv"), "w", encoding="utf-8"
        )

        output_file.write("id,regex,time\n")

        times = []

        for dataset in sorted(os.listdir(queries_path)):

            for experiment in sorted(os.listdir(os.path.join(queries_path, dataset))):
                regex_path = os.path.join(
                    queries_path, dataset, experiment, "rematch.rgx"
                )
                print(f"Regex: {dataset}/{experiment}")
                try:
                    query_time = execute_query(regex_path, document_path)
                    times.append(query_time)
                    output_file.write(
                        f'{dataset}-{experiment},"{get_regex(regex_path)}",{query_time}\n'
                    )
                except TimeoutError:
                    print("Command timed out")
                    output_file.write(
                        f'{dataset}-{experiment},"{get_regex(regex_path)}",timeout\n'
                    )

        save_boxplot(
            times,
            suite,
            os.path.join(results_path, "times.png"),
        )

        output_file.close()


if __name__ == "__main__":
    run_experiments()
