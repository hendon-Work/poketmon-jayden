from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# 데이터 로드
def load_data():
    try:
        # 현재 스크립트 파일의 디렉토리를 기준으로 절대 경로 생성
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'pokemon_data.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

data = load_data()

def search_pokemon_raw(query):
    """
    Returns a dictionary with parsed results instead of a single formatted string,
    so the bot can format it into a BasicCard.
    """
    if not data:
        return {"error": "데이터를 불러올 수 없습니다."}
        
    result_data = {
        "tier_matches": [],
        "beginner_matches": [],
        "pokedex_matches": []
    }
    
    # 1. 티어 데이터 검색
    for type_group in data.get('tier_data', []):
        if query in type_group['Type']:
            results = []
            for p in type_group['Pokémon']:
                 results.append(f"{p['Grade']} | {p['Name']} | DPS: {p['DPS']} | TDO: {p['TDO']} | {p['Moves']}")
            result_data["tier_matches"].append({"type": type_group['Type'], "results": results})
        else:
            matching = [p for p in type_group['Pokémon'] if query in p['Name']]
            if matching:
                 results = []
                 for p in matching:
                     results.append(f"{p['Grade']} | {p['Name']} | DPS: {p['DPS']} | TDO: {p['TDO']} | {p['Moves']}")
                 result_data["tier_matches"].append({"type": type_group['Type'], "results": results})

    # 2. 초보자 추천 검색
    for p in data.get('beginner_list', []):
        if query in p['name'] or query in p['from']:
            result_data["beginner_matches"].append(
                f"- {p['name']} (진화전: {p['from']})\n기술: {p['moves']}"
            )

    # 3. 도감 정보 검색
    for p in data.get('all_pokemon', []):
        if query in str(p.get('name', '')):
            types_str = ", ".join(p.get('types', []))
            weak4 = p.get('weaknesses', {}).get('4배', '-') if p.get('weaknesses', {}).get('4배') else '-'
            weak2 = p.get('weaknesses', {}).get('2배', '-') if p.get('weaknesses', {}).get('2배') else '-'
            result_data["pokedex_matches"].append({
                "no": p['no'],
                "name": p['name'],
                "desc": f"타입: {types_str}\n4배 약점: {weak4}\n2배 약점: {weak2}"
            })
            
    is_empty = not result_data["tier_matches"] and not result_data["beginner_matches"] and not result_data["pokedex_matches"]
    if is_empty:
        return {"error": f"'{query}'에 대한 검색 결과가 없습니다."}
        
    return result_data

@app.route('/api/pokemon', methods=['POST'])
def kakao_pokemon_bot():
    try:
        req = request.get_json(force=True, silent=True) or {}
        user_utterance = req.get('userRequest', {}).get('utterance', '').strip()
        
        if not user_utterance:
            return return_simple_text("포켓몬 이름이나 타입을 검색해주세요.")
            
        result_data = search_pokemon_raw(user_utterance)
        
        if "error" in result_data:
            return return_simple_text(result_data["error"])
            
        # BasicCard 생성을 위해 텍스트 조립
        title = f"🔍 '{user_utterance}' 검색 결과"
        desc_lines = []
        
        if result_data["pokedex_matches"]:
            for p in result_data["pokedex_matches"][:3]: # 카드는 길이 제한이 있어 최대 3개까지만 도감 정보 축약
                desc_lines.append(f"No.{p['no']} {p['name']}\n{p['desc']}")
            desc_lines.append("────────────────")
            
        if result_data["tier_matches"]:
            for match in result_data["tier_matches"][:2]: # 티어 결과 최대 2개 타입분만
                desc_lines.append(f"[{match['type']} 타입 티어/검색]")
                desc_lines.extend(match["results"][:3]) # 첫 3마리만
                if len(match["results"]) > 3:
                    desc_lines.append("...등")
                desc_lines.append("")
                
        if result_data["beginner_matches"]:
            desc_lines.append(f"[초보자 추천]")
            desc_lines.extend(result_data["beginner_matches"][:2])

        description = "\n".join(desc_lines).strip()
        
        # description 문자열 76자 이상일때 처리해야 하지만 넉넉히 잘라줌
        # Kakao BasicCard 제약상 description의 최대 글자수가 정해져있을 수 있음
        if len(description) > 500:
            description = description[:495] + "\n..."

        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "basicCard": {
                            "title": title,
                            "description": description,
                            "thumbnail": {
                                # 포켓몬 공식 일러스트 대신 포켓몬스터 범용 공 썸네일 혹은 투명 이미지 사용
                                "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/1024px-Pok%C3%A9_Ball_icon.svg.png"
                            },
                        }
                    }
                ]
            }
        }
        return jsonify(response)
            
    except Exception as e:
        return return_simple_text(f"서버 처리 중 에러가 발생했습니다: {str(e)}")

def return_simple_text(text):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text[:995] + "..." if len(text) > 1000 else text
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    # Render 등 클라우드 환경에서는 PORT 환경변수를 사용합니다
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
