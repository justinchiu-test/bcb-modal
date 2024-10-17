import requests
import datasets
from tqdm import tqdm

def send_request(codes):
    url = "https://justinchiu--runtest-dev.modal.run"
    response = requests.post(url, json={"codes": codes})
    return response.json()

def main():
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

    batch_size = 5  # Adjust this based on your needs
    results = []
    
    for i in tqdm(range(0, len(complete_dataset), batch_size)):
        batch = complete_dataset[i:i+batch_size]
        codes = [example["solution"] for example in batch]
        batch_results = send_request(codes)
        results.extend(batch_results)

    print(f"Received {len(results)} results:")
    for i, result in enumerate(results):
        print(f"Result {i + 1}: {result}")

if __name__ == "__main__":
    main()
