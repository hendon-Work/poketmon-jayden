from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# 데이터 로드
def load_data():
    try:
        with open('pokemon_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

data = load_data()

def search_pokemon(query):
    if not data:
        return "데이터를 불러올 수 없습니다."
        
    results = []
    
    # 1. 티어 데이터 검색
    for type_group in data.get('tier_data', []):
        if query in type_group['Type']:
             results.append(f"[{type_group['Type']} 타입 티어]")
             for p in type_group['Pokémon']:
                 results.append(f"{p['Grade']} | {p['Name']} | {p['DPS']} | {p['TDO']} | {p['Moves']}")
        else:
            matching = [p for p in type_group['Pokémon'] if query in p['Name']]
            if matching:
                 results.append(f"[{type_group['Type']} 타입 검색 결과]")
                 for p in matching:
                     results.append(f"{p['Grade']} | {p['Name']} | {p['DPS']} | {p['TDO']} | {p['Moves']}")

    # 2. 초보자 추천 검색
    beginner_matches = []
    for p in data.get('beginner_list', []):
        if query in p['name'] or query in p['from']:
            beginner_matches.append(p)
            
    if beginner_matches:
        results.append("\n[초보자 추천]")
        for p in beginner_matches:
            results.append(f"- {p['name']} (진화전: {p['from']})\n  기술: {p['moves']}")

    # 3. 도감 정보 검색
    pokedex_matches = []
    for p in data.get('all_pokemon', []):
        if query in str(p.get('name', '')):
            pokedex_matches.append(p)
            
    if pokedex_matches:
        results.append("\n[도감 정보]")
        for p in pokedex_matches:
            types_str = ", ".join(p.get('types', []))
            weak4 = p.get('weaknesses', {}).get('4배', '-') if p.get('weaknesses', {}).get('4배') else '-'
            weak2 = p.get('weaknesses', {}).get('2배', '-') if p.get('weaknesses', {}).get('2배') else '-'
            results.append(f"No.{p['no']} {p['name']}\n타입: {types_str}\n4배 약점: {weak4}\n2배 약점: {weak2}\n---")

    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다."
        
    return "\n".join(results)

@app.route('/api/pokemon', methods=['POST'])
def kakao_pokemon_bot():
    req = request.get_json()
    
    # 카카오톡 챗봇에서 사용자가 입력한 발화(utterance) 추출
    user_utterance = req.get('userRequest', {}).get('utterance', '').strip()
    
    # 검색 수행
    search_result = search_pokemon(user_utterance)
    
    # 최대 텍스트 길이(1000자) 제한 확인 (카카오톡 simpleText 정책)
    if len(search_result) > 1000:
        search_result = search_result[:995] + "\n..."
    
    # 카카오톡 응답 포맷 (Skill Response)
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": search_result
                    }
                }
            ]
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    # Render 등 클라우드 환경에서는 PORT 환경변수를 사용합니다
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
