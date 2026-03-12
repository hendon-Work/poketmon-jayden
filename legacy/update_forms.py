import json
import os

def update_regional_forms():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'pokemon_data.json')
    js_path = os.path.join(base_dir, 'pokemon_data.js')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 우리가 추가할 리전폼 목록
    # 약점 계산 (pokemongo info)
    # 포켓몬고는 4배는 2.56배, 2배는 1.6배지만, 기존 포맷에 맞추어 4배, 2배로 표시
    regional_forms = [
        {
            "no": 10091,
            "name": "알로라 꼬렛",
            "types": ["악", "노말"],
            "weaknesses": {"4배": "격투", "2배": "벌레, 페어리"},
            "generation": "알로라폼"
        },
        {
            "no": 10092,
            "name": "알로라 레트라",
            "types": ["악", "노말"],
            "weaknesses": {"4배": "격투", "2배": "벌레, 페어리"},
            "generation": "알로라폼"
        },
        {
            "no": 10100,
            "name": "알로라 라이츄",
            "types": ["전기", "에스퍼"],
            "weaknesses": {"2배": "땅, 벌레, 고스트, 악"},
            "generation": "알로라폼"
        },
        {
            "no": 10101,
            "name": "알로라 모래두지",
            "types": ["얼음", "강철"],
            "weaknesses": {"4배": "격투, 불꽃", "2배": "땅"},
            "generation": "알로라폼"
        },
        {
            "no": 10102,
            "name": "알로라 고지",
            "types": ["얼음", "강철"],
            "weaknesses": {"4배": "격투, 불꽃", "2배": "땅"},
            "generation": "알로라폼"
        },
        {
            "no": 10103,
            "name": "알로라 식스테일",
            "types": ["얼음"],
            "weaknesses": {"2배": "격투, 바위, 강철, 불꽃"},
            "generation": "알로라폼"
        },
        {
            "no": 10104,
            "name": "알로라 나인테일",
            "types": ["얼음", "페어리"],
            "weaknesses": {"4배": "강철", "2배": "독, 바위, 불꽃"},
            "generation": "알로라폼"
        },
        {
            "no": 10105,
            "name": "알로라 디그다",
            "types": ["땅", "강철"],
            "weaknesses": {"2배": "격투, 땅, 불꽃, 물"},
            "generation": "알로라폼"
        },
        {
            "no": 10106,
            "name": "알로라 닥트리오",
            "types": ["땅", "강철"],
            "weaknesses": {"2배": "격투, 땅, 불꽃, 물"},
            "generation": "알로라폼"
        },
        {
            "no": 10107,
            "name": "알로라 나옹",
            "types": ["악"],
            "weaknesses": {"2배": "격투, 벌레, 페어리"},
            "generation": "알로라폼"
        },
        {
            "no": 10108,
            "name": "알로라 페르시온",
            "types": ["악"],
            "weaknesses": {"2배": "격투, 벌레, 페어리"},
            "generation": "알로라폼"
        },
        {
            "no": 10109,
            "name": "알로라 꼬마돌",
            "types": ["바위", "전기"],
            "weaknesses": {"4배": "땅", "2배": "격투, 물, 풀"},
            "generation": "알로라폼"
        },
        {
            "no": 10110,
            "name": "알로라 데구리",
            "types": ["바위", "전기"],
            "weaknesses": {"4배": "땅", "2배": "격투, 물, 풀"},
            "generation": "알로라폼"
        },
        {
            "no": 10111,
            "name": "알로라 딱구리",
            "types": ["바위", "전기"],
            "weaknesses": {"4배": "땅", "2배": "격투, 물, 풀"},
            "generation": "알로라폼"
        },
        {
            "no": 10112,
            "name": "알로라 질퍽이",
            "types": ["독", "악"],
            "weaknesses": {"2배": "땅"},
            "generation": "알로라폼"
        },
        {
            "no": 10113,
            "name": "알로라 질뻐기",
            "types": ["독", "악"],
            "weaknesses": {"2배": "땅"},
            "generation": "알로라폼"
        },
        {
            "no": 10114,
            "name": "알로라 나시",
            "types": ["풀", "드래곤"],
            "weaknesses": {"4배": "얼음", "2배": "독, 비행, 벌레, 드래곤, 페어리"},
            "generation": "알로라폼"
        },
        {
            "no": 10115,
            "name": "알로라 텅구리",
            "types": ["불꽃", "고스트"],
            "weaknesses": {"2배": "땅, 바위, 고스트, 물, 악"},
            "generation": "알로라폼"
        },
        {
            "no": 10161,
            "name": "가라르 나옹",
            "types": ["강철"],
            "weaknesses": {"2배": "격투, 땅, 불꽃"},
            "generation": "가라르폼"
        },
        {
            "no": 10162,
            "name": "가라르 포니타",
            "types": ["에스퍼"],
            "weaknesses": {"2배": "벌레, 고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10163,
            "name": "가라르 날쌩마",
            "types": ["에스퍼", "페어리"],
            "weaknesses": {"2배": "독, 고스트, 강철"},
            "generation": "가라르폼"
        },
        {
            "no": 10164,
            "name": "가라르 야돈",
            "types": ["에스퍼"],
            "weaknesses": {"2배": "벌레, 고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10165,
            "name": "가라르 야도란",
            "types": ["독", "에스퍼"],
            "weaknesses": {"2배": "땅, 고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10166,
            "name": "가라르 파오리",
            "types": ["격투"],
            "weaknesses": {"2배": "비행, 에스퍼, 페어리"},
            "generation": "가라르폼"
        },
        {
            "no": 10167,
            "name": "가라르 또가스",
            "types": ["독", "페어리"],
            "weaknesses": {"2배": "땅, 강철, 에스퍼"},
            "generation": "가라르폼"
        },
        {
            "no": 10168,
            "name": "가라르 마임맨",
            "types": ["얼음", "에스퍼"],
            "weaknesses": {"2배": "바위, 벌레, 고스트, 강철, 불꽃, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10169,
            "name": "가라르 프리져",
            "types": ["에스퍼", "비행"],
            "weaknesses": {"2배": "바위, 고스트, 전기, 얼음, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10170,
            "name": "가라르 썬더",
            "types": ["격투", "비행"],
            "weaknesses": {"2배": "비행, 전기, 에스퍼, 얼음, 페어리"},
            "generation": "가라르폼"
        },
        {
            "no": 10171,
            "name": "가라르 파이어",
            "types": ["악", "비행"],
            "weaknesses": {"2배": "바위, 전기, 얼음, 페어리"},
            "generation": "가라르폼"
        },
        {
            "no": 10172,
            "name": "가라르 야도킹",
            "types": ["독", "에스퍼"],
            "weaknesses": {"2배": "땅, 고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10173,
            "name": "가라르 코산호",
            "types": ["고스트"],
            "weaknesses": {"2배": "고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10174,
            "name": "가라르 지그제구리",
            "types": ["악", "노말"],
            "weaknesses": {"4배": "격투", "2배": "벌레, 페어리"},
            "generation": "가라르폼"
        },
        {
            "no": 10175,
            "name": "가라르 직구리",
            "types": ["악", "노말"],
            "weaknesses": {"4배": "격투", "2배": "벌레, 페어리"},
            "generation": "가라르폼"
        },
        {
            "no": 10177,
            "name": "가라르 달막화",
            "types": ["얼음"],
            "weaknesses": {"2배": "격투, 바위, 강철, 불꽃"},
            "generation": "가라르폼"
        },
        {
            "no": 10178,
            "name": "가라르 불비달마",
            "types": ["얼음"],
            "weaknesses": {"2배": "격투, 바위, 강철, 불꽃"},
            "generation": "가라르폼"
        },
        {
            "no": 10179,
            "name": "가라르 데스마스",
            "types": ["땅", "고스트"],
            "weaknesses": {"2배": "물, 풀, 얼음, 고스트, 악"},
            "generation": "가라르폼"
        },
        {
            "no": 10180,
            "name": "가라르 메더",
            "types": ["땅", "강철"],
            "weaknesses": {"2배": "격투, 땅, 불꽃, 물"},
            "generation": "가라르폼"
        },
        {
            "no": 10229,
            "name": "히스이 가디",
            "types": ["불꽃", "바위"],
            "weaknesses": {"4배": "물, 땅", "2배": "격투, 바위"},
            "generation": "히스이폼"
        },
        {
            "no": 10230,
            "name": "히스이 윈디",
            "types": ["불꽃", "바위"],
            "weaknesses": {"4배": "물, 땅", "2배": "격투, 바위"},
            "generation": "히스이폼"
        },
        {
            "no": 10231,
            "name": "히스이 찌리리공",
            "types": ["전기", "풀"],
            "weaknesses": {"2배": "독, 벌레, 불꽃, 얼음"},
            "generation": "히스이폼"
        },
        {
            "no": 10232,
            "name": "히스이 붐볼",
            "types": ["전기", "풀"],
            "weaknesses": {"2배": "독, 벌레, 불꽃, 얼음"},
            "generation": "히스이폼"
        },
        {
            "no": 10233,
            "name": "히스이 블레이범",
            "types": ["불꽃", "고스트"],
            "weaknesses": {"2배": "땅, 바위, 고스트, 물, 악"},
            "generation": "히스이폼"
        },
        {
            "no": 10234,
            "name": "히스이 침바루",
            "types": ["악", "독"],
            "weaknesses": {"2배": "땅"},
            "generation": "히스이폼"
        },
        {
            "no": 10235,
            "name": "히스이 포푸니",
            "types": ["격투", "독"],
            "weaknesses": {"4배": "에스퍼", "2배": "비행, 땅"},
            "generation": "히스이폼"
        },
        {
            "no": 10236,
            "name": "히스이 대검귀",
            "types": ["물", "악"],
            "weaknesses": {"2배": "격투, 벌레, 풀, 전기, 페어리"},
            "generation": "히스이폼"
        },
        {
            "no": 10237,
            "name": "히스이 드레디어",
            "types": ["풀", "격투"],
            "weaknesses": {"4배": "비행", "2배": "독, 불꽃, 에스퍼, 얼음, 페어리"},
            "generation": "히스이폼"
        },
        {
            "no": 10238,
            "name": "히스이 조로아",
            "types": ["노말", "고스트"],
            "weaknesses": {"2배": "악"},
            "generation": "히스이폼"
        },
        {
            "no": 10239,
            "name": "히스이 조로아크",
            "types": ["노말", "고스트"],
            "weaknesses": {"2배": "악"},
            "generation": "히스이폼"
        },
        {
            "no": 10240,
            "name": "히스이 워글",
            "types": ["에스퍼", "비행"],
            "weaknesses": {"2배": "바위, 고스트, 전기, 얼음, 악"},
            "generation": "히스이폼"
        },
        {
            "no": 10241,
            "name": "히스이 미끄네일",
            "types": ["강철", "드래곤"],
            "weaknesses": {"2배": "격투, 땅"},
            "generation": "히스이폼"
        },
        {
            "no": 10242,
            "name": "히스이 미끄래곤",
            "types": ["강철", "드래곤"],
            "weaknesses": {"2배": "격투, 땅"},
            "generation": "히스이폼"
        },
        {
            "no": 10243,
            "name": "히스이 크레베이스",
            "types": ["얼음", "바위"],
            "weaknesses": {"4배": "격투, 강철", "2배": "땅, 바위, 물, 풀"},
            "generation": "히스이폼"
        },
        {
            "no": 10244,
            "name": "히스이 모크나이퍼",
            "types": ["풀", "격투"],
            "weaknesses": {"4배": "비행", "2배": "독, 불꽃, 에스퍼, 얼음, 페어리"},
            "generation": "히스이폼"
        },
        {
            "no": 10250,
            "name": "팔데아 켄타로스 (투쟁종)",
            "types": ["격투"],
            "weaknesses": {"2배": "비행, 에스퍼, 페어리"},
            "generation": "팔데아폼"
        },
        {
            "no": 10251,
            "name": "팔데아 켄타로스 (홍련종)",
            "types": ["격투", "불꽃"],
            "weaknesses": {"2배": "비행, 땅, 물, 에스퍼"},
            "generation": "팔데아폼"
        },
        {
            "no": 10252,
            "name": "팔데아 켄타로스 (워터종)",
            "types": ["격투", "물"],
            "weaknesses": {"2배": "비행, 풀, 전기, 에스퍼, 페어리"},
            "generation": "팔데아폼"
        },
        {
            "no": 10253,
            "name": "팔데아 우파",
            "types": ["독", "땅"],
            "weaknesses": {"2배": "땅, 물, 얼음, 에스퍼"},
            "generation": "팔데아폼"
        }
    ]

    all_pokemon = data.get('all_pokemon', [])
    
    # 중복 제거 (이전에 잘못 들어간 "38-1" 같은 데이터들 삭제)
    all_pokemon = [p for p in all_pokemon if p.get('generation') not in ["알로라폼", "가라르폼", "히스이폼", "팔데아폼"]]
    
    # 새로 추가
    for form in regional_forms:
        all_pokemon.append(form)
            
    data['all_pokemon'] = all_pokemon

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # pokemon_data.js도 동일하게 반영
    # js 형태는 const pokemonData = { ... };
    js_content = f"const pokemonData = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"{len(regional_forms)}개의 리전폼 포켓몬이 (PokeAPI ID 기반으로) 추가 또는 업데이트되었습니다!")

if __name__ == '__main__':
    update_regional_forms()
