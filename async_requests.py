import aiohttp
import asyncio

async def send_post_requests(strings):
    """
    Takes a list of strings and sends those strings as separate POST requests
    to https://modal-server.com/run using aiohttp.
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for string in strings:
            task = asyncio.create_task(send_single_request(session, string))
            tasks.append(task)
        await asyncio.gather(*tasks)

async def send_single_request(session, string):
    """Helper function to send a single POST request."""
    url = "https://modal-server.com/run"
    async with session.post(url, data=string) as response:
        return await response.text()

# Example usage
if __name__ == "__main__":
    strings_to_send = ["string1", "string2", "string3"]
    asyncio.run(send_post_requests(strings_to_send))
