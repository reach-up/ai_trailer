from fastapi import FastAPI, Request
import subprocess

app = FastAPI()

@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    data = await request.json()
    plot = data.get("plot", "Default plot...")

    with open("plot.txt", "w") as f:
        f.write(plot)

    subprocess.run(["python", "src/main.py"])
    return {"status": "started"}
