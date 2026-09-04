from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Server is running"}


@app.get("/ping")
def ping():
    return {"pong": True}


@app.get("/add")
def add_numbers(a: float, b: float):
    return {
        "operation": "addition",
        "a": a,
        "b": b,
        "result": a + b
    }