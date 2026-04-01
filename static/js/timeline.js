// Timeline JavaScript

// Load timeline events
function loadTimeline() {
    const startYear = document.getElementById('start-year').value;
    const endYear = document.getElementById('end-year').value;
    
    const container = document.getElementById('timeline-events');
    container.innerHTML = '<div class="loading">LOADING TIMELINE DATA...</div>';
    
    fetch(`/timeline/api/events?start_year=${startYear}&end_year=${endYear}`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = '<div class="info-text">No events found for selected period</div>';
                return;
            }
            
            data.forEach(event => {
                const eventEl = createTimelineEvent(event);
                container.appendChild(eventEl);
            });
        })
        .catch(error => {
            console.error('Error loading timeline:', error);
            container.innerHTML = '<div class="info-text">Error loading timeline data</div>';
        });
}

// Create timeline event element
function createTimelineEvent(event) {
    const div = document.createElement('div');
    div.className = 'timeline-event';
    
    const date = new Date(event.date);
    const dateStr = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const typeIcon = event.type === 'battle' ? '⚔' : '📋';
    const sideColor = event.side === 'allies' ? '#CC6666' : 
                     event.side === 'axis' ? '#8B3A3A' : '#666666';
    
    let content = `
        <div class="event-date">${dateStr}</div>
        <div class="event-name">${typeIcon} ${event.name}</div>
    `;
    
    if (event.code_name) {
        content += `<div style="font-size: 0.85rem; color: ${sideColor}; margin-bottom: 0.5rem">
            CODE: ${event.code_name}
        </div>`;
    }
    
    if (event.location) {
        content += `<div style="font-size: 0.85rem; color: #999; margin-bottom: 0.5rem">
            📍 ${event.location}
        </div>`;
    }
    
    if (event.victor) {
        content += `<div style="font-size: 0.85rem; color: ${event.victor === 'allies' ? '#CC6666' : '#8B3A3A'}; margin-bottom: 0.5rem">
            VICTOR: ${event.victor.toUpperCase()}
        </div>`;
    }
    
    if (event.outcome) {
        const outcomeColor = event.outcome === 'success' ? '#CC6666' : 
                           event.outcome === 'failure' ? '#8B3A3A' : '#A05252';
        content += `<div style="font-size: 0.85rem; color: ${outcomeColor}; margin-bottom: 0.5rem">
            OUTCOME: ${event.outcome.toUpperCase()}
        </div>`;
    }
    
    if (event.description) {
        content += `<div class="event-description">${event.description}</div>`;
    }
    
    div.innerHTML = content;
    return div;
}

// Load timeline on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTimeline();
    
    // Reload when year selection changes
    document.getElementById('start-year').addEventListener('change', loadTimeline);
    document.getElementById('end-year').addEventListener('change', loadTimeline);
});

