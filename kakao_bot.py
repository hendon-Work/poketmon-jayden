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
        "beginner_matches": [],
        "raid_matches": []
    }
    
    # 1. 도감 검색
    for p in data.get('all_pokemon', []):
        if query in str(p.get('name', '')):
            types_str = ", ".join(p.get('types', []))
            weak4 = p.get('weaknesses', {}).get('4배', '-') if p.get('weaknesses', {}).get('4배') else '-'
            weak2 = p.get('weaknesses', {}).get('2배', '-') if p.get('weaknesses', {}).get('2배') else '-'
            evo_info = f"\n🧬 진화: {p['evolution']}" if 'evolution' in p else ""
            
            result_data["pokedex_matches"].append({
                "no": p['no'],
                "name": p['name'],
                "short_desc": f"🔸 타입: {types_str}",
                "full_desc": f"[{p['name']}]\n💥 4배 약점: {weak4} / ⚡ 2배 약점: {weak2}{evo_info}"
            })

    # 2. 티어 검색
    for type_group in data.get('tier_data', []):
        if query in type_group['Type']:
            results = []
            for p in type_group['Pokémon']:
                 results.append(f"[{p['Grade']}] {p['Name']}\n⚔️ {p['Moves']} (DPS: {p['DPS']})")
            result_data["tier_matches"].append({"type": type_group['Type'], "results": results})
        else:
            matching = [p for p in type_group['Pokémon'] if query in p['Name']]
            if matching:
                 results = []
                 for p in matching:
                     results.append(f"[{p['Grade']}] {p['Name']}\n⚔️ {p['Moves']} (DPS: {p['DPS']})")
                 result_data["tier_matches"].append({"type": type_group['Type'], "results": results})

    # 3. 초보자 추천 검색
    for p in data.get('beginner_list', []):
        if query in p['name'] or query in p['from']:
            result_data["beginner_matches"].append(
                f"🌱 {p['name']} (진화전: {p['from']})\n✨ 추천 기술: {p['moves']}"
            )
            
    # 4. 레이드 카운터 검색
    raid_counters = data.get('raid_counters', {})
    for boss, counters in raid_counters.items():
        if query in boss:
            result_data["raid_matches"].append({
                "boss": boss,
                "counters": counters
            })
            
    is_empty = not result_data["tier_matches"] and not result_data["beginner_matches"] and not result_data["pokedex_matches"] and not result_data["raid_matches"]
    if is_empty:
        # 검색 결과가 없을 때의 응답 메시지를 자유롭게 변경할 수 있습니다.
        return {"error": f"앗! '{query}'(이)라는 포켓몬은 아직 도감에 없거나, 이름을 잘못 입력하신 것 같아요. 🥲 다시 한번 정확히 입력해 주세요!"}
        
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
            
        outputs = []
        
        # 대표 포켓몬 번호 찾기 (썸네일용)
        def get_thumbnail_url(no):
            if no:
                try:
                    num = int(str(no).split('-')[0].strip()) # 773-1 같은 폼 대응은 기본 773번 이미지로
                    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{num}.png"
                except Exception:
                    pass
            return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"

        # 도감 정보를 매칭한 경우 1. 이미지 원본 비율 보존을 위한 BasicCard 또는 Carousel 출력
        if result_data["pokedex_matches"]:
            items = []
            for p in result_data["pokedex_matches"][:5]: # 최대 5개의 폼 출력
                items.append({
                    "title": f"📖 No.{p['no']} {p['name']}",
                    "description": p['short_desc'], 
                    "thumbnail": {
                        "imageUrl": get_thumbnail_url(p["no"]),
                        "fixedRatio": True,
                        "width": 500,
                        "height": 500
                    }
                })
            
            if len(items) == 1:
                outputs.append({"basicCard": items[0]})
            else:
                outputs.append({
                    "carousel": {
                        "type": "basicCard",
                        "items": items
                    }
                })

        # 2. 텍스트 카드를 슬라이드 내용별로 명확하게 분리 (최대 400자 지원)
        text_cards = []
        
        # 2-1. 첫번째 슬라이드: 진화 트리 정보 및 약점 4배/2배 (+ 초보자 추천)
        pokedex_lines = []
        if result_data["pokedex_matches"]:
            for p in result_data["pokedex_matches"][:5]:
                if p.get('full_desc'):
                    pokedex_lines.append(p['full_desc'])
                    
        if result_data["beginner_matches"]:
            if pokedex_lines:
                pokedex_lines.append("────────────────")
            pokedex_lines.append(f"🔰 [초보자 추천]")
            pokedex_lines.extend(result_data["beginner_matches"][:2])
            
        pokedex_desc = "\n".join(pokedex_lines).strip()
        if pokedex_desc:
            if len(pokedex_desc) > 400:
                pokedex_desc = pokedex_desc[:395] + "..."
            text_cards.append({
                "title": f"� '{user_utterance}' 포켓몬 정보",
                "description": pokedex_desc
            })

        # 2-2. 두번째 슬라이드: 타입 티어 정보 (타입별로 각각의 슬라이드 카드로 분리하여 잘림 방지)
        for match in result_data["tier_matches"][:3]: # 최대 3개의 타입까지 슬라이드로 추가
            tier_lines = []
            tier_lines.extend(match["results"][:4]) # 한 타입당 4위까지 보여줌
            
            tier_desc = "\n\n".join(tier_lines).strip() # 줄간격 띄우기
            if tier_desc:
                if len(tier_desc) > 390:
                    tier_desc = tier_desc[:385] + "..."
                text_cards.append({
                    "title": f"📊 {match['type']} 타입 티어 및 기술추천",
                    "description": tier_desc
                })

        # 2-3. 세번째 슬라이드: 레이드 카운터 정보 (6위씩 분리하여 여러 슬라이드로)
        if result_data["raid_matches"]:
            for match in result_data["raid_matches"][:2]: # 보스가 2개 이상일 때 대비
                counters = match['counters']
                # 최대 18위까지(3슬라이드) 노출. 한 슬라이드당 최대 6위.
                for page in range(0, min(len(counters), 18), 6):
                    chunk = counters[page:page+6]
                    lines = []
                    for i, counter in enumerate(chunk):
                        lines.append(f"{page+i+1}. {counter['pokemon']}\n  - {counter['fast_move']} / {counter['charge_move']}")
                    
                    desc = "\n".join(lines).strip()
                    if len(desc) > 390: 
                        desc = desc[:385] + "..."
                    
                    text_cards.append({
                        "title": f"⚔️ [{match['boss']}] 카운터 ({page+1}~{page+len(chunk)}위)",
                        "description": desc
                    })
            
        if text_cards:
            if len(text_cards) == 1:
                outputs.append({"textCard": text_cards[0]})
            else:
                outputs.append({
                    "carousel": {
                        "type": "textCard",
                        "items": text_cards[:10] # 카카오톡 carousel 아이템 개수 제한(10개) 대비
                    }
                })

        response = {
            "version": "2.0",
            "template": {
                "outputs": outputs
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
