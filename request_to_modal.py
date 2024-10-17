import asyncio
import aiohttp
import datasets
from tqdm import tqdm

async def send_request(session, codes):
    url = "https://justinchiu--runtest-dev.modal.run"
    async with session.post(url, json={"codes": codes}) as response:
        return await response.json()

async def main():
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

    async with aiohttp.ClientSession() as session:
        batch_size = 5  # Adjust this based on your needs
        results = []
        
        for i in tqdm(range(0, len(complete_dataset), batch_size)):
            batch = complete_dataset[i:i+batch_size]
            codes = [example["solution"] for example in batch]
            batch_results = await send_request(session, codes)
            results.extend(batch_results)

    print(f"Received {len(results)} results:")
    for i, result in enumerate(results):
        print(f"Result {i + 1}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
