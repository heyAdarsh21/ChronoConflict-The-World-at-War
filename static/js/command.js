// Command & Leadership module

const leaderState = {
    country: '',
    role: '',
    search: '',
    page: 1,
    perPage: 12,
    countries: [],
};

const leaderGrid = document.getElementById('leader-grid');
const leaderDetail = document.getElementById('leader-detail');
const nationFilterEl = document.getElementById('nation-filter');
const roleChips = document.querySelectorAll('.filter-chip');
const searchInput = document.getElementById('leader-search');

async function fetchLeaders() {
    leaderGrid.innerHTML = '<div class="loading">COMPILING DOSSIERS...</div>';

    const params = new URLSearchParams();
    if (leaderState.country) params.append('country', leaderState.country);
    if (leaderState.role) params.append('role_type', leaderState.role);
    if (leaderState.search) params.append('q', leaderState.search);
    params.append('page', leaderState.page);
    params.append('per_page', leaderState.perPage);

    try {
        const response = await fetch(`/command/api/leaders?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to load leaders');
        const data = await response.json();

        leaderState.countries = data.countries || [];
        renderNationFilters();
        renderLeaders(data.leaders || []);
    } catch (error) {
        console.error('Error loading leaders:', error);
        leaderGrid.innerHTML = '<div class="info-text">Unable to retrieve dossiers.</div>';
    }
}

function renderNationFilters() {
    if (!nationFilterEl) return;
    nationFilterEl.innerHTML = '';

    const allButton = document.createElement('button');
    allButton.className = `filter-chip ${!leaderState.country ? 'chip-active' : ''}`;
    allButton.textContent = 'All Nations';
    allButton.addEventListener('click', () => {
        leaderState.country = '';
        fetchLeaders();
    });
    nationFilterEl.appendChild(allButton);

    leaderState.countries.forEach((country) => {
        const button = document.createElement('button');
        button.className = `filter-chip ${leaderState.country === country ? 'chip-active' : ''}`;
        button.textContent = country;
        button.addEventListener('click', () => {
            leaderState.country = country === leaderState.country ? '' : country;
            fetchLeaders();
        });
        nationFilterEl.appendChild(button);
    });
}

function renderLeaders(leaders) {
    if (!leaderGrid) return;

    if (leaders.length === 0) {
        leaderGrid.innerHTML = '<div class="info-text">No dossiers match the current filters.</div>';
        return;
    }

    const fragment = document.createDocumentFragment();

    leaders.forEach((leader) => {
        const card = document.createElement('article');
        card.className = 'leader-card';
        card.dataset.id = leader.id;
        card.innerHTML = `
            <div class="leader-portrait" style="background-image: url('${leader.portrait_url || 'img/leaders/placeholder.jpg'}')">
                <div class="leader-overlay">
                    <span>${leader.title || ''}</span>
                    <span>${leader.country}</span>
                </div>
            </div>
            <div class="leader-meta">
                <h4>${leader.name}</h4>
                <p class="leader-role">${leader.role_type ? leader.role_type.toUpperCase() : 'UNKNOWN'}</p>
                <div class="influence-meter">
                    <div class="influence-fill" style="width: ${Math.min(leader.influence_score || 0, 100)}%"></div>
                    <span class="influence-label">Influence ${Math.round(leader.influence_score || 0)}</span>
                </div>
            </div>
        `;

        card.addEventListener('click', () => {
            selectLeader(card.dataset.id, card);
        });

        fragment.appendChild(card);
    });

    leaderGrid.innerHTML = '';
    leaderGrid.appendChild(fragment);
}

async function selectLeader(id, card) {
    if (!id) return;

    document.querySelectorAll('.leader-card').forEach((c) => c.classList.remove('leader-selected'));
    card?.classList.add('leader-selected');

    leaderDetail.innerHTML = '<div class="loading">RETRIEVING COMMAND DOSSIER...</div>';

    try {
        const response = await fetch(`/command/api/leaders/${id}`);
        if (!response.ok) throw new Error('Failed to load leader detail');
        const data = await response.json();
        renderLeaderDetail(data);
    } catch (error) {
        console.error('Error retrieving leader detail:', error);
        leaderDetail.innerHTML = '<div class="info-text">Unable to load dossier.</div>';
    }
}

function parseJsonField(field) {
    if (!field) return [];
    try {
        const parsed = JSON.parse(field);
        return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
        return [];
    }
}

function renderLeaderDetail(leader) {
    if (!leaderDetail) return;

    const quotes = parseJsonField(leader.notable_quotes);
    const keyOperations = parseJsonField(leader.key_operations);

    const assignments = leader.assignments || [];

    leaderDetail.innerHTML = `
        <div class="dossier-header">
            <div class="dossier-portrait" style="background-image: url('${leader.portrait_url || 'img/leaders/placeholder.jpg'}')"></div>
            <div class="dossier-meta">
                <span class="dossier-label">${(leader.role_type || '').toUpperCase()}</span>
                <h2>${leader.name}</h2>
                <p class="dossier-country">${leader.title ? leader.title + ' | ' : ''}${leader.country || ''}</p>
                <div class="influence-meter influence-large">
                    <div class="influence-fill" style="width: ${Math.min(leader.influence_score || 0, 100)}%"></div>
                    <span class="influence-label">Influence ${Math.round(leader.influence_score || 0)}</span>
                </div>
            </div>
        </div>
        <div class="dossier-body">
            <section>
                <h3>Biography</h3>
                <p>${leader.biography || 'No biography available.'}</p>
            </section>
            <section>
                <h3>Ideological Notes</h3>
                <p>${leader.ideology || 'Classified / Unknown'}</p>
            </section>
            <section>
                <h3>Operational Influence</h3>
                <ul class="operation-list">
                    ${keyOperations.map((op) => `<li><span class="op-tag">${op}</span></li>`).join('') || '<li>No recorded operations.</li>'}
                </ul>
            </section>
            <section>
                <h3>Command Assignments</h3>
                <div class="assignment-list">
                    ${assignments.map(renderAssignmentCard).join('') || '<p>No active assignments recorded.</p>'}
                </div>
            </section>
            <section>
                <h3>Quotes &amp; Directives</h3>
                <div class="quote-feed">
                    ${quotes.map((quote) => `<p class="quote-line">“${quote}”</p>`).join('') || '<p>No quotes archived.</p>'}
                </div>
            </section>
        </div>
    `;
}

function renderAssignmentCard(assignment) {
    const context = assignment.context || {};
    const timespan = [assignment.start_date, assignment.end_date]
        .filter(Boolean)
        .map((date) => new Date(date).getFullYear())
        .join(' – ');

    let contextLabel = 'Unknown Theatre';
    if (context.type === 'operation') {
        contextLabel = `Operation ${context.name || 'Classified'}${context.code_name ? ` (${context.code_name})` : ''}`;
    } else if (context.type === 'campaign') {
        contextLabel = `Campaign ${context.name || 'Classified'}`;
    }

    return `
        <article class="assignment-card">
            <div class="assignment-header">
                <span class="assignment-position">${assignment.position || 'Unknown Role'}</span>
                <span class="assignment-period">${timespan || 'Unknown Period'}</span>
            </div>
            <div class="assignment-context">${contextLabel}</div>
            <p class="assignment-notes">${assignment.notes || 'No additional notes.'}</p>
        </article>
    `;
}

function initCommandModule() {
    if (!leaderGrid) return;

    // Attach role filters
    roleChips.forEach((chip) => {
        chip.addEventListener('click', () => {
            roleChips.forEach((c) => c.classList.remove('chip-active'));
            chip.classList.add('chip-active');
            leaderState.role = chip.dataset.role || '';
            fetchLeaders();
        });
    });

    // Search input debounce
    let searchTimeout = null;
    searchInput?.addEventListener('input', (event) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            leaderState.search = event.target.value.trim();
            fetchLeaders();
        }, 400);
    });

    fetchLeaders();
}

document.addEventListener('DOMContentLoaded', initCommandModule);

