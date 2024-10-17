import asyncio
import datasets
import pdb
import modal
import subprocess
import json
import pathlib
import modal

app = modal.App("swebench-server")

image = modal.Image.from_registry("bigcodebench/bigcodebench-evaluate")


@app.function(
    image=image,
    cpu=1.0,
    concurrency_limit=64,
)
def run(example):
    task_id = example["task_id"].replace("/", "-")

    rundir = pathlib.Path(f"scratch/{task_id}")
    rundir.mkdir(exist_ok=True, parents=True)

    with (rundir / "run.py").open("w") as f:
        f.write(example["solution"])
        f.write("\n")
        f.write(example["test"])

    output = subprocess.check_output(
        f"pytest scratch/{task_id}/run.py --json-report --json-report-file=scratch/{task_id}/report.json".split()
    )

    with (rundir / "report.json").open("r") as f:
        result = json.loads(f.read())
        outcomes = [test["outcome"] for test in result["tests"]]
        return outcomes


@app.local_entrypoint()
async def main():
    dataset = datasets.load_dataset("bigcode/bigcodebench", split="v0.1.2[:10]")

    def combine_code_solution(example):
        example["solution"] = example["complete_prompt"] + example["canonical_solution"]
        return example

    complete_dataset = dataset.map(combine_code_solution)

    futures = []
    for example in dataset:
        futures.append(run.remote.aio(example))
    all_outcomes = asyncio.gather(*futures)
    pdb.set_trace()
