"""Year-by-year resource snapshots for major WWII nations (1939-1945).

Units:
  oil       – thousands of barrels/day equivalent (energy output proxy)
  steel     – thousands of metric tons/year
  manpower  – total military personnel (active)
  food      – index (100 = pre-war baseline sufficiency)
  ammunition – index (100 = full operational requirements)
  aircraft  – total military aircraft inventory
  naval_tonnage – warship displacement (thousands of long tons)
  rubber    – thousands of metric tons/year

Metrics (JSONB):
  gdp       – nominal GDP in 1944 USD (billions)
  morale    – 0-100 composite index
  cinc      – Correlates of War Composite Index of National Capability
  territory_count – controlled/active theater regions
"""

from __future__ import annotations

RESOURCE_TYPES = [
    ("oil", "Oil / Energy", "thousand barrels/day", "strategic"),
    ("steel", "Steel / Industrial Output", "thousand metric tons", "strategic"),
    ("manpower", "Military Manpower", "personnel", "human"),
    ("food", "Food Supply", "index", "logistic"),
    ("ammunition", "Ammunition & Ordnance", "index", "logistic"),
    ("aircraft", "Military Aircraft", "units", "equipment"),
    ("naval_tonnage", "Naval Tonnage", "thousand tons", "equipment"),
    ("rubber", "Rubber Supply", "thousand metric tons", "strategic"),
]

# fmt: off
RESOURCE_SNAPSHOTS = {
    "Germany": [
        {"year": 1939, "oil": 5800, "steel": 22500, "manpower": 4500000, "food": 95, "ammunition": 90, "aircraft": 4201, "naval_tonnage": 350, "rubber": 80, "gdp": 384, "morale": 85, "cinc": 0.142, "territory_count": 5},
        {"year": 1940, "oil": 6200, "steel": 21500, "manpower": 5760000, "food": 88, "ammunition": 85, "aircraft": 6600, "naval_tonnage": 380, "rubber": 70, "gdp": 392, "morale": 90, "cinc": 0.148, "territory_count": 12},
        {"year": 1941, "oil": 6800, "steel": 20800, "manpower": 7260000, "food": 82, "ammunition": 80, "aircraft": 7200, "naval_tonnage": 400, "rubber": 55, "gdp": 400, "morale": 82, "cinc": 0.151, "territory_count": 18},
        {"year": 1942, "oil": 6900, "steel": 20500, "manpower": 8600000, "food": 75, "ammunition": 75, "aircraft": 8400, "naval_tonnage": 360, "rubber": 45, "gdp": 395, "morale": 72, "cinc": 0.146, "territory_count": 20},
        {"year": 1943, "oil": 6500, "steel": 19000, "manpower": 9500000, "food": 68, "ammunition": 78, "aircraft": 10500, "naval_tonnage": 310, "rubber": 35, "gdp": 388, "morale": 60, "cinc": 0.138, "territory_count": 16},
        {"year": 1944, "oil": 4200, "steel": 16000, "manpower": 9400000, "food": 60, "ammunition": 65, "aircraft": 12000, "naval_tonnage": 250, "rubber": 20, "gdp": 370, "morale": 48, "cinc": 0.118, "territory_count": 10},
        {"year": 1945, "oil": 1500, "steel": 5000, "manpower": 7800000, "food": 40, "ammunition": 35, "aircraft": 3000, "naval_tonnage": 100, "rubber": 5, "gdp": 200, "morale": 20, "cinc": 0.042, "territory_count": 3},
    ],
    "USA": [
        {"year": 1939, "oil": 13400, "steel": 47900, "manpower": 334000, "food": 100, "ammunition": 60, "aircraft": 2500, "naval_tonnage": 1250, "rubber": 600, "gdp": 870, "morale": 55, "cinc": 0.158, "territory_count": 4},
        {"year": 1940, "oil": 14200, "steel": 60800, "manpower": 458000, "food": 100, "ammunition": 65, "aircraft": 3600, "naval_tonnage": 1350, "rubber": 580, "gdp": 930, "morale": 58, "cinc": 0.165, "territory_count": 4},
        {"year": 1941, "oil": 15100, "steel": 75000, "manpower": 1801000, "food": 100, "ammunition": 70, "aircraft": 12000, "naval_tonnage": 1500, "rubber": 540, "gdp": 1070, "morale": 75, "cinc": 0.182, "territory_count": 4},
        {"year": 1942, "oil": 16200, "steel": 78000, "manpower": 3900000, "food": 100, "ammunition": 82, "aircraft": 26000, "naval_tonnage": 2100, "rubber": 300, "gdp": 1240, "morale": 80, "cinc": 0.225, "territory_count": 5},
        {"year": 1943, "oil": 17800, "steel": 80600, "manpower": 9200000, "food": 100, "ammunition": 95, "aircraft": 65000, "naval_tonnage": 3200, "rubber": 450, "gdp": 1430, "morale": 85, "cinc": 0.282, "territory_count": 7},
        {"year": 1944, "oil": 19800, "steel": 81300, "manpower": 11400000, "food": 100, "ammunition": 100, "aircraft": 96000, "naval_tonnage": 4100, "rubber": 500, "gdp": 1530, "morale": 88, "cinc": 0.315, "territory_count": 10},
        {"year": 1945, "oil": 20500, "steel": 72000, "manpower": 12100000, "food": 100, "ammunition": 100, "aircraft": 80000, "naval_tonnage": 4500, "rubber": 520, "gdp": 1550, "morale": 92, "cinc": 0.318, "territory_count": 12},
    ],
    "USSR": [
        {"year": 1939, "oil": 6200, "steel": 17600, "manpower": 1800000, "food": 82, "ammunition": 75, "aircraft": 7500, "naval_tonnage": 500, "rubber": 60, "gdp": 420, "morale": 65, "cinc": 0.138, "territory_count": 6},
        {"year": 1940, "oil": 6400, "steel": 18300, "manpower": 4200000, "food": 80, "ammunition": 72, "aircraft": 8000, "naval_tonnage": 520, "rubber": 55, "gdp": 438, "morale": 62, "cinc": 0.142, "territory_count": 7},
        {"year": 1941, "oil": 5800, "steel": 13000, "manpower": 5300000, "food": 65, "ammunition": 55, "aircraft": 4000, "naval_tonnage": 480, "rubber": 40, "gdp": 360, "morale": 60, "cinc": 0.110, "territory_count": 5},
        {"year": 1942, "oil": 7200, "steel": 8100, "manpower": 9500000, "food": 58, "ammunition": 60, "aircraft": 9800, "naval_tonnage": 460, "rubber": 35, "gdp": 325, "morale": 68, "cinc": 0.125, "territory_count": 4},
        {"year": 1943, "oil": 8800, "steel": 12400, "manpower": 11000000, "food": 62, "ammunition": 78, "aircraft": 22000, "naval_tonnage": 470, "rubber": 45, "gdp": 380, "morale": 75, "cinc": 0.158, "territory_count": 6},
        {"year": 1944, "oil": 11000, "steel": 14600, "manpower": 12200000, "food": 65, "ammunition": 88, "aircraft": 33000, "naval_tonnage": 490, "rubber": 50, "gdp": 420, "morale": 82, "cinc": 0.195, "territory_count": 9},
        {"year": 1945, "oil": 12500, "steel": 15000, "manpower": 11300000, "food": 60, "ammunition": 92, "aircraft": 35000, "naval_tonnage": 500, "rubber": 55, "gdp": 430, "morale": 88, "cinc": 0.205, "territory_count": 12},
    ],
    "United Kingdom": [
        {"year": 1939, "oil": 2200, "steel": 13400, "manpower": 897000, "food": 90, "ammunition": 70, "aircraft": 2900, "naval_tonnage": 2100, "rubber": 120, "gdp": 280, "morale": 72, "cinc": 0.082, "territory_count": 8},
        {"year": 1940, "oil": 2500, "steel": 13000, "manpower": 2270000, "food": 78, "ammunition": 65, "aircraft": 4200, "naval_tonnage": 2050, "rubber": 110, "gdp": 290, "morale": 85, "cinc": 0.088, "territory_count": 7},
        {"year": 1941, "oil": 2800, "steel": 12800, "manpower": 3400000, "food": 72, "ammunition": 68, "aircraft": 6400, "naval_tonnage": 1950, "rubber": 95, "gdp": 305, "morale": 82, "cinc": 0.092, "territory_count": 7},
        {"year": 1942, "oil": 3200, "steel": 13200, "manpower": 4100000, "food": 70, "ammunition": 75, "aircraft": 8800, "naval_tonnage": 1850, "rubber": 80, "gdp": 315, "morale": 78, "cinc": 0.098, "territory_count": 6},
        {"year": 1943, "oil": 3800, "steel": 13100, "manpower": 4600000, "food": 72, "ammunition": 82, "aircraft": 12000, "naval_tonnage": 1900, "rubber": 90, "gdp": 325, "morale": 80, "cinc": 0.102, "territory_count": 7},
        {"year": 1944, "oil": 4500, "steel": 12600, "manpower": 4900000, "food": 75, "ammunition": 90, "aircraft": 14000, "naval_tonnage": 2000, "rubber": 100, "gdp": 330, "morale": 85, "cinc": 0.108, "territory_count": 8},
        {"year": 1945, "oil": 4800, "steel": 12000, "manpower": 4700000, "food": 78, "ammunition": 92, "aircraft": 12000, "naval_tonnage": 2050, "rubber": 105, "gdp": 320, "morale": 90, "cinc": 0.105, "territory_count": 9},
    ],
    "Japan": [
        {"year": 1939, "oil": 2500, "steel": 6700, "manpower": 1700000, "food": 88, "ammunition": 78, "aircraft": 3200, "naval_tonnage": 1150, "rubber": 40, "gdp": 170, "morale": 82, "cinc": 0.072, "territory_count": 8},
        {"year": 1940, "oil": 2800, "steel": 6900, "manpower": 2000000, "food": 85, "ammunition": 80, "aircraft": 4000, "naval_tonnage": 1200, "rubber": 300, "gdp": 178, "morale": 85, "cinc": 0.078, "territory_count": 10},
        {"year": 1941, "oil": 3100, "steel": 6800, "manpower": 2400000, "food": 82, "ammunition": 82, "aircraft": 5000, "naval_tonnage": 1300, "rubber": 350, "gdp": 185, "morale": 88, "cinc": 0.082, "territory_count": 14},
        {"year": 1942, "oil": 3800, "steel": 7000, "manpower": 3800000, "food": 78, "ammunition": 75, "aircraft": 6200, "naval_tonnage": 1400, "rubber": 400, "gdp": 195, "morale": 82, "cinc": 0.088, "territory_count": 18},
        {"year": 1943, "oil": 3200, "steel": 7800, "manpower": 4500000, "food": 72, "ammunition": 70, "aircraft": 9000, "naval_tonnage": 1100, "rubber": 250, "gdp": 190, "morale": 72, "cinc": 0.078, "territory_count": 14},
        {"year": 1944, "oil": 2200, "steel": 6500, "manpower": 5400000, "food": 65, "ammunition": 55, "aircraft": 12000, "naval_tonnage": 600, "rubber": 100, "gdp": 175, "morale": 62, "cinc": 0.058, "territory_count": 10},
        {"year": 1945, "oil": 800, "steel": 3800, "manpower": 5500000, "food": 50, "ammunition": 40, "aircraft": 5000, "naval_tonnage": 200, "rubber": 30, "gdp": 120, "morale": 45, "cinc": 0.032, "territory_count": 4},
    ],
    "Italy": [
        {"year": 1939, "oil": 300, "steel": 2300, "manpower": 1600000, "food": 82, "ammunition": 55, "aircraft": 1800, "naval_tonnage": 680, "rubber": 15, "gdp": 152, "morale": 55, "cinc": 0.038, "territory_count": 5},
        {"year": 1940, "oil": 350, "steel": 2100, "manpower": 1900000, "food": 78, "ammunition": 50, "aircraft": 2400, "naval_tonnage": 670, "rubber": 12, "gdp": 148, "morale": 52, "cinc": 0.035, "territory_count": 6},
        {"year": 1941, "oil": 400, "steel": 2000, "manpower": 2500000, "food": 72, "ammunition": 45, "aircraft": 2200, "naval_tonnage": 620, "rubber": 10, "gdp": 145, "morale": 45, "cinc": 0.032, "territory_count": 7},
        {"year": 1942, "oil": 350, "steel": 1800, "manpower": 2800000, "food": 68, "ammunition": 40, "aircraft": 2000, "naval_tonnage": 540, "rubber": 8, "gdp": 140, "morale": 38, "cinc": 0.028, "territory_count": 6},
        {"year": 1943, "oil": 250, "steel": 1500, "manpower": 1800000, "food": 62, "ammunition": 35, "aircraft": 1500, "naval_tonnage": 400, "rubber": 5, "gdp": 120, "morale": 25, "cinc": 0.020, "territory_count": 3},
    ],
    "France": [
        {"year": 1939, "oil": 400, "steel": 7900, "manpower": 5000000, "food": 92, "ammunition": 72, "aircraft": 1400, "naval_tonnage": 680, "rubber": 35, "gdp": 200, "morale": 60, "cinc": 0.058, "territory_count": 6},
        {"year": 1940, "oil": 350, "steel": 4000, "manpower": 3000000, "food": 65, "ammunition": 55, "aircraft": 800, "naval_tonnage": 650, "rubber": 20, "gdp": 130, "morale": 30, "cinc": 0.032, "territory_count": 2},
        {"year": 1944, "oil": 50, "steel": 500, "manpower": 560000, "food": 55, "ammunition": 40, "aircraft": 200, "naval_tonnage": 180, "rubber": 10, "gdp": 80, "morale": 72, "cinc": 0.012, "territory_count": 2},
        {"year": 1945, "oil": 100, "steel": 1200, "manpower": 1300000, "food": 58, "ammunition": 55, "aircraft": 500, "naval_tonnage": 250, "rubber": 15, "gdp": 95, "morale": 80, "cinc": 0.018, "territory_count": 4},
    ],
    "China": [
        {"year": 1939, "oil": 100, "steel": 500, "manpower": 5000000, "food": 62, "ammunition": 30, "aircraft": 300, "naval_tonnage": 60, "rubber": 10, "gdp": 72, "morale": 55, "cinc": 0.082, "territory_count": 5},
        {"year": 1942, "oil": 80, "steel": 400, "manpower": 5600000, "food": 55, "ammunition": 25, "aircraft": 200, "naval_tonnage": 40, "rubber": 8, "gdp": 65, "morale": 50, "cinc": 0.078, "territory_count": 4},
        {"year": 1944, "oil": 90, "steel": 450, "manpower": 5900000, "food": 50, "ammunition": 28, "aircraft": 350, "naval_tonnage": 50, "rubber": 12, "gdp": 60, "morale": 52, "cinc": 0.075, "territory_count": 4},
        {"year": 1945, "oil": 100, "steel": 500, "manpower": 5700000, "food": 48, "ammunition": 30, "aircraft": 400, "naval_tonnage": 55, "rubber": 15, "gdp": 58, "morale": 55, "cinc": 0.072, "territory_count": 5},
    ],
}
# fmt: on

NATIONS = [
    {"name": "Germany", "code": "DE", "side": "axis", "alliance": "AXIS", "capital": "Berlin", "ideology": "National Socialism", "description": "Nazi Germany under Adolf Hitler, the primary Axis power in Europe."},
    {"name": "Japan", "code": "JP", "side": "axis", "alliance": "AXIS", "capital": "Tokyo", "ideology": "Military Imperialism", "description": "The Empire of Japan, the primary Axis power in the Pacific."},
    {"name": "Italy", "code": "IT", "side": "axis", "alliance": "AXIS", "capital": "Rome", "ideology": "Fascism", "description": "Fascist Italy under Mussolini, allied with Germany until the 1943 armistice."},
    {"name": "Hungary", "code": "HU", "side": "axis", "alliance": "AXIS", "capital": "Budapest", "ideology": "Authoritarian Conservatism", "description": "Kingdom of Hungary, Axis co-belligerent."},
    {"name": "Romania", "code": "RO", "side": "axis", "alliance": "AXIS", "capital": "Bucharest", "ideology": "Authoritarian Monarchy", "description": "Kingdom of Romania, initially Axis then switched to Allies in 1944."},
    {"name": "Bulgaria", "code": "BG", "side": "axis", "alliance": "AXIS", "capital": "Sofia", "ideology": "Authoritarian Monarchy", "description": "Kingdom of Bulgaria, Axis member."},
    {"name": "Finland", "code": "FI", "side": "axis", "alliance": "AXIS", "capital": "Helsinki", "ideology": "Democratic Co-belligerent", "description": "Finland fought alongside Germany against the USSR (Continuation War) but maintained democratic governance."},
    {"name": "USA", "code": "US", "side": "allies", "alliance": "ALLIES", "capital": "Washington", "ideology": "Liberal Democracy", "description": "The United States of America, the 'arsenal of democracy' and dominant Allied industrial power."},
    {"name": "USSR", "code": "SU", "side": "allies", "alliance": "ALLIES", "capital": "Moscow", "ideology": "Soviet Communism", "description": "The Soviet Union, which bore the heaviest casualties and fought the largest land campaigns of the war."},
    {"name": "United Kingdom", "code": "GB", "side": "allies", "alliance": "ALLIES", "capital": "London", "ideology": "Parliamentary Democracy", "description": "The United Kingdom stood alone against Nazi Germany from June 1940 to June 1941. The British Empire mobilised vast resources from across its territories."},
    {"name": "France", "code": "FR", "side": "allies", "alliance": "ALLIES", "capital": "Paris", "ideology": "Republic / Free France", "description": "Metropolitan France fell in 1940, but Free French forces under de Gaulle continued fighting alongside the Allies."},
    {"name": "China", "code": "CN", "side": "allies", "alliance": "ALLIES", "capital": "Chongqing", "ideology": "Nationalist (Kuomintang)", "description": "The Republic of China fought Japan from 1937, tying down over a million Japanese troops."},
    {"name": "Poland", "code": "PL", "side": "allies", "alliance": "ALLIES", "capital": "Warsaw (Government-in-exile: London)", "ideology": "Republic in Exile", "description": "Poland was the first victim of German aggression. Polish forces fought on all Allied fronts and contributed vital intelligence (Enigma codebreaking)."},
    {"name": "Canada", "code": "CA", "side": "allies", "alliance": "ALLIES", "capital": "Ottawa", "ideology": "Parliamentary Democracy", "description": "Canada made significant contributions across all theaters, including Juno Beach on D-Day and the Italian Campaign."},
    {"name": "Australia", "code": "AU", "side": "allies", "alliance": "ALLIES", "capital": "Canberra", "ideology": "Parliamentary Democracy", "description": "Australia fought in North Africa, the Pacific, and Southeast Asia, including the Kokoda Track campaign."},
    {"name": "New Zealand", "code": "NZ", "side": "allies", "alliance": "ALLIES", "capital": "Wellington", "ideology": "Parliamentary Democracy", "description": "New Zealand contributed forces to North Africa, Italy, and the Pacific relative to its small population."},
    {"name": "India", "code": "IN", "side": "allies", "alliance": "ALLIES", "capital": "New Delhi", "ideology": "British Crown Colony", "description": "British India fielded the largest volunteer army in history — 2.5 million personnel serving across multiple theaters."},
    {"name": "South Africa", "code": "ZA", "side": "allies", "alliance": "ALLIES", "capital": "Pretoria", "ideology": "Parliamentary Democracy", "description": "South Africa contributed forces to the North African and Italian campaigns."},
    {"name": "Belgium", "code": "BE", "side": "allies", "alliance": "ALLIES", "capital": "Brussels", "ideology": "Constitutional Monarchy", "description": "Belgium was occupied in 1940 but contributed resistance fighters and colonial forces from the Belgian Congo."},
    {"name": "Netherlands", "code": "NL", "side": "allies", "alliance": "ALLIES", "capital": "Amsterdam", "ideology": "Constitutional Monarchy", "description": "The Netherlands was occupied in 1940. Dutch forces continued fighting in the East Indies and resistance movements operated at home."},
    {"name": "Greece", "code": "GR", "side": "allies", "alliance": "ALLIES", "capital": "Athens", "ideology": "Monarchy", "description": "Greece successfully repelled the Italian invasion in 1940 before falling to a combined German-Italian assault in 1941."},
    {"name": "Yugoslavia", "code": "YU", "side": "allies", "alliance": "ALLIES", "capital": "Belgrade", "ideology": "Monarchy", "description": "Yugoslavia was conquered in 1941 but sustained a massive partisan resistance movement under Tito."},
    {"name": "Norway", "code": "NO", "side": "allies", "alliance": "ALLIES", "capital": "Oslo", "ideology": "Constitutional Monarchy", "description": "Norway was occupied in 1940. Norwegian forces and resistance fighters continued the struggle throughout the war."},
    {"name": "Czechoslovakia", "code": "CS", "side": "allies", "alliance": "ALLIES", "capital": "Prague", "ideology": "Republic in Exile", "description": "Czechoslovakia was dismembered in 1938-39. Czech and Slovak forces served with Allied armies throughout the war."},
]

GEOGRAPHIC_REGIONS = [
    {"name": "Europe", "theater": "Europe", "latitude": 50.0, "longitude": 15.0, "strategic_rating": 10},
    {"name": "Eastern Front", "theater": "Europe", "parent": "Europe", "latitude": 52.0, "longitude": 35.0, "strategic_rating": 10},
    {"name": "Normandy", "theater": "Europe", "parent": "Europe", "latitude": 49.18, "longitude": -0.37, "strategic_rating": 9},
    {"name": "Western Europe", "theater": "Europe", "parent": "Europe", "latitude": 48.86, "longitude": 2.35, "strategic_rating": 9},
    {"name": "Ardennes", "theater": "Europe", "parent": "Europe", "latitude": 50.05, "longitude": 5.72, "strategic_rating": 7},
    {"name": "Berlin", "theater": "Europe", "parent": "Europe", "latitude": 52.52, "longitude": 13.405, "strategic_rating": 10},
    {"name": "Italy", "theater": "Europe", "parent": "Europe", "latitude": 41.9, "longitude": 12.5, "strategic_rating": 7},
    {"name": "Netherlands", "theater": "Europe", "parent": "Europe", "latitude": 52.37, "longitude": 4.9, "strategic_rating": 6},
    {"name": "United Kingdom", "theater": "Europe", "latitude": 51.5, "longitude": -0.12, "strategic_rating": 10},
    {"name": "Pacific", "theater": "Pacific", "latitude": 15.0, "longitude": 160.0, "strategic_rating": 9},
    {"name": "Midway Atoll", "theater": "Pacific", "parent": "Pacific", "latitude": 28.21, "longitude": -177.37, "strategic_rating": 8},
    {"name": "North Africa", "theater": "Africa", "latitude": 30.0, "longitude": 20.0, "strategic_rating": 8},
    {"name": "Southeast Asia", "theater": "Asia", "latitude": 10.0, "longitude": 105.0, "strategic_rating": 7},
    {"name": "Atlantic Ocean", "theater": "Europe", "latitude": 50.0, "longitude": -30.0, "strategic_rating": 9},
]
