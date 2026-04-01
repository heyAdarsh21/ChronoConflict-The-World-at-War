"""
Simulation routes
"""

from flask import Blueprint, render_template, jsonify, request, session
from database import db
from models import Simulation, Resource, Territory
from datetime import datetime
import json
import random

bp = Blueprint('simulation', __name__, url_prefix='/simulation')

@bp.route('/')
def index():
    """Simulation mode interface"""
    return render_template('simulation/index.html')

@bp.route('/start', methods=['POST'])
def start_simulation():
    """Start a new simulation"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    scenario_name = data.get('scenario_name', 'Default Scenario')
    start_year = data.get('start_year', 1941)
    side = data.get('side', 'allies')
    
    simulation = Simulation(
        user_id=session['user_id'],
        scenario_name=scenario_name,
        start_year=start_year,
        side=side,
        decisions=json.dumps([]),
        outcome=json.dumps({})
    )
    db.session.add(simulation)
    db.session.commit()
    
    return jsonify({
        'simulation_id': simulation.id,
        'scenario_name': scenario_name,
        'start_year': start_year,
        'side': side
    })

@bp.route('/decision', methods=['POST'])
def make_decision():
    """Process a strategic decision"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    simulation_id = data.get('simulation_id')
    decision_type = data.get('decision_type')  # 'resource_allocation', 'espionage', 'military_action', 'diplomacy'
    decision_data = data.get('decision_data', {})
    
    simulation = Simulation.query.get(simulation_id)
    if not simulation or simulation.user_id != session['user_id']:
        return jsonify({'error': 'Simulation not found'}), 404
    
    # Load existing decisions
    decisions = json.loads(simulation.decisions or '[]')
    
    # Process decision and generate outcome
    outcome = evaluate_decision(decision_type, decision_data, simulation)
    
    # Add new decision
    decisions.append({
        'type': decision_type,
        'data': decision_data,
        'outcome': outcome,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Update simulation
    simulation.decisions = json.dumps(decisions)
    simulation.outcome = json.dumps(outcome)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'outcome': outcome,
        'decisions': decisions
    })

def evaluate_decision(decision_type, decision_data, simulation):
    """Evaluate a decision and return outcome"""
    # Simple probability-based evaluation
    base_success = 0.5
    
    if decision_type == 'resource_allocation':
        # Resource allocation decisions
        resource = decision_data.get('resource')
        amount = decision_data.get('amount', 0)
        target = decision_data.get('target', 'production')
        
        success_rate = min(0.9, base_success + (amount / 1000) * 0.1)
        success = random.random() < success_rate
        
        return {
            'success': success,
            'message': f"Resource allocation {'succeeded' if success else 'failed'}",
            'impact': {
                'production': amount * 0.1 if success else 0,
                'morale': 5 if success else -2
            }
        }
    
    elif decision_type == 'espionage':
        # Espionage missions
        target = decision_data.get('target')
        mission_type = decision_data.get('mission_type', 'intelligence')
        
        success_rate = 0.4  # Espionage is risky
        success = random.random() < success_rate
        
        return {
            'success': success,
            'message': f"Espionage mission {'succeeded' if success else 'was discovered'}",
            'intelligence_gained': random.randint(10, 50) if success else 0,
            'casualties': random.randint(0, 5) if not success else 0
        }
    
    elif decision_type == 'military_action':
        # Military operations
        operation_type = decision_data.get('operation_type')
        location = decision_data.get('location')
        forces = decision_data.get('forces', 1000)
        
        success_rate = min(0.8, base_success + (forces / 10000) * 0.2)
        success = random.random() < success_rate
        
        casualties = int(forces * random.uniform(0.1, 0.3))
        
        return {
            'success': success,
            'message': f"Military action {'succeeded' if success else 'failed'}",
            'casualties': casualties,
            'territory_gained': 1 if success else 0,
            'morale_impact': 10 if success else -5
        }
    
    elif decision_type == 'diplomacy':
        # Diplomatic actions
        action = decision_data.get('action')
        target_nation = decision_data.get('target_nation')
        
        success_rate = 0.6
        success = random.random() < success_rate
        
        return {
            'success': success,
            'message': f"Diplomatic action {'succeeded' if success else 'failed'}",
            'alliance_strength': 5 if success else -2,
            'resources_gained': random.randint(100, 500) if success else 0
        }
    
    return {
        'success': False,
        'message': 'Unknown decision type'
    }

@bp.route('/<int:simulation_id>')
def view_simulation(simulation_id):
    """View a specific simulation"""
    simulation = Simulation.query.get(simulation_id)
    if not simulation:
        return redirect(url_for('simulation.index'))
    
    return render_template('simulation/view.html', simulation=simulation)

