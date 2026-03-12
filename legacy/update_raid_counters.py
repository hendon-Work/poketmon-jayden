import csv
import json
import os
import re

def update_raid_counters():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'raid_counters.csv')
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')

    # Read existing data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dictionary to store raid counters
    raid_counters = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row in reader:
            if not row or len(row) < 4: continue
            
            boss = row[0].strip()
            if not boss: continue
            
            # Remove newlines and extra spaces from the pokemon name
            counter_pokemon = " ".join(row[1].split())
            fast_move = " / ".join(row[2].split())
            charge_move = " / ".join(row[3].split())
            
            if boss not in raid_counters:
                raid_counters[boss] = []
                
            raid_counters[boss].append({
                "pokemon": counter_pokemon,
                "fast_move": fast_move,
                "charge_move": charge_move
            })

    data['raid_counters'] = raid_counters

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Added raid counters for {len(raid_counters)} boss(es).")

if __name__ == "__main__":
    update_raid_counters()
