import datasets
import pdb
import modal
import subprocess
import json
import pathlib


dataset = datasets.load_dataset("bigcode/bigcodebench", split="v0.1.2")

def combine_code_solution(example):
    example["solution"] = example["complete_prompt"] + example["canonical_solution"]
    return example

complete_dataset = dataset.map(combine_code_solution)


example = complete_dataset[0]
print("solution")
print(example["solution"])
print("test")
print(example["test"])

with open("scratch/run.py", "w") as f:
    f.write(example["solution"])
    f.write("\n")
    f.write(example["test"])

output = subprocess.check_output(
    f"pytest scratch/run.py --json-report --json-report-file=scratch/report.json".split()
)

with open("scratch/report.json", "r") as f:
    result = json.loads(f.read())
    outcomes = [test["outcome"] for test in result["tests"]]

pdb.set_trace()
