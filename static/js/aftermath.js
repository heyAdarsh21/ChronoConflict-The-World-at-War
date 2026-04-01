// Aftermath & War Crimes module

const aftermathState = {
    startYear: null,
    endYear: null,
    category: '',
    region: '',
};

const feedEl = document.getElementById('aftermath-feed');
const modalEl = document.getElementById('aftermath-modal');
const modalBody = document.getElementById('modal-body');
const categoryChipsEl = document.getElementById('category-chips');
const regionSelect = document.getElementById('region-select');
const periodButtons = document.querySelectorAll('.period-chip');

async function fetchEvents() {
    if (!feedEl) return;
    feedEl.innerHTML = '<div class="loading">PULLING ARCHIVAL EVIDENCE...</div>';

    const params = new URLSearchParams();
    if (aftermathState.startYear) params.append('start_year', aftermathState.startYear);
    if (aftermathState.endYear) params.append('end_year', aftermathState.endYear);
    if (aftermathState.category) params.append('category', aftermathState.category);
    if (aftermathState.region) params.append('region', aftermathState.region);

    try {
        const response = await fetch(`/aftermath/api/events?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to load events');
        const data = await response.json();
        renderCategories(data.categories || []);
        renderEvents(data.events || []);
    } catch (error) {
        console.error('Error loading aftermath data:', error);
        feedEl.innerHTML = '<div class="info-text">Unable to retrieve archival records.</div>';
    }
}

function renderCategories(categories) {
    if (!categoryChipsEl) return;
    categoryChipsEl.innerHTML = '';

    const allChip = document.createElement('button');
    allChip.className = `period-chip ${!aftermathState.category ? 'chip-active' : ''}`;
    allChip.textContent = 'All categories';
    allChip.addEventListener('click', () => {
        aftermathState.category = '';
        fetchEvents();
    });
    categoryChipsEl.appendChild(allChip);

    categories.forEach((cat) => {
        const chip = document.createElement('button');
        chip.className = `period-chip ${aftermathState.category === cat ? 'chip-active' : ''}`;
        chip.textContent = cat.replace('_', ' ').toUpperCase();
        chip.addEventListener('click', () => {
            aftermathState.category = aftermathState.category === cat ? '' : cat;
            fetchEvents();
        });
        categoryChipsEl.appendChild(chip);
    });
}

function renderEvents(events) {
    if (events.length === 0) {
        feedEl.innerHTML = '<div class="info-text">No archival events for the selected filters.</div>';
        return;
    }

    const fragment = document.createDocumentFragment();

    events.forEach((event) => {
        const card = document.createElement('article');
        card.className = 'aftermath-card';
        card.innerHTML = `
            <div class="card-overlay"></div>
            <div class="card-heading">
                <span class="card-date">${formatDate(event.event_date)}</span>
                <span class="card-region">${event.region || 'Unknown theatre'}</span>
            </div>
            <h2 class="card-title">${event.title}</h2>
            <p class="card-location">${event.location || 'Classified location'}</p>
            <p class="card-summary">${summarizeText(event.description)}</p>
            <div class="card-footer">
                <span class="card-category">${(event.category || 'Uncategorized').replace('_', ' ')}</span>
                <button class="btn-military btn-secondary" data-event-id="${event.id}">OPEN DOSSIER</button>
            </div>
        `;

        card.querySelector('button')?.addEventListener('click', () => openModal(event));
        fragment.appendChild(card);
    });

    feedEl.innerHTML = '';
    feedEl.appendChild(fragment);
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function summarizeText(text) {
    if (!text) return 'No summary available.';
    if (text.length <= 180) return text;
    return `${text.substring(0, 180)}…`;
}

function parseListField(field) {
    if (!field) return [];
    try {
        const parsed = JSON.parse(field);
        return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
        return [];
    }
}

function openModal(event) {
    if (!modalEl) return;

    const sources = parseListField(event.sources);

    const victims = event.victims ? `<p><strong>Victims:</strong> ${event.victims}</p>` : '';
    const perpetrators = event.perpetrators ? `<p><strong>Perpetrators:</strong> ${event.perpetrators}</p>` : '';

    modalBody.innerHTML = `
        <div class="modal-header">
            <div class="modal-newspaper" style="background-image: url('${event.media_url || 'img/aftermath/newspaper_texture.jpg'}')"></div>
            <div>
                <h2 class="modal-title">${event.title}</h2>
                <p class="modal-dates">${formatDate(event.event_date)}${event.end_date ? ' – ' + formatDate(event.end_date) : ''}</p>
                <p class="modal-location">${event.location || 'Classified coordinates'} (${event.region || 'Unknown region'})</p>
            </div>
        </div>
        <div class="modal-content-section">
            <h3>Summary</h3>
            <p>${event.description || 'No archival summary available.'}</p>
        </div>
        <div class="modal-content-section">
            <h3>Human Impact</h3>
            ${victims}
            ${perpetrators}
            <p><strong>Estimated casualties:</strong> ${event.death_toll ? event.death_toll.toLocaleString('en-US') : 'Classified'}</p>
        </div>
        <div class="modal-content-section">
            <h3>Sources</h3>
            <ul class="source-list">
                ${sources.map((source) => `<li>${source}</li>`).join('') || '<li>No sources provided.</li>'}
            </ul>
        </div>
    `;

    modalEl.setAttribute('aria-hidden', 'false');
    modalEl.classList.add('modal-open');
}

function closeModal() {
    if (!modalEl) return;
    modalEl.setAttribute('aria-hidden', 'true');
    modalEl.classList.remove('modal-open');
}

function handlePeriodSelection() {
    periodButtons.forEach((button) => {
        button.addEventListener('click', () => {
            periodButtons.forEach((b) => b.classList.remove('chip-active'));
            button.classList.add('chip-active');

            const range = button.dataset.range || '';
            if (!range) {
                aftermathState.startYear = null;
                aftermathState.endYear = null;
            } else {
                const [start, end] = range.split('-');
                aftermathState.startYear = parseInt(start, 10);
                aftermathState.endYear = parseInt(end, 10);
            }

            fetchEvents();
        });
    });
}

function initModalListeners() {
    modalEl?.querySelectorAll('[data-close-modal]').forEach((el) => {
        el.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
}

function initAftermathModule() {
    if (!feedEl) return;

    handlePeriodSelection();
    initModalListeners();

    regionSelect?.addEventListener('change', (event) => {
        aftermathState.region = event.target.value;
        fetchEvents();
    });

    fetchEvents();
}

document.addEventListener('DOMContentLoaded', initAftermathModule);

