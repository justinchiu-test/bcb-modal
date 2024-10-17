# bcb-server
Run bigcodebench execution stuff.

## Server
To run the server, use
```
uv run modal serve app/server.py
```
Terminating this command will also kill the server.

If you want to deploy it permanently, you can use
```
uv run modal deploy app/server.py
```
The deployed instance must be killed from the modal UI.

## Client
See `run_bcb_gold.py` for an example of running all the given solutions in bigcodebench.
Each request sent to the server should be a list of code strings to run.
Each code string should containt the solution + test cases as one string.
The server will take care of parallel execution for you.

Note: you will have to change the URL to your own, obtained by serving or deploying the modal app.

You can run this via
```
uv run python run_bcb_gold.py
```
