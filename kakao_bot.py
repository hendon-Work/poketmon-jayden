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
            
            result_data["pokedex_matches"].append({
                "no": p['no'],
                "name": p['name'],
                "short_desc": f"🔸 타입: {types_str}",
                "weaknesses": f"💥 4배 약점: {weak4}\n⚡ 2배 약점: {weak2}",
                "evolution": p.get('evolution', '')
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

# 대표 포켓몬 번호 찾기 (썸네일용)
def get_thumbnail_url(no):
    if no:
        try:
            num = int(str(no).split('-')[0].strip()) # 773-1 같은 폼 대응은 기본 773번 이미지로
            return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{num}.png"
        except Exception:
            pass
    return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"

@app.route('/api/pokemon', methods=['POST'])
def kakao_pokemon_bot():
    try:
        req = request.get_json(force=True, silent=True) or {}
        user_utterance = req.get('userRequest', {}).get('utterance', '').strip()
        
        if not user_utterance or user_utterance in ["시작", "메뉴", "도움말"]:
            return return_main_menu()
            
        # 포켓몬 검색 방법 안내 (버튼 클릭 시)
        if user_utterance == "포켓몬 검색":
            return return_search_guide()

        # 도감 정보 강제 검색 (레이드 보스인 경우에도 도감 정보를 보고 싶을 때)
        is_force_pokedex = any(k in user_utterance for k in ["정보", "도감"])
        clean_utterance = user_utterance.replace("정보", "").replace("도감", "").strip()

        # 배틀리그 관련 처리
        if "리그" in user_utterance:
            if any(l in user_utterance for l in ["슈퍼", "하이퍼", "마스터"]):
                league_name = next(l for l in ["슈퍼리그", "하이퍼리그", "마스터리그"] if l[:2] in user_utterance)
                
                # 티어 정보가 발화에 포함된 경우 (예: "슈퍼리그 S+ 티어 추천")
                target_tier = None
                for t in ["S~S+", "A~A+", "B~B+", "S+", "S", "A+", "A", "B+", "B"]:
                    if t in user_utterance:
                        target_tier = t if "~" in t else f"{t[0]}~{t[0]}+ 티어"
                        break
                
                if target_tier:
                    return return_league_recommendations(league_name, target_tier)
                else:
                    return return_tier_menu(league_name)
            return return_league_menu()
            
        # 레이드 관련 처리
        raid_bosses = data.get('raid_counters', {}).keys()
        is_raid_query = any(k in user_utterance for k in ["레이드", "카운터"])
        
        if not is_force_pokedex:
            for boss in raid_bosses:
                # 보스 이름이 정확히 일치하거나, 레이드/카운터 키워드가 포함된 경우
                if boss == user_utterance or (is_raid_query and boss in user_utterance):
                    return return_raid_details(boss)
            
            if is_raid_query:
                return return_raid_menu()

        result_data = search_pokemon_raw(clean_utterance if is_force_pokedex else user_utterance)
        
        if "error" in result_data:
            return return_simple_text(result_data["error"], include_menu=True)
            
        outputs = []

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
        
        # 2-1. 첫번째 슬라이드: 검색된 포켓몬들의 약점 정보
        if result_data["pokedex_matches"]:
            info_lines = []
            evo_lines = []
            
            for p in result_data["pokedex_matches"][:3]: # 최대 3개 폼까지 상세 노출
                info_lines.append(f"[{p['name']}]\n{p['weaknesses']}")
                if p['evolution'] and p['evolution'] not in evo_lines:
                    evo_lines.append(p['evolution'])
            
            # 정보 카드 추가
            info_desc = "\n\n".join(info_lines).strip()
            if info_desc:
                if len(info_desc) > 400: info_desc = info_desc[:395] + "..."
                text_cards.append({
                    "title": f"🔍 '{user_utterance}' 약점 정보",
                    "description": info_desc
                })
            
            # 진화 카드 추가 (별도 분리)
            if evo_lines:
                evo_desc = "\n\n".join([f"🧬 {e}" for e in evo_lines]).strip()
                if len(evo_desc) > 400: evo_desc = evo_desc[:395] + "..."
                text_cards.append({
                    "title": f"🧬 '{user_utterance}' 진화 트리",
                    "description": evo_desc
                })

        # 초보자 추천 카드는 별도로 유지 또는 통합
        if result_data["beginner_matches"]:
            beg_desc = "\n".join(result_data["beginner_matches"][:3]).strip()
            if len(beg_desc) > 400: beg_desc = beg_desc[:395] + "..."
            text_cards.append({
                "title": f"🔰 [초보자 추천] {user_utterance}",
                "description": beg_desc
            })

        # 2-2. 두번째 슬라이드: 타입 티어 정보 (타입별, 랭킹별로 슬라이드 카드로 분리하여 잘림 방지)
        for match in result_data["tier_matches"][:3]: # 최대 3개의 타입까지 슬라이드로 추가
            tier_results = match["results"]
            # 최대 9위까지(3슬라이드) 노출. 한 슬라이드당 최대 3위.
            for page in range(0, min(len(tier_results), 9), 3):
                chunk = tier_results[page:page+3]
                tier_desc = "\n\n".join(chunk).strip() # 줄간격 띄우기
                
                if tier_desc:
                    if len(tier_desc) > 390:
                        tier_desc = tier_desc[:385] + "..."
                    text_cards.append({
                        "title": f"📊 {match['type']} 타입 티어",
                        "description": tier_desc
                    })

        # 2-3. 세번째 슬라이드: 레이드 카운터 정보 (3위씩 분리하여 여러 슬라이드로)
        if result_data["raid_matches"]:
            for match in result_data["raid_matches"][:2]: # 보스가 2개 이상일 때 대비
                counters = match['counters']
                # 최대 15위까지(5슬라이드) 노출. 한 슬라이드당 최대 3위.
                for page in range(0, min(len(counters), 15), 3):
                    chunk = counters[page:page+3]
                    lines = []
                    for i, counter in enumerate(chunk):
                        lines.append(f"{page+i+1}. {counter['pokemon']}\n  - {counter['fast_move']} / {counter['charge_move']}")
                    
                    desc = "\n\n".join(lines).strip() # 줄간격을 무조건 주어 가독성 향상
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
                "outputs": outputs,
                "quickReplies": [
                    {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                    {"label": "🔍 다시 검색", "action": "message", "messageText": "포켓몬 검색"},
                    {"label": "🏆 배틀리그 추천", "action": "message", "messageText": "배틀리그 추천"},
                    {"label": "⚔️ 레이드 카운터", "action": "message", "messageText": "레이드 추천"}
                ]
            }
        }
        return jsonify(response)
            
    except Exception as e:
        return return_simple_text(f"서버 처리 중 에러가 발생했습니다: {str(e)}")

def return_search_guide():
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": "🔍 포켓몬 검색 방법 안내",
                        "description": "찾고 싶은 포켓몬의 이름을 직접 입력해 주세요!\n\n예시:\n📍 '피카츄' (이름 검색)\n📍 '그림자 맘모꾸리' (그림자 포켓몬)",
                        "thumbnail": {
                            "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"
                        }
                    }
                }
            ],
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                {"label": "🔴 리자몽", "action": "message", "messageText": "리자몽"},
                {"label": "⚪ 뮤츠", "action": "message", "messageText": "뮤츠"},
                {"label": "🔵 드래곤", "action": "message", "messageText": "드래곤"}
            ]
        }
    })

def return_simple_text(text, include_menu=False):
    res = {
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
    }
    if include_menu:
        res["template"]["quickReplies"] = [
            {"label": "🏠 홈", "action": "message", "messageText": "시작"},
            {"label": "🔍 포켓몬 검색", "action": "message", "messageText": "포켓몬 검색"},
            {"label": "🏆 배틀리그 추천", "action": "message", "messageText": "배틀리그 추천"},
            {"label": "⚔️ 레이드 카운터", "action": "message", "messageText": "레이드 메뉴"}
        ]
    return jsonify(res)

def return_main_menu():
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": "안녕하세요! 포켓몬 마스터 도우미입니다. ⚡",
                        "description": "원하시는 메뉴를 선택하거나 포켓몬 이름을 입력해 주세요.",
                        "thumbnail": {
                            "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"
                        }
                    }
                }
            ],
            "quickReplies": [
                {"label": "🔍 포켓몬 검색", "action": "message", "messageText": "포켓몬 검색"},
                {"label": "🏆 배틀리그 추천", "action": "message", "messageText": "배틀리그 추천"},
                {"label": "⚔️ 레이드 카운터", "action": "message", "messageText": "레이드 추천"}
            ]
        }
    })

def return_raid_menu():
    raid_bosses = list(data.get('raid_counters', {}).keys())
    if not raid_bosses:
        return return_simple_text("현재 등록된 레이드 정보가 없습니다.")
    
    # 최근 10개 보스만 노출 (카카오 퀵리플라이 제한 10개)
    quick_replies = []
    for boss in raid_bosses[:10]:
        quick_replies.append({"label": f"⚔️ {boss}", "action": "message", "messageText": f"{boss} 레이드"})

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "현재 진행 중인 주요 레이드 보스 목록입니다. 보스를 선택하면 카운터 정보를 알려드려요! ⚔️"
                    }
                }
            ],
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"}
            ] + quick_replies
        }
    })

def return_raid_details(boss_name):
    counters = data.get('raid_counters', {}).get(boss_name, [])
    if not counters:
        return return_simple_text(f"'{boss_name}' 레이드 정보가 없습니다.")

    # 보스 이미지 찾기
    boss_no = None
    for p in data.get('all_pokemon', []):
        if boss_name in p['name']:
            boss_no = p['no']
            break
    
    thumb_url = get_thumbnail_url(boss_no)

    # 1. 상단: 보스 이미지 단독 카드
    outputs = [
        {
            "basicCard": {
                "title": f"⚔️ [{boss_name}] 레이드 보스",
                "thumbnail": {
                    "imageUrl": thumb_url,
                    "fixedRatio": True
                }
            }
        }
    ]

    # 2. 하단: 카운터 정보 카루셀 (텍스트 카드 방식)
    counter_items = []
    # 3명씩 끊어서 카드 생성 (최대 15위까지)
    for page in range(0, min(len(counters), 15), 3):
        chunk = counters[page:page+3]
        lines = []
        for i, counter in enumerate(chunk):
            lines.append(f"{page+i+1}. {counter['pokemon']}\n  - {counter['fast_move']} / {counter['charge_move']}")
        
        desc = "\n\n".join(lines).strip()
        counter_items.append({
            "title": f"📊 카운터 포켓몬 ({page+1}~{page+len(chunk)}위)",
            "description": desc
        })

    if counter_items:
        outputs.append({
            "carousel": {
                "type": "textCard",
                "items": counter_items
            }
        })

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": outputs,
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                {"label": "📖 도감 정보", "action": "message", "messageText": f"{boss_name} 정보"},
                {"label": "⚔️ 다른 보스 보기", "action": "message", "messageText": "레이드 추천"}
            ]
        }
    })

def return_league_menu():
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "어떤 리그의 추천 포켓몬을 확인하시겠어요? 아래에서 리그를 선택해 주세요! 🏟️"
                    }
                }
            ],
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                {"label": "🔴 슈퍼리그 (CP 1500)", "action": "message", "messageText": "슈퍼리그 추천"},
                {"label": "🟡 하이퍼리그 (CP 2500)", "action": "message", "messageText": "하이퍼리그 추천"},
                {"label": "🔵 마스터리그 (제한 없음)", "action": "message", "messageText": "마스터리그 추천"}
            ]
        }
    })

def return_tier_menu(league_name):
    # 데이터에서 해당 리그의 티어 목록을 가져옴
    league_data = data.get('battle_league_data', {}).get(league_name, {})
    tiers = list(league_data.keys()) if isinstance(league_data, dict) else []
    
    if not tiers:
        return return_league_recommendations(league_name) # 기존 데이터 형식이면 바로 노출

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"[{league_name}] 어떤 티어의 추천 포켓몬을 확인하시겠어요? 🏆\n(시트 기준으로 매일 업데이트됩니다!)"
                    }
                }
            ],
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                {"label": "🥇 S~S+ 티어", "action": "message", "messageText": f"{league_name} S~S+ 티어 추천"},
                {"label": "🥈 A~A+ 티어", "action": "message", "messageText": f"{league_name} A~A+ 티어 추천"},
                {"label": "🥉 B~B+ 티어", "action": "message", "messageText": f"{league_name} B~B+ 티어 추천"},
                {"label": "🏟️ 리그 다시 선택", "action": "message", "messageText": "배틀리그 추천"}
            ]
        }
    })

def return_league_recommendations(league_name, tier_name=None):
    league_content = data.get('battle_league_data', {}).get(league_name, [])
    
    # 새로운 구조(dict)인 경우 티어 필터링
    if isinstance(league_content, dict):
        if tier_name:
            # "S+" 입력 시 "S~S+ 티어" 키 매칭 처리
            matched_key = next((k for k in league_content.keys() if tier_name in k), None)
            league_data = league_content.get(matched_key or tier_name, [])
        else:
            # 티어가 지정되지 않았으면 모든 티어 합치기
            league_data = []
            for t_data in league_content.values():
                league_data.extend(t_data)
    else:
        # 기존 리스트 구조인 경우
        league_data = league_content

    if not league_data:
        msg = f"죄송합니다. {league_name}"
        if tier_name: msg += f" {tier_name}"
        msg += " 데이터가 준비되지 않았습니다."
        return return_simple_text(msg)

    items = []
    # 3명씩 끊어서 카드 생성 (최대 30마리까지)
    for page in range(0, min(len(league_data), 30), 3):
        chunk = league_data[page:page+3]
        lines = []
        for i, p in enumerate(chunk):
            title_prefix = "🥇" if "S" in (tier_name or "") else "🥈" if "A" in (tier_name or "") else "🥉" if "B" in (tier_name or "") else "🔸"
            lines.append(f"{title_prefix} {p['name']}\n  - 기술: {p['moves']}")
        
        desc = "\n\n".join(lines).strip()
        items.append({
            "title": f"📊 {tier_name or league_name} 추천 포켓몬",
            "description": desc
        })

    title_text = f"🏆 [{league_name}]"
    if tier_name: title_text += f" {tier_name}"
    title_text += " 추천"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"{title_text} 결과입니다. 최신 메타를 반영하여 공략해 보세요! ⚡"
                    }
                },
                {
                    "carousel": {
                        "type": "textCard",
                        "items": items
                    }
                }
            ],
            "quickReplies": [
                {"label": "🏠 홈", "action": "message", "messageText": "시작"},
                {"label": "🏆 다른 티어 보기", "action": "message", "messageText": f"{league_name} 추천"},
                {"label": "🏟️ 다른 리그 보기", "action": "message", "messageText": "배틀리그 추천"}
            ]
        }
    })

if __name__ == '__main__':
    # Render 등 클라우드 환경에서는 PORT 환경변수를 사용합니다
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
