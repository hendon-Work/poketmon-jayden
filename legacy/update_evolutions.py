import concurrent.futures
import requests
import json
import os

def fetch_species_data(pid):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pid}/"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return None

def fetch_chain(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        pass
    return None

def get_korean_name(species):
    return next((n['name'] for n in species['names'] if n['language']['name'] == 'ko'), species['name'])

def update_evolutions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    all_pokemon = data.get('all_pokemon', [])
    
    base_ids = set()
    for p in all_pokemon:
        no = str(p['no']).split('-')[0].strip()
        if no.isdigit():
            num = int(no)
            if num < 10000:
                base_ids.add(num)
                
    print(f"Fetching species data for {len(base_ids)} pokemons...")
    
    species_data = {}
    chain_urls = set()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_species_data, pid): pid for pid in base_ids}
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            if res:
                ko_name = get_korean_name(res)
                en_name = res['name']
                species_data[en_name] = ko_name
                if 'evolution_chain' in res and res['evolution_chain']:
                    chain_urls.add(res['evolution_chain']['url'])
            if (idx + 1) % 50 == 0:
                print(f"Species progress: {idx + 1}/{len(base_ids)}")
                
    print(f"Fetching {len(chain_urls)} evolution chains...")
    evo_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        chain_futures = {executor.submit(fetch_chain, url): url for url in chain_urls}
        for idx, future in enumerate(concurrent.futures.as_completed(chain_futures)):
            chain_data = future.result()
            if chain_data:
                def traverse(node, current_path):
                    en_name = node['species']['name']
                    ko_name = species_data.get(en_name, en_name)
                    path = current_path + [ko_name]
                    if not node['evolves_to']:
                        for _name in path:
                            if _name not in evo_map or len(evo_map[_name]) < len(path):
                                evo_map[_name] = path
                    else:
                        for child in node['evolves_to']:
                            traverse(child, path)
                            
                traverse(chain_data['chain'], [])
            if (idx + 1) % 50 == 0:
                print(f"Chains progress: {idx + 1}/{len(chain_urls)}")
                
    # Ensure old/stale evolutions are removed before assigning
    for p in all_pokemon:
        if 'evolution' in p:
            del p['evolution']

    updated_count = 0
    for p in all_pokemon:
        p_name = p['name']
        core_name = p_name
        for pre in ["알로라 ", "가라르 ", "히스이 ", "팔데아 ", "메가 ", "그림자 "]:
            if core_name.startswith(pre):
                core_name = core_name[len(pre):]
                
        # Handle special cases where stripping was wrong or form names
        # Actually form names like "화이트 큐레무" need to be stripped to "큐레무"
        for pre in ["화이트 ", "블랙 ", "원시 ", "알로라 ", "가라르 ", "히스이 ", "팔데아 ", "메가 "]:
            if core_name.startswith(pre):
                core_name = core_name[len(pre):]
        
        # Handle suffixes like " (기준)" or " (투쟁종)"
        if " (" in core_name:
            core_name = core_name.split(" (")[0]
        
        if core_name in evo_map:
            chain = evo_map[core_name]
            if len(chain) > 1:
                p['evolution'] = " ➔ ".join(chain)
                updated_count += 1
                
    data['all_pokemon'] = all_pokemon
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Updated {updated_count} evolutions!")

if __name__ == '__main__':
    update_evolutions()
