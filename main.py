from fastapi import FastAPI, Request

app = FastAPI()

# 데이터 키값도 '피카츄'로 되어있는지 확인해주세요!
POKEMON_INFO = {
    "피카츄": {"tier": "B", "skills": "전기쇼크 / 10만볼트"},
    "뮤츠": {"tier": "S+", "skills": "사이코커터 / 사이코브레이크"},
    "망나뇽": {"tier": "A", "skills": "용의숨결 / 드래곤클로"}
}

@app.post("/pokemon")
async def handle_kakao(request: Request):
    data = await request.json()
    
    # [수정 포인트] 카카오 i 오픈빌더 설정값과 동일하게 't'를 넣었습니다.
    params = data.get('action', {}).get('params', {})
    name = params.get('poketmon_name', '') 

    if name in POKEMON_INFO:
        info = POKEMON_INFO[name]
        response_text = f"🔍 {name}의 분석 정보입니다.\n⭐ 티어: {info['tier']}\n⚔️ 추천 스킬: {info['skills']}"
    else:
        # name이 비어있거나 데이터에 없을 때 출력됩니다.
        response_text = f"'{name}' 포켓몬 정보를 찾을 수 없습니다. (입력된 이름: {name})"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": response_text}}]
        }
    }
