// Dashboard JavaScript

let warMap;
let resourceCharts = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadResources();
    loadIntelligence();
    loadStats();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        loadIntelligence();
        loadResources();
    }, 30000);
});

// Initialize Leaflet map
function initializeMap() {
    warMap = L.map('war-map').setView([50, 20], 3);
    
    // Use a dark theme tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(warMap);
    
    // Load territories and battles
    loadTerritories();
    loadBattles();
}

// Load territories on map
function loadTerritories() {
    fetch('/dashboard/api/territories')
        .then(response => response.json())
        .then(data => {
            data.forEach(territory => {
                const color = getNationColor(territory.controlled_by);
                L.circleMarker([territory.lat, territory.lng], {
                    radius: 8,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(warMap)
                .bindPopup(`
                    <strong>${territory.name}</strong><br>
                    Controlled by: ${territory.controlled_by}<br>
                    Strategic Value: ${territory.strategic_value}/10<br>
                    Region: ${territory.region}
                `);
            });
        })
        .catch(error => console.error('Error loading territories:', error));
}

// Load battles on map
function loadBattles() {
    fetch('/dashboard/api/battles')
        .then(response => response.json())
        .then(data => {
            data.forEach(battle => {
                if (battle.lat && battle.lng) {
                    const iconColor = battle.victor === 'allies' ? '#CC6666' : '#8B3A3A';
                    L.circleMarker([battle.lat, battle.lng], {
                        radius: 12,
                        fillColor: iconColor,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.7
                    }).addTo(warMap)
                    .bindPopup(`
                        <strong>${battle.name}</strong><br>
                        Date: ${formatDate(battle.start_date)}<br>
                        Location: ${battle.location}<br>
                        Victor: ${battle.victor.toUpperCase()}<br>
                        Axis Casualties: ${formatNumber(battle.axis_casualties)}<br>
                        Allied Casualties: ${formatNumber(battle.allied_casualties)}
                    `);
                }
            });
        })
        .catch(error => console.error('Error loading battles:', error));
}

// Get color for nation
function getNationColor(nation) {
    const colors = {
        'Germany': '#8b0000',
        'USA': '#0066cc',
        'USSR': '#cc0000',
        'United Kingdom': '#006600',
        'Japan': '#ff6600',
        'Allies': '#CC6666',
        'Italy': '#008000'
    };
    return colors[nation] || '#666666';
}

// Load resource data
function loadResources() {
    fetch('/dashboard/api/resources')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('resource-charts');
            container.innerHTML = '';
            
            Object.keys(data).forEach(nation => {
                const resource = data[nation];
                const meter = createResourceMeter(nation, resource);
                container.appendChild(meter);
            });
        })
        .catch(error => console.error('Error loading resources:', error));
}

// Create resource meter
function createResourceMeter(nation, data) {
    const meter = document.createElement('div');
    meter.className = 'resource-meter';
    
    const maxValues = {
        oil: 20000,
        steel: 18000,
        manpower: 12000000,
        gdp: 250000000000,
        morale: 100,
        territory_count: 20
    };
    
    const metrics = ['oil', 'steel', 'manpower', 'morale'];
    
    meter.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 0.5rem; color: ${getNationColor(nation)}">
            ${nation.toUpperCase()}
        </div>
        ${metrics.map(metric => {
            const value = data[metric] || 0;
            const max = maxValues[metric];
            const percentage = (value / max) * 100;
            const displayValue = metric === 'manpower' ? formatNumber(value) : 
                               metric === 'oil' || metric === 'steel' ? formatNumber(value) :
                               metric === 'gdp' ? formatNumber(value) :
                               value.toFixed(1);
            
            return `
                <div class="resource-label">
                    <span>${metric.toUpperCase()}</span>
                    <span>${displayValue}</span>
                </div>
                <div class="resource-bar">
                    <div class="resource-fill" style="width: ${percentage}%"></div>
                </div>
            `;
        }).join('')}
    `;
    
    return meter;
}

// Load intelligence feed
function loadIntelligence() {
    fetch('/dashboard/api/intelligence')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('intelligence-feed');
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = '<div class="info-text">No intelligence reports available</div>';
                return;
            }
            
            data.forEach(report => {
                const reportEl = createIntelligenceReport(report);
                container.appendChild(reportEl);
            });
        })
        .catch(error => console.error('Error loading intelligence:', error));
}

// Create intelligence report element
function createIntelligenceReport(report) {
    const div = document.createElement('div');
    div.className = 'intel-report';
    
    const date = new Date(report.date);
    const dateStr = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    div.innerHTML = `
        <div class="intel-header">
            <span>${dateStr}</span>
            <span class="intel-classification">${report.classification.toUpperCase()}</span>
        </div>
        <div style="font-size: 0.75rem; color: ${getNationColor(report.side)}; margin-bottom: 0.5rem">
            SOURCE: ${report.source.toUpperCase()} | SIDE: ${report.side.toUpperCase()}
        </div>
        <div class="intel-content">${report.content}</div>
        ${report.decoded ? '<div style="margin-top: 0.5rem; font-size: 0.75rem; color: #CC6666">✓ DECODED</div>' : ''}
    `;
    
    return div;
}

// Load statistics
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-battles').textContent = data.total_battles;
            document.getElementById('total-operations').textContent = data.total_operations;
            document.getElementById('total-territories').textContent = data.total_territories;
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Refresh map
function refreshMap() {
    warMap.eachLayer(layer => {
        if (layer instanceof L.CircleMarker) {
            warMap.removeLayer(layer);
        }
    });
    loadTerritories();
    loadBattles();
}

// Refresh intelligence
function refreshIntelligence() {
    loadIntelligence();
}

// Format date helper
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format number helper
function formatNumber(num) {
    return num.toLocaleString('en-US');
}

