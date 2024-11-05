import os
import json
from datetime import datetime
import pyrematch as REmatch

HERE = "/home/gustavo/Documents/REmatch-datasets/"

with open(
    os.path.join(HERE, "scripts", "config", "test-config.json"),
    encoding="utf-8",
) as file:
    EXPERIMENT_CONFIG = json.load(file)

CHOSEN_EXPERIMENTS = EXPERIMENT_CONFIG["experimentsToRun"]

# document is a global variable
document = ""


def get_regex(rgx_path):
    with open(rgx_path, "r", encoding="utf-8") as file_path:
        rgx = file_path.read()
    return rgx


def find_differences(actual_outputs, expected_outputs):
    idx1 = 0
    idx2 = 0

    missing_outputs = []
    extra_outputs = []

    while idx1 < len(actual_outputs) and idx2 < len(expected_outputs):

        actual_output = actual_outputs[idx1]
        expected_output = expected_outputs[idx2]

        if actual_output > expected_output:
            missing_outputs.append(expected_output)
            idx2 += 1
        elif expected_output > actual_output:
            extra_outputs.append(actual_output)
            idx1 += 1
        else:
            idx1 += 1
            idx2 += 1

    missing_outputs.extend(expected_outputs[idx2:])
    extra_outputs.extend(actual_outputs[idx1:])

    return missing_outputs, extra_outputs


def print_differences(missing_outputs, extra_outputs):
    if missing_outputs or extra_outputs:
        print("Outputs are different")
    else:
        print("Outputs are identical")

    if missing_outputs:
        print("Missing outputs:")
        for output in missing_outputs:
            print(f"\t{output}")

    if extra_outputs:
        print("Extra outputs:")
        for output in extra_outputs:
            print(f"\t{output}")


def check_if_outputs_are_correct(regex_path, expected_outputs_path):
    with open(regex_path, "r", encoding="utf-8") as regex_file:
        pattern = regex_file.read()

    with open(expected_outputs_path, "r", encoding="utf-8") as expected_outputs_file:
        expected_outputs = [line.strip() for line in expected_outputs_file.readlines()]

    query = REmatch.reql(
        pattern, max_deterministic_states=100000, max_mempool_duplications=10
    )
    matches = query.findall(document)

    expected_outputs = sorted(expected_outputs)
    actual_outputs = sorted([str(m) for m in matches])

    missing_outputs, extra_outputs = find_differences(actual_outputs, expected_outputs)

    outputs_are_equal = not (missing_outputs or extra_outputs)
    print_differences(missing_outputs, extra_outputs)

    return outputs_are_equal


def run_experiments():
    global document

    for suite in CHOSEN_EXPERIMENTS:
        print(f"\tOn dataset: {suite}\n")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        # define the paths
        experiment_paths = EXPERIMENT_CONFIG["experiments"][suite]
        queries_path = os.path.join(HERE, experiment_paths["queries"])
        document_path = os.path.join(HERE, experiment_paths["document"])
        results_path = os.path.join(
            HERE, EXPERIMENT_CONFIG["correctnessOutputDirectory"], suite, timestamp
        )

        os.makedirs(results_path, exist_ok=True)

        output_file = open(
            os.path.join(results_path, "summary.csv"), "w", encoding="utf-8"
        )

        output_file.write("id,regex,is_correct\n")

        for dataset in sorted(os.listdir(queries_path)):
            expected_outputs_path = os.path.join(
                HERE, experiment_paths["outputs"], dataset
            )

            with open(document_path, "rb") as document_file:
                document = document_file.read()

            for experiment in sorted(os.listdir(os.path.join(queries_path, dataset))):
                regex_path = os.path.join(
                    queries_path, dataset, experiment, "rematch.rgx"
                )
                expected_output_path = os.path.join(
                    expected_outputs_path, experiment + ".txt"
                )
                print(f"Regex: {dataset}/{experiment}")
                try:
                    equal = check_if_outputs_are_correct(
                        regex_path, expected_output_path
                    )
                    output_file.write(
                        f'{dataset}-{experiment},"{get_regex(regex_path)}",{equal}\n'
                    )
                except TimeoutError:
                    print("Timeout")
                    output_file.write(
                        f'{dataset}-{experiment},"{get_regex(regex_path)}",timeout\n'
                    )

        output_file.close()


if __name__ == "__main__":
    run_experiments()
