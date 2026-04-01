// Simulation JavaScript

let currentSimulation = null;

// Initialize simulation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scenario-form');
    form.addEventListener('submit', startSimulation);
});

// Start simulation
function startSimulation(e) {
    e.preventDefault();
    
    const scenarioName = document.getElementById('scenario-name').value;
    const startYear = document.getElementById('start-year').value;
    const side = document.getElementById('side').value;
    
    fetch('/simulation/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            scenario_name: scenarioName,
            start_year: parseInt(startYear),
            side: side
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentSimulation = data;
        document.getElementById('decision-panel').style.display = 'block';
        
        displayOutcome({
            success: true,
            message: `Simulation "${scenarioName}" started. Year: ${startYear}, Side: ${side.toUpperCase()}`,
            simulation_id: data.simulation_id
        });
    })
    .catch(error => {
        console.error('Error starting simulation:', error);
        alert('Failed to start simulation');
    });
}

// Show decision form
function showDecisionForm(decisionType) {
    const container = document.getElementById('decision-form-container');
    
    let formHTML = '';
    
    switch(decisionType) {
        case 'resource_allocation':
            formHTML = `
                <div class="simulation-form">
                    <div class="form-group">
                        <label>RESOURCE TYPE</label>
                        <select id="resource-type" class="form-input">
                            <option value="oil">Oil</option>
                            <option value="steel">Steel</option>
                            <option value="manpower">Manpower</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>AMOUNT</label>
                        <input type="number" id="resource-amount" class="form-input" value="1000" min="100" step="100">
                    </div>
                    <div class="form-group">
                        <label>TARGET</label>
                        <select id="resource-target" class="form-input">
                            <option value="production">Production</option>
                            <option value="military">Military</option>
                            <option value="research">Research</option>
                        </select>
                    </div>
                    <button class="btn-military btn-primary" onclick="makeDecision('resource_allocation')">
                        EXECUTE
                    </button>
                </div>
            `;
            break;
            
        case 'espionage':
            formHTML = `
                <div class="simulation-form">
                    <div class="form-group">
                        <label>TARGET NATION</label>
                        <select id="espionage-target" class="form-input">
                            <option value="Germany">Germany</option>
                            <option value="Japan">Japan</option>
                            <option value="Italy">Italy</option>
                            <option value="USSR">USSR</option>
                            <option value="USA">USA</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>MISSION TYPE</label>
                        <select id="espionage-type" class="form-input">
                            <option value="intelligence">Intelligence Gathering</option>
                            <option value="sabotage">Sabotage</option>
                            <option value="propaganda">Propaganda</option>
                        </select>
                    </div>
                    <button class="btn-military btn-primary" onclick="makeDecision('espionage')">
                        LAUNCH MISSION
                    </button>
                </div>
            `;
            break;
            
        case 'military_action':
            formHTML = `
                <div class="simulation-form">
                    <div class="form-group">
                        <label>OPERATION TYPE</label>
                        <select id="operation-type" class="form-input">
                            <option value="offensive">Offensive</option>
                            <option value="defensive">Defensive</option>
                            <option value="raid">Raid</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>LOCATION</label>
                        <input type="text" id="operation-location" class="form-input" placeholder="Enter location">
                    </div>
                    <div class="form-group">
                        <label>FORCES</label>
                        <input type="number" id="operation-forces" class="form-input" value="5000" min="1000" step="1000">
                    </div>
                    <button class="btn-military btn-primary" onclick="makeDecision('military_action')">
                        EXECUTE OPERATION
                    </button>
                </div>
            `;
            break;
            
        case 'diplomacy':
            formHTML = `
                <div class="simulation-form">
                    <div class="form-group">
                        <label>ACTION</label>
                        <select id="diplomacy-action" class="form-input">
                            <option value="negotiate">Negotiate Treaty</option>
                            <option value="alliance">Form Alliance</option>
                            <option value="trade">Trade Agreement</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>TARGET NATION</label>
                        <select id="diplomacy-target" class="form-input">
                            <option value="USA">USA</option>
                            <option value="USSR">USSR</option>
                            <option value="United Kingdom">United Kingdom</option>
                            <option value="Germany">Germany</option>
                            <option value="Japan">Japan</option>
                        </select>
                    </div>
                    <button class="btn-military btn-primary" onclick="makeDecision('diplomacy')">
                        INITIATE DIPLOMACY
                    </button>
                </div>
            `;
            break;
    }
    
    container.innerHTML = formHTML;
}

// Make decision
function makeDecision(decisionType) {
    if (!currentSimulation) {
        alert('Please start a simulation first');
        return;
    }
    
    let decisionData = {};
    
    switch(decisionType) {
        case 'resource_allocation':
            decisionData = {
                resource: document.getElementById('resource-type').value,
                amount: parseInt(document.getElementById('resource-amount').value),
                target: document.getElementById('resource-target').value
            };
            break;
        case 'espionage':
            decisionData = {
                target: document.getElementById('espionage-target').value,
                mission_type: document.getElementById('espionage-type').value
            };
            break;
        case 'military_action':
            decisionData = {
                operation_type: document.getElementById('operation-type').value,
                location: document.getElementById('operation-location').value,
                forces: parseInt(document.getElementById('operation-forces').value)
            };
            break;
        case 'diplomacy':
            decisionData = {
                action: document.getElementById('diplomacy-action').value,
                target_nation: document.getElementById('diplomacy-target').value
            };
            break;
    }
    
    fetch('/simulation/decision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            simulation_id: currentSimulation.simulation_id,
            decision_type: decisionType,
            decision_data: decisionData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        displayOutcome(data.outcome);
    })
    .catch(error => {
        console.error('Error making decision:', error);
        alert('Failed to process decision');
    });
}

// Display outcome
function displayOutcome(outcome) {
    const container = document.getElementById('outcome-display');
    
    const outcomeClass = outcome.success ? 'outcome-success' : 'outcome-failure';
    const timestamp = new Date().toLocaleTimeString('en-US', {hour12: false});
    
    const outcomeEl = document.createElement('div');
    outcomeEl.className = `outcome-item ${outcomeClass}`;
    outcomeEl.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem">
            <strong>${outcome.success ? '✓ SUCCESS' : '✗ FAILURE'}</strong>
            <span style="font-size: 0.85rem; color: #999">${timestamp}</span>
        </div>
        <div style="margin-bottom: 0.5rem">${outcome.message}</div>
        ${outcome.impact ? `
            <div style="font-size: 0.85rem; margin-top: 0.5rem">
                <strong>IMPACT:</strong>
                ${Object.keys(outcome.impact).map(key => 
                    `${key}: ${outcome.impact[key] > 0 ? '+' : ''}${outcome.impact[key]}`
                ).join(', ')}
            </div>
        ` : ''}
        ${outcome.casualties !== undefined ? `
            <div style="font-size: 0.85rem; color: #ff0000; margin-top: 0.5rem">
                CASUALTIES: ${outcome.casualties}
            </div>
        ` : ''}
        ${outcome.intelligence_gained ? `
            <div style="font-size: 0.85rem; color: #CC6666; margin-top: 0.5rem">
                INTELLIGENCE GAINED: ${outcome.intelligence_gained}
            </div>
        ` : ''}
    `;
    
    container.insertBefore(outcomeEl, container.firstChild);
    
    // Keep only last 10 outcomes
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

