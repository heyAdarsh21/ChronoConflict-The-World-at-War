# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   - Open your browser to: `http://localhost:5000`
   - The database will be automatically created and seeded on first run

## First Steps

1. **Register an account:**
   - Click "REQUEST CLEARANCE" on the landing page
   - Choose your role: Historian (data analysis) or Commander (simulation mode)

2. **Explore the Dashboard:**
   - View the global war map with battles and territories
   - Monitor resource intelligence for major powers
   - Read the live intelligence feed

3. **Browse the Timeline:**
   - Navigate to the Timeline section
   - Select year ranges (1939-1945)
   - View historical battles and operations

4. **Try Simulation Mode:**
   - Create a new scenario
   - Make strategic decisions
   - See alternate outcomes

## Default Data

The application comes pre-loaded with:
- 5 major battles (Stalingrad, Normandy, Midway, Britain, Barbarossa)
- 4 military operations
- 8 strategic territories
- Resource data for 1941 and 1944
- Sample intelligence reports

## Troubleshooting

**Database not created?**
- Delete `ww2_intel.db` and restart the application
- The database will be recreated automatically

**Import errors?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.8 or higher

**Map not loading?**
- Check your internet connection (Leaflet.js requires online access for map tiles)
- The map uses CartoDB dark theme tiles

## Next Steps

- Add more historical data in `seed_data.py`
- Customize the UI in `static/css/style.css`
- Extend simulation logic in `routes/simulation.py`

