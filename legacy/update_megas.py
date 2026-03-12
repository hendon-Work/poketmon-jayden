import json
import os
import requests

TYPE_TRANSLATION = {
    "normal": "노말", "fire": "불꽃", "water": "물", "electric": "전기",
    "grass": "풀", "ice": "얼음", "fighting": "격투", "poison": "독",
    "ground": "땅", "flying": "비행", "psychic": "에스퍼", "bug": "벌레",
    "rock": "바위", "ghost": "고스트", "dragon": "드래곤", "dark": "악",
    "steel": "강철", "fairy": "페어리"
}

# Type interaction matrix (simplified for weaknesses calculation)
# For pokemon weaknesses, we fetch from type effectiveness logic or hardcode.
# Better to use a small lookup function for weaknesses
# PokeAPI에서 실시간으로 타입 상성을 가져오기 위한 캐시
TYPE_DATA_CACHE = {}

def get_type_data(type_name_en):
    if type_name_en in TYPE_DATA_CACHE:
        return TYPE_DATA_CACHE[type_name_en]
    res = requests.get(f"https://pokeapi.co/api/v2/type/{type_name_en}")
    data = res.json()['damage_relations']
    TYPE_DATA_CACHE[type_name_en] = data
    return data

def calculate_weaknesses_from_api(types_en):
    # Pokemon Go uses ~1.6 for SE, ~0.625 for NVE, ~0.39 for immunities
    effectiveness = {t: 1.0 for t in TYPE_TRANSLATION.keys()}
    
    for t in types_en:
        relations = get_type_data(t)
        for d in relations['double_damage_from']:
            if d['name'] in effectiveness:
                effectiveness[d['name']] *= 1.6
        for d in relations['half_damage_from']:
            if d['name'] in effectiveness:
                effectiveness[d['name']] *= 0.625
        for d in relations['no_damage_from']:
            if d['name'] in effectiveness:
                effectiveness[d['name']] *= 0.390625 # Pokemon Go's latest immunity multiplier
                
    weak_4x = [TYPE_TRANSLATION[k] for k, v in effectiveness.items() if v >= 2.5]
    weak_2x = [TYPE_TRANSLATION[k] for k, v in effectiveness.items() if 1.5 < v < 2.0]
    
    res = {}
    if weak_4x:
        res["4배"] = ", ".join(weak_4x)
    if weak_2x:
        res["2배"] = ", ".join(weak_2x)
    return res

MEGA_LIST = {
    10033: "메가 이상해꽃", 10034: "메가 리자몽X", 10035: "메가 리자몽Y", 10036: "메가 거북왕",
    10090: "메가 독침붕", 10073: "메가 피죤투", 10037: "메가 후딘", 10071: "메가 야도란",
    10038: "메가 팬텀", 10039: "메가 캥카", 10040: "메가 쁘사이저", 10041: "메가 갸라도스",
    10042: "메가 프테라", 10043: "메가 뮤츠X", 10044: "메가 뮤츠Y", 10045: "메가 전룡",
    10072: "메가 강철톤", 10046: "메가 핫삼", 10047: "메가 헤라크로스", 10048: "메가 헬가",
    10049: "메가 마기라스", 10065: "메가 나무킹", 10050: "메가 번치코", 10064: "메가 대짱이",
    10051: "메가 가디안", 10066: "메가 깜까미", 10052: "메가 입치트", 10053: "메가 보스로라",
    10054: "메가 요가램", 10055: "메가 썬더볼트", 10070: "메가 샤크니아", 10087: "메가 폭타",
    10067: "메가 파비코리", 10056: "메가 다크펫", 10057: "메가 앱솔", 10074: "메가 얼음귀신",
    10089: "메가 보만다", 10076: "메가 메타그로스", 10062: "메가 라티아스", 10063: "메가 라티오스",
    10078: "메가 레쿠쟈", 10088: "메가 이어롭", 10058: "메가 한카리아스", 10059: "메가 루카리오",
    10060: "메가 눈설왕", 10068: "메가 엘레이드", 10069: "메가 다부니", 10075: "메가 디안시"
}

def update_megas():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_pokemon = data.get('all_pokemon', [])
    all_pokemon = [p for p in all_pokemon if p.get('generation') != '메가진화']

    new_megas = []
    print("Fetching mega evolution data from PokeAPI...")
    for poke_id, poke_name in MEGA_LIST.items():
        try:
            res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{poke_id}")
            if res.status_code == 200:
                poke_data = res.json()
                types_en = [t['type']['name'] for t in poke_data['types']]
                types_ko = [TYPE_TRANSLATION.get(t) for t in types_en]
                weaknesses = calculate_weaknesses_from_api(types_en)
                
                new_megas.append({
                    "no": poke_id,
                    "name": poke_name,
                    "types": types_ko,
                    "weaknesses": weaknesses,
                    "generation": "메가진화"
                })
        except Exception as e:
            print(f"Error fetching {poke_id}: {e}")

    for m in new_megas:
        all_pokemon.append(m)

    data['all_pokemon'] = all_pokemon

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"{len(new_megas)} Megas updated!")

if __name__ == '__main__':
    update_megas()
