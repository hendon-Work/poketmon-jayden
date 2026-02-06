from fastapi import FastAPI, Request

app = FastAPI()

# 임시 데이터베이스 (나중에 실제 API나 더 많은 데이터로 확장 가능합니다)
POKEMON_INFO = {
    "피카츄": {"tier": "B", "skills": "전기쇼크 / 10만볼트"},
    "뮤츠": {"tier": "S+", "skills": "사이코커터 / 사이코브레이크"},
    "망나뇽": {"tier": "A", "skills": "용의숨결 / 드래곤클로"}
}

@app.post("/pokemon")
async def handle_kakao(request: Request):
    data = await request.json()
    
    # 카카오에서 보낸 파라미터 값(포켓몬 이름) 읽기
    params = data.get('action', {}).get('params', {})
    name = params.get('pokemon_name', '') # 2단계에서 설정한 파라미터 이름

    if name in POKEMON_INFO:
        info = POKEMON_INFO[name]
        response_text = f"🔍 {name}의 분석 정보입니다.\n⭐ 티어: {info['tier']}\n⚔️ 추천 스킬: {info['skills']}"
    else:
        # 이름을 찾지 못했거나 입력되지 않았을 때
        response_text = f"'{name}' 포켓몬을 찾을 수 없습니다. 이름을 정확히 입력하셨나요?"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
