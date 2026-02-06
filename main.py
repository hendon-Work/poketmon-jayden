from fastapi import FastAPI, Request

app = FastAPI()

# 포켓몬 데이터베이스
POKEMON_INFO = {
    "피카츄": {"tier": "B", "skills": "전기쇼크 / 10만볼트"},
    "뮤츠": {"tier": "S+", "skills": "사이코커터 / 사이코브레이크"},
    "망나뇽": {"tier": "A", "skills": "용의숨결 / 드래곤클로"}
}

@app.post("/pokemon")
async def handle_kakao(request: Request):
    data = await request.json()
    
    # 1. 어떤 데이터가 들어오는지 Render 로그에 출력 (디버깅용)
    print(f"카카오 요청 데이터: {data}")

    # 2. 파라미터 찾기 (여러 경로를 모두 뒤져봅니다)
    action = data.get('action', {})
    params = action.get('params', {})
    detail_params = action.get('detailParams', {})

    # pokemon_name 또는 poketmon_name 중 있는 것을 가져옵니다.
    name = params.get('pokemon_name') or \
           params.get('poketmon_name') or \
           detail_params.get('pokemon_name', {}).get('value') or \
           ''

    # 3. 응답 로직
    if name in POKEMON_INFO:
        info = POKEMON_INFO[name]
        msg = f"🔍 {name}의 분석 정보\n⭐ 티어: {info['tier']}\n⚔️ 추천 스킬: {info['skills']}"
    else:
        # 이 메시지가 나오면 서버가 'name'을 여전히 못 찾은 것입니다.
        msg = f"'{name}' 포켓몬 정보를 찾을 수 없습니다. (입력된 이름: {name})"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": msg}}]
        }
    }
