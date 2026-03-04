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
        "pokedex_matches": [],
        "tier_matches": [],
        "beginner_matches": []
    }
    
    # 1. 도감 검색
    for p in data.get('all_pokemon', []):
        if query in str(p.get('name', '')):
            types_str = ", ".join(p.get('types', []))
            weak4 = p.get('weaknesses', {}).get('4배', '-') if p.get('weaknesses', {}).get('4배') else '-'
            weak2 = p.get('weaknesses', {}).get('2배', '-') if p.get('weaknesses', {}).get('2배') else '-'
            result_data["pokedex_matches"].append({
                "no": p['no'],
                "name": p['name'],
                "desc": f"🔸 타입: {types_str}\n💥 4배 약점: {weak4}\n⚡ 2배 약점: {weak2}"
            })

    # 2. 티어 검색
    for type_group in data.get('tier_data', []):
        if query in type_group['Type']:
            results = []
            for p in type_group['Pokémon']:
                 results.append(f"[{p['Grade']} 티어] {p['Name']}\n⚔️ {p['Moves']}\n📊 DPS: {p['DPS']} | TDO: {p['TDO']}")
            result_data["tier_matches"].append({"type": type_group['Type'], "results": results})
        else:
            matching = [p for p in type_group['Pokémon'] if query in p['Name']]
            if matching:
                 results = []
                 for p in matching:
                     results.append(f"[{p['Grade']} 티어] {p['Name']}\n⚔️ {p['Moves']}\n📊 DPS: {p['DPS']} | TDO: {p['TDO']}")
                 result_data["tier_matches"].append({"type": type_group['Type'], "results": results})

    # 3. 초보자 추천 검색
    for p in data.get('beginner_list', []):
        if query in p['name'] or query in p['from']:
            result_data["beginner_matches"].append(
                f"🌱 {p['name']} (진화전: {p['from']})\n✨ 추천 기술: {p['moves']}"
            )
            
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
            
        cards = []
        thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Pok%C3%A9_Ball_icon.svg/1024px-Pok%C3%A9_Ball_icon.svg.png"

        # 1. 도감 카드 생성
        for p in result_data["pokedex_matches"][:3]: # 카드는 길이 제한이 있어 최대 3개까지만
            cards.append({
                "title": f"📖 No.{p['no']} {p['name']}",
                "description": p['desc'],
                "thumbnail": {"imageUrl": thumbnail_url}
            })
            
        # 2. 티어 카드 생성
        for match in result_data["tier_matches"][:3]: # 최대 3개 타입 결과만
            desc_lines = match["results"][:3] # 한 카드당 상위 3마리만
            if len(match["results"]) > 3:
                desc_lines.append("...등 더 많은 정보가 있습니다.")
                
            cards.append({
                "title": f"🏆 {match['type']} 타입 티어/검색",
                "description": "\n\n".join(desc_lines),
                "thumbnail": {"imageUrl": thumbnail_url}
            })
                
        # 3. 초보자 추천 카드 생성
        if result_data["beginner_matches"]:
            cards.append({
                "title": f"🔰 초보자 추천 포켓몬",
                "description": "\n\n".join(result_data["beginner_matches"][:3]),
                "thumbnail": {"imageUrl": thumbnail_url}
            })

        # 혹시 모를 배열 초과 방지 (Carousel은 최대 10개까지 지원)
        cards = cards[:10]

        # 단일 카드인지, 캐러셀(여러 장 카드 슬라이드)인지에 따라 형태 분기
        if len(cards) == 1:
            template = {
                "outputs": [{"basicCard": cards[0]}]
            }
        else:
            template = {
                "outputs": [{"carousel": {"type": "basicCard", "items": cards}}]
            }

        response = {
            "version": "2.0",
            "template": template
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
