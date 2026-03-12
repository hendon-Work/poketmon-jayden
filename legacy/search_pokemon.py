
import json
import sys
import os

def load_data():
    try:
        # Try finding the file in the current directory
        with open('pokemon_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: pokemon_data.json not found.")
        return None

def search_pokemon(query, data):
    results = []
    
    # 1. Search in Tier Data
    tier_matches = []
    for type_group in data.get('tier_data', []):
        # Type Match
        if query in type_group['Type']:
             results.append({
                "category": f"{type_group['Type']} 타입 티어 (Raid)",
                "type": "table",
                "data": type_group['Pokémon']
            })
        else:
            # Pokemon Match
            matching = [p for p in type_group['Pokémon'] if query in p['Name']]
            if matching:
                 results.append({
                    "category": f"{type_group['Type']} 타입 검색 결과",
                    "type": "table",
                    "data": matching
                })

    # 2. Beginner List
    beginner_matches = []
    for p in data.get('beginner_list', []):
        if query in p['name'] or query in p['from']:
            beginner_matches.append(p)
    
    if beginner_matches:
        results.append({
            "category": "초보자 추천",
            "type": "beginner_list",
            "data": beginner_matches
        })

    # 3. All Pokemon (Pokedex info)
    pokedex_matches = []
    for p in data.get('all_pokemon', []):
        if query in p['name']:
            pokedex_matches.append(p)
            
    if pokedex_matches:
        results.append({
            "category": "도감 정보",
            "type": "pokedex",
            "data": pokedex_matches
        })

    return results

def print_table(data):
    # Fixed width formatting for terminal
    print(f"{'등급':<10} | {'이름':<15} | {'DPS':<5} | {'TDO':<5} | {'기술'}")
    print("-" * 60)
    for row in data:
        # Simple formatting
        print(f"{row['Grade']:<10} | {row['Name']:<15} | {row['DPS']:<5} | {row['TDO']:<5} | {row['Moves']}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python search_pokemon.py [포켓몬이름 또는 타입]")
        return

    query = sys.argv[1]
    data = load_data()
    
    if not data:
        return

    results = search_pokemon(query, data)

    if results:
        print(f"=== '{query}' 검색 결과 ===\n")
        for res in results:
            print(f"[{res['category']}]")
            if res['type'] == 'table':
                print_table(res['data'])
            elif res['type'] == 'beginner_list':
                for p in res['data']:
                    print(f"- {p['name']} (진화전: {p['from']}) / {p['moves']}")
            elif res['type'] == 'pokedex':
                print(f"{'도감번호':<10} | {'이름':<15} | {'타입':<15} | {'진화 정보':<20} | {'4배 약점':<10} | {'2배 약점'}")
                print("-" * 100)
                for p in res['data']:
                    types_str = ", ".join(p.get('types', []))
                    weak4 = p.get('weaknesses', {}).get('4배', '-') if p.get('weaknesses', {}).get('4배') else '-'
                    weak2 = p.get('weaknesses', {}).get('2배', '-') if p.get('weaknesses', {}).get('2배') else '-'
                    evo = p.get('evolution', '-')
                    print(f"No.{p['no']:<7} | {p['name']:<15} | {types_str:<15} | {evo:<20} | {weak4:<10} | {weak2}")
            print("\n")
    else:
        print(f"'{query}'에 대한 상세 데이터(Tier 등)를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
