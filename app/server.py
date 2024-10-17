import asyncio
import datasets
import pdb
import modal
import subprocess
import json
import pathlib
import modal

app = modal.App("bcb-server")

image = (modal.Image.from_registry("ubuntu:22.04", add_python="3.10")
    .run_commands("apt update")
    .apt_install("clang", "git", "g++", "python3-tk", "zip", "unzip", "procps", "r-base")
    .copy_local_file("requirements.txt")
    .pip_install("uv")
    .run_commands(
        "uv pip install --system -r requirements.txt",
        #"pip install -r requirements.txt",
    )
)


@app.function(
    image=image,
    cpu=1.0,
    concurrency_limit=64,
)
def run(code):
    with ("run.py").open("w") as f:
        f.write(code)

    output = subprocess.check_output(
        f"pytest run.py --json-report --json-report-file=report.json".split()
    )

    with ("report.json").open("r") as f:
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
        futures.append(run.remote.aio(example["solution"]))
    all_outcomes = await asyncio.gather(*futures)
    pdb.set_trace()


web_image = modal.Image.debian_slim(python_version="3.10")


@app.function(image=web_image, timeout=60*20)
@modal.web_endpoint(
    method="POST", label=f"runtest",
)
def runtest(data) -> list[str]:
    """Generate responses to a batch of prompts, optionally with custom inference settings."""
    return run.remote(data)
