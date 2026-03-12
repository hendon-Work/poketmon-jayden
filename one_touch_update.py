import json
import os
import csv
import urllib.request
import io
import re

import ssl

def download_csv(url):
    print(f"Downloading data from {url}...")
    # Bypass SSL verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(url, context=ctx) as response:
            content = response.read().decode('utf-8')
            return content
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def process_pokemon_data(csv_content, existing_data):
    if not csv_content:
        return existing_data
    
    reader = csv.reader(io.StringIO(csv_content))
    header = next(reader)
    
    all_pokemon = existing_data.get('all_pokemon', [])
    # Create a mapping for quick lookup
    pokemon_map = {str(p['no']): p for p in all_pokemon}
    
    updated_count = 0
    added_count = 0
    
    for row in reader:
        if not row or len(row) < 6:
            continue
            
        no = row[0].strip()
        name = row[1].strip()
        type1 = row[2].strip()
        type2 = row[3].strip()
        weak4 = row[4].strip()
        weak2 = row[5].strip()
        
        if not no:
            continue
            
        types = []
        if type1 and type1 != '-': types.append(type1)
        if type2 and type2 != '-': types.append(type2)
        
        # Formatting weaknesses
        weaknesses = {}
        if weak4 and weak4 != '-':
            # Remove (4배) suffix if present
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
        
        if not types:
            continue
            
        if no in pokemon_map:
            p = pokemon_map[no]
            p['name'] = name
            p['types'] = types
            p['weaknesses'] = weaknesses
            updated_count += 1
        else:
            # New pokemon
            new_p = {
                "no": no,
                "name": name,
                "types": types,
                "weaknesses": weaknesses
            }
            # Try to infer generation if possible, or leave it
            # For simplicity, we just add it
            all_pokemon.append(new_p)
            pokemon_map[no] = new_p
            added_count += 1
            
    # Sort all_pokemon by 'no' if they are numeric
    def get_sort_key(p):
        no_str = str(p.get('no', '0'))
        # Handle cases like "773-1"
        match = re.search(r'(\d+)', no_str)
        if match:
            return int(match.group(1))
        return 9999
        
    all_pokemon.sort(key=get_sort_key)
    existing_data['all_pokemon'] = all_pokemon
    
    print(f"Pokemon Data: Updated {updated_count}, Added {added_count} entries.")
    return existing_data

def process_raid_data(csv_content, existing_data):
    if not csv_content:
        return existing_data
    
    reader = csv.reader(io.StringIO(csv_content))
    header = next(reader)
    
    raid_counters = {}
    
    for row in reader:
        if not row or len(row) < 4:
            continue
            
        boss = row[0].strip()
        if not boss:
            continue
            
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
        
    existing_data['raid_counters'] = raid_counters
    print(f"Raid Data: Updated counters for {len(raid_counters)} bosses.")
    return existing_data

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')
    
    # URLs
    pokemon_url = "https://docs.google.com/spreadsheets/d/1IH8rDfDMATG-nnQ7B0HexoIR0B2J152muONxLi1KE9M/export?format=csv&gid=747431545"
    raid_url = "https://docs.google.com/spreadsheets/d/1gAdoMc5Aaqt_TCQJnMMEfdoMbKNYIeRAhu0HtUezM70/export?format=csv&gid=0"
    
    # Load existing data
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"all_pokemon": [], "raid_counters": {}, "tier_data": [], "beginner_list": []}
        
    # Update Pokemon Info
    pokemon_csv = download_csv(pokemon_url)
    data = process_pokemon_data(pokemon_csv, data)
    
    # Update Raid Info
    raid_csv = download_csv(raid_url)
    data = process_raid_data(raid_csv, data)
    
    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # Save JS
    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print("\n✅ Update completed successfully!")
    print(f"Files updated: \n- {json_path}\n- {js_path}")

if __name__ == "__main__":
    main()
