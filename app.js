
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsArea = document.getElementById('results-area');

    // Trigger search on Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    searchBtn.addEventListener('click', performSearch);

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Ensure case-insensitive search if needed, though mostly Korean
        displayResults(searchPokemon(query));
    }

    function searchPokemon(query) {
        const results = [];
        const data = POKEMON_DATA; // From pokemon_data.js

        // 1. Search in Tier Data (Specific Pokemon or Type)
        data.tier_data.forEach(typeGroup => {
            // Check if query matches Type Name (e.g. "얼음")
            if (typeGroup.Type.includes(query)) {
                results.push({
                    category: `${typeGroup.Type} 타입 티어 (Raid)`,
                    type: "table", // Flag to render as table
                    data: typeGroup.Pokémon
                });
            } else {
                // Check if query matches any Pokemon in this type
                const matchingPokemon = typeGroup.Pokémon.filter(p => p.Name.includes(query));
                if (matchingPokemon.length > 0) {
                    results.push({
                        category: `${typeGroup.Type} 타입 검색 결과`,
                        type: "table",
                        data: matchingPokemon
                    });
                }
            }
        });

        // 2. Search in Beginner List (Fallback or specific)
        const beginnerMatches = data.beginner_list.filter(p => p.name.includes(query) || p.from.includes(query));
        if (beginnerMatches.length > 0) {
            results.push({
                category: "초보자 추천 (가성비)",
                type: "text",
                content: beginnerMatches.map(p => `[${p.name}] (진화전: ${p.from})\n기술: ${p.moves}\n${p.desc}`).join('\n\n')
            });
        }

        // 3. Search detailed type descriptions (Fallback)
        Object.keys(data.types).forEach(typeName => {
            if (typeName.includes(query)) {
                // Don't duplicate if we already showed the table for this type
                if (!results.some(r => r.category.includes(typeName))) {
                    results.push({
                        category: "타입 평가",
                        type: "text",
                        content: data.types[typeName]
                    });
                }
            }
        });

        // 4. Search in All Pokemon (Pokedex info)
        if (data.all_pokemon) {
            const pokedexMatches = data.all_pokemon.filter(p => p.name.includes(query));
            if (pokedexMatches.length > 0) {
                results.push({
                    category: "도감 정보",
                    type: "pokedex",
                    data: pokedexMatches
                });
            }
        }

        return results;
    }

    function displayResults(results) {
        resultsArea.innerHTML = '';

        if (results.length === 0) {
            resultsArea.innerHTML = `
                <div class="empty-state">
                    <p>검색 결과가 없습니다.</p>
                </div>
            `;
            return;
        }

        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'card';

            let contentHtml = '';

            if (res.type === 'table') {
                contentHtml = `
                    <table>
                        <thead>
                            <tr>
                                <th>등급</th>
                                <th>이름</th>
                                <th>기술</th>
                                <th class="dps-col">DPS</th>
                                <th class="tdo-col">TDO</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${res.data.map(row => `
                                <tr>
                                    <td>${row.Grade}</td>
                                    <td>${row.Name}</td>
                                    <td>${row.Moves}</td>
                                    <td class="dps-col">${row.DPS}</td>
                                    <td class="tdo-col">${row.TDO}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else if (res.type === 'pokedex') {
                contentHtml = `
                    <table class="pokedex-table">
                        <thead>
                            <tr>
                                <th>도감번호</th>
                                <th>이름</th>
                                <th>타입</th>
                                <th>진화 트리</th>
                                <th>약점 (4배)</th>
                                <th>약점 (2배)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${res.data.map(row => `
                                <tr>
                                    <td>No.${row.no}</td>
                                    <td>${row.name}</td>
                                    <td>${row.types.join(', ')}</td>
                                    <td>${row.evolution || '-'}</td>
                                    <td class="weakness-4x">${row.weaknesses['4배'] || '-'}</td>
                                    <td class="weakness-2x">${row.weaknesses['2배'] || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else {
                contentHtml = `<div class="card-content">${res.content}</div>`;
            }

            card.innerHTML = `
                <h2>${res.category}</h2>
                ${contentHtml}
            `;

            resultsArea.appendChild(card);
        });
    }
});
