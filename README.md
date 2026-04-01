# WW2 Intelligence Operations Simulator

A comprehensive web application simulating World War 2 intelligence, strategy, and wartime decision-making between Axis and Allied powers. Features interactive data visualization, narrative interactivity, and historical accuracy with a dystopian military UI inspired by 1940s command centers.

## Features

### 🎯 Core Functionality

- **War Dashboard**: Interactive command center with global map visualization, resource meters, and intelligence feed
- **Historical Timeline**: Chronological viewer of battles and operations (1939-1945)
- **Strategy Simulation**: Make strategic decisions as Axis or Allies and see alternate outcomes
- **Database Analytics**: Store and visualize WW2 data including battles, operations, resources, and territories
- **User System**: Login/register system for saving simulation progress

### 🎨 Design

- **Dystopian Military Theme**: Black, army green, steel gray color palette
- **CRT Terminal Aesthetics**: Scanlines, noise effects, typewriter animations
- **Interactive Maps**: Leaflet.js integration for battlefront visualization
- **Real-time Updates**: Live intelligence feed and resource monitoring

## Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database management
- **SQLite**: Database (can be upgraded to PostgreSQL/MySQL)

### Frontend
- **HTML5/CSS3/JavaScript**: Core web technologies
- **Leaflet.js**: Interactive map visualization
- **Chart.js**: Data visualization (ready for integration)
- **Custom CSS**: Military-themed styling with CRT effects

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "WWII Cursor"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python app.py
   ```
   The database will be automatically created and seeded with initial data on first run.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

## Usage

### Getting Started

1. **Landing Page**: Start at the main page with cinematic introduction
2. **Register/Login**: Create an account or login to access the dashboard
3. **Dashboard**: View the global war map, resource intelligence, and live intelligence feed
4. **Timeline**: Explore historical events by year range (1939-1945)
5. **Simulation**: Start a strategy simulation and make decisions to see alternate outcomes

### User Roles

- **Historian**: Focus on data analysis and historical exploration
- **Commander**: Full access to simulation mode for strategic decision-making

### Simulation Mode

1. Create a scenario with a name, start year, and side (Axis/Allies)
2. Make strategic decisions:
   - **Resource Allocation**: Allocate oil, steel, or manpower
   - **Espionage**: Launch intelligence missions
   - **Military Action**: Execute offensive or defensive operations
   - **Diplomacy**: Negotiate treaties or form alliances
3. View outcomes and track your decisions

## Project Structure

```
WWII Cursor/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── seed_data.py           # Database seeding script
├── requirements.txt       # Python dependencies
├── routes/                # Route blueprints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── dashboard.py       # Dashboard routes
│   ├── timeline.py        # Timeline routes
│   ├── simulation.py      # Simulation routes
│   └── api.py             # API endpoints
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template
│   ├── index.html         # Landing page
│   ├── auth/              # Authentication templates
│   ├── dashboard/         # Dashboard templates
│   ├── timeline/          # Timeline templates
│   └── simulation/        # Simulation templates
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── main.js        # Main JavaScript
│       ├── dashboard.js   # Dashboard functionality
│       ├── timeline.js    # Timeline functionality
│       └── simulation.js  # Simulation functionality
└── ww2_intel.db          # SQLite database (created on first run)
```

## Database Schema

### Models

- **User**: User accounts and authentication
- **Battle**: Historical battle records with casualties and locations
- **Operation**: Military operations and campaigns
- **Resource**: Resource data by nation and date (oil, steel, manpower, GDP, morale)
- **Territory**: Territorial control data with strategic values
- **IntelligenceReport**: Intelligence and intercepted messages
- **Simulation**: User simulation sessions and decisions

## API Endpoints

### Dashboard
- `GET /dashboard/` - Main dashboard view
- `GET /dashboard/api/resources` - Resource data
- `GET /dashboard/api/territories` - Territory control data
- `GET /dashboard/api/intelligence` - Intelligence reports
- `GET /dashboard/api/battles` - Battle data

### Timeline
- `GET /timeline/` - Timeline viewer
- `GET /timeline/api/events` - Timeline events by year range

### Simulation
- `GET /simulation/` - Simulation interface
- `POST /simulation/start` - Start new simulation
- `POST /simulation/decision` - Make strategic decision

### API
- `GET /api/stats` - Overall statistics

## Customization

### Adding Historical Data

Edit `seed_data.py` to add more battles, operations, or resources:

```python
battle = Battle(
    name='Your Battle Name',
    start_date=datetime(1942, 1, 1),
    # ... other fields
)
db.session.add(battle)
```

### Styling

Modify `static/css/style.css` to customize the military theme:
- Color variables in `:root`
- Animation timings
- Layout and spacing

### Map Configuration

Update map settings in `static/js/dashboard.js`:
- Default view coordinates
- Tile layer provider
- Marker styles

## Future Enhancements

Potential features for expansion:

- **Real-time Multiplayer**: WebSocket integration for online simulations
- **Machine Learning**: AI-powered outcome prediction
- **3D Maps**: Three.js integration for immersive visualization
- **Audio**: Background radio chatter and ambient sounds
- **Advanced Analytics**: More detailed charts and graphs
- **Export Functionality**: Save simulation results as reports

## Data Sources

The application includes sample historical data. For production use, consider integrating:

- Historical battle databases
- WW2 casualty records
- Economic and resource data from the period
- Declassified intelligence documents

## License

This project is for educational and demonstration purposes.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional historical data
- Enhanced visualization
- Performance optimization
- Mobile responsiveness
- Accessibility features

## Support

For issues or questions, please check the code documentation or create an issue in the project repository.

---

**CLASSIFIED // TOP SECRET // NOFORN**

*"In war, truth is the first casualty." - Aeschylus*

