import uvicorn
from multiprocessing import Process


def run_public_app():
    uvicorn.run("src.public_app:app", host="0.0.0.0", port=8000, reload=False)

def run_internal_app():
    uvicorn.run("src.internal_app:app", host="127.0.0.1", port=9000, reload=False)


if __name__ == "__main__":
    public_process = Process(target=run_public_app)
    internal_process = Process(target=run_internal_app)

    public_process.start()
    internal_process.start()

    public_process.join()
    internal_process.join()
