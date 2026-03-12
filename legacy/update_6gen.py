import csv
import json
import os

def update_6gen():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '6gen.csv')
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')

    # Read existing data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_pokemon = data.get('all_pokemon', [])
    existing_nos = set(str(p['no']) for p in all_pokemon)
    existing_names = set(p['name'] for p in all_pokemon)

    added_count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row in reader:
            if not row or len(row) < 6: continue
            
            no = row[0].strip()
            name = row[1].strip()
            type1 = row[2].strip()
            type2 = row[3].strip()
            weak4 = row[4].strip()
            weak2 = row[5].strip()
            
            if not no.isdigit(): continue
            
            # Ensure no duplicates: update if exists
            existing_p = next((p for p in all_pokemon if str(p['no']) == no), None)
            
            types = []
            if type1 and type1 != '-': types.append(type1)
            if type2 and type2 != '-': types.append(type2)
            
            # Formatting weaknesses
            weaknesses = {}
            if weak4 and weak4 != '-':
                weak4 = weak4.replace("(4배)", "").strip()
                weaknesses["4배"] = weak4
            if weak2 and weak2 != '-':
                if "(4배)" in weak2:
                    parts = [p.strip() for p in weak2.split(",")]
                    w4 = []
                    w2 = []
                    for p in parts:
                        if "(4배)" in p:
                            w4.append(p.replace("(4배)", "").strip())
                        else:
                            w2.append(p)
                    
                    if w4:
                        weaknesses["4배"] = ", ".join(w4)
                    if w2:
                        weaknesses["2배"] = ", ".join(w2)
                else:
                    weaknesses["2배"] = weak2

            if not types: continue
            
            if existing_p:
                existing_p['name'] = name
                existing_p['types'] = types
                existing_p['weaknesses'] = weaknesses
                existing_p['generation'] = "6세대 포켓몬"
                added_count += 1
            else:
                new_pokemon = {
                    "no": int(no),
                    "name": name,
                    "types": types,
                    "weaknesses": weaknesses,
                    "generation": "6세대 포켓몬"
                }
                all_pokemon.append(new_pokemon)
                existing_nos.add(no)
                existing_names.add(name)
                added_count += 1
                
    data['all_pokemon'] = all_pokemon

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Added/Updated {added_count} 6th generation Pokemon to the pokedex.")

if __name__ == "__main__":
    update_6gen()
