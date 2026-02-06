from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "포켓몬 챗봇 서버가 작동 중입니다!"}

@app.post("/pokemon")
async def chat(request: Request):
    item = await request.json()
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": "포켓몬 정보를 곧 알려드릴게요!"}}]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)