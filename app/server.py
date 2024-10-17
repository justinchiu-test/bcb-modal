import modal

app = modal.App("bcb-server")

# bcb dockerfile uses python 3.10, but i dont know how that's possible since llvmlite requires < 3.10
# and it seems like one of the requirements requires llvmlite?
image = (modal.Image.from_registry("ubuntu:22.04", add_python="3.9")
    .env({"DEBIAN_FRONTEND": "noninteractive", "TZ": "America/New_York"})
    .run_commands("apt update")
    .apt_install("clang", "git", "g++", "python3-tk", "zip", "unzip", "procps", "r-base")
    # bigcodebench requirements, but with versions removed :laugh:
    .copy_local_file("requirements.txt")
    .pip_install("uv")
    .run_commands(
        "uv pip install --system -r requirements.txt",
        "uv pip install --system pytest pytest-json-report",
    )
    .workdir("/test")
)


@app.function(
    image=image,
    cpu=1.0,
    concurrency_limit=64,
)
def run(code):
    import subprocess
    import json
    from pathlib import Path

    with Path("run.py").open("w") as f:
        f.write(code)

    output = subprocess.check_output(
        f"pytest run.py --json-report --json-report-file=report.json".split()
    )

    with Path("report.json").open("r") as f:
        result = json.loads(f.read())
        outcomes = [test["outcome"] for test in result["tests"]]
        return outcomes


@app.local_entrypoint()
async def main():
    import asyncio
    import datasets
    import pdb
    dataset = datasets.load_dataset("bigcode/bigcodebench", split="v0.1.2[:10]")

    def combine_code_solution(example):
        example["solution"] = (
            example["complete_prompt"]
            + example["canonical_solution"]
            + "\n"
            + example["test"]
        )
        return example

    complete_dataset = dataset.map(combine_code_solution)

    futures = []
    for example in complete_dataset:
        futures.append(run.remote.aio(example["solution"]))
    all_outcomes = await asyncio.gather(*futures)
    print(all_outcomes)


#web_image = modal.Image.debian_slim(python_version="3.10")


#@app.function(image=web_image, timeout=60*20)
#@modal.web_endpoint(
#    method="POST", label=f"runtest",
#)
#def runtest(data) -> list[str]:
#    """Generate responses to a batch of prompts, optionally with custom inference settings."""
#    return run.remote(data)
