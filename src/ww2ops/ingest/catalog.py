from __future__ import annotations

PRIMARY_SIDES = {
    "Germany": "axis",
    "Japan": "axis",
    "Italy": "axis",
    "Hungary": "axis",
    "Romania": "axis",
    "Bulgaria": "axis",
    "Finland": "axis",
    "Slovakia": "axis",
    "United Kingdom": "allies",
    "USA": "allies",
    "USSR": "allies",
    "France": "allies",
    "Poland": "allies",
    "Canada": "allies",
    "Australia": "allies",
    "China": "allies",
    "New Zealand": "allies",
    "Belgium": "allies",
    "Netherlands": "allies",
    "Greece": "allies",
    "Yugoslavia": "allies",
    "Norway": "allies",
    "Czechoslovakia": "allies",
    "South Africa": "allies",
    "India": "allies",
}

COUNTRY_ALIASES = {
    "United States": "USA",
    "United States of America": "USA",
    "U.S.A.": "USA",
    "Soviet Union": "USSR",
    "Union of Soviet Socialist Republics": "USSR",
    "Russia": "USSR",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Great Britain": "United Kingdom",
    "UK": "United Kingdom",
    "Nazi Germany": "Germany",
    "Empire of Japan": "Japan",
    "Kingdom of Italy": "Italy",
    "Free France": "France",
    "Republic of China": "China",
}

REGION_ALIASES = {
    "Volgograd": "Eastern Front",
    "Stalingrad": "Eastern Front",
    "Normandy": "Normandy",
    "Midway Atoll": "Midway Atoll",
    "Kursk": "Eastern Front",
    "Berlin": "Europe",
    "North Africa": "North Africa",
    "Pacific Ocean": "Pacific",
    "Pacific Theater": "Pacific",
    "Ardennes": "Europe",
    "El Alamein": "North Africa",
    "Monte Cassino": "Europe",
    "Leningrad": "Eastern Front",
}

NATION_LABELS = {
    "Germany": "Germany",
    "United Kingdom": "United Kingdom",
    "USA": "United States",
    "USSR": "Soviet Union",
    "Japan": "Japan",
    "Italy": "Italy",
    "France": "France",
    "Poland": "Poland",
    "China": "China",
    "Canada": "Canada",
    "Australia": "Australia",
    "New Zealand": "New Zealand",
    "Belgium": "Belgium",
    "Netherlands": "Netherlands",
    "Greece": "Greece",
    "Yugoslavia": "Yugoslavia",
    "Norway": "Norway",
    "Czechoslovakia": "Czechoslovakia",
    "Romania": "Romania",
    "Hungary": "Hungary",
    "Bulgaria": "Bulgaria",
    "Finland": "Finland",
    "India": "India",
    "South Africa": "South Africa",
}

LEADERS = {
    "Adolf Hitler": {"country": "Germany", "role_type": "political", "dbpedia": "Adolf_Hitler"},
    "Winston Churchill": {"country": "United Kingdom", "role_type": "political", "dbpedia": "Winston_Churchill"},
    "Franklin D. Roosevelt": {"country": "USA", "role_type": "political", "dbpedia": "Franklin_D._Roosevelt"},
    "Joseph Stalin": {"country": "USSR", "role_type": "political", "dbpedia": "Joseph_Stalin"},
    "Charles de Gaulle": {"country": "France", "role_type": "political", "dbpedia": "Charles_de_Gaulle"},
    "Dwight D. Eisenhower": {"country": "USA", "role_type": "military", "dbpedia": "Dwight_D._Eisenhower"},
    "Erwin Rommel": {"country": "Germany", "role_type": "military", "dbpedia": "Erwin_Rommel"},
    "Georgy Zhukov": {"country": "USSR", "role_type": "military", "dbpedia": "Georgy_Zhukov"},
    "Bernard Montgomery": {"country": "United Kingdom", "role_type": "military", "dbpedia": "Bernard_Montgomery"},
    "Isoroku Yamamoto": {"country": "Japan", "role_type": "military", "dbpedia": "Isoroku_Yamamoto"},
    "Chester W. Nimitz": {"country": "USA", "role_type": "military", "dbpedia": "Chester_W._Nimitz"},
    "Douglas MacArthur": {"country": "USA", "role_type": "military", "dbpedia": "Douglas_MacArthur"},
}

BATTLES = {
    "Battle of Stalingrad": {"region": "Eastern Front", "victor_side": "allies", "dbpedia": "Battle_of_Stalingrad", "axis_casualties": 850000, "allied_casualties": 1100000},
    "Battle of Normandy": {"region": "Normandy", "victor_side": "allies", "dbpedia": "Battle_of_Normandy", "axis_casualties": 200000, "allied_casualties": 226000},
    "Battle of Midway": {"region": "Midway Atoll", "victor_side": "allies", "dbpedia": "Battle_of_Midway", "axis_casualties": 3057, "allied_casualties": 307},
    "Battle of Britain": {"region": "Europe", "victor_side": "allies", "dbpedia": "Battle_of_Britain", "axis_casualties": 2500, "allied_casualties": 1544},
    "Battle of Kursk": {"region": "Eastern Front", "victor_side": "allies", "dbpedia": "Battle_of_Kursk", "axis_casualties": 200000, "allied_casualties": 254000},
    "Battle of Berlin": {"region": "Europe", "victor_side": "allies", "dbpedia": "Battle_of_Berlin", "axis_casualties": 92000, "allied_casualties": 352000},
    "Battle of the Bulge": {"region": "Europe", "victor_side": "allies", "dbpedia": "Battle_of_the_Bulge", "axis_casualties": 100000, "allied_casualties": 89000},
    "Second Battle of El Alamein": {"region": "North Africa", "victor_side": "allies", "dbpedia": "Second_Battle_of_El_Alamein", "axis_casualties": 30000, "allied_casualties": 13500},
    "Siege of Leningrad": {"region": "Eastern Front", "victor_side": "allies", "dbpedia": "Siege_of_Leningrad", "axis_casualties": 580000, "allied_casualties": 1100000},
    "Battle of Monte Cassino": {"region": "Europe", "victor_side": "allies", "dbpedia": "Battle_of_Monte_Cassino", "axis_casualties": 20000, "allied_casualties": 55000},
}

OPERATIONS = {
    "Operation Overlord": {"region": "Normandy", "side": "allies", "outcome": "success", "code_name": "OVERLORD", "campaign": "Western Front Liberation", "dbpedia": "Operation_Overlord"},
    "Operation Barbarossa": {"region": "Eastern Front", "side": "axis", "outcome": "failure", "code_name": "BARBAROSSA", "campaign": "Eastern Front Offensive", "dbpedia": "Operation_Barbarossa"},
    "Operation Torch": {"region": "North Africa", "side": "allies", "outcome": "success", "code_name": "TORCH", "campaign": "North African Theater", "dbpedia": "Operation_Torch_(World_War_II)"},
    "Operation Husky": {"region": "Europe", "side": "allies", "outcome": "success", "code_name": "HUSKY", "campaign": "Mediterranean Offensive", "dbpedia": "Allied_invasion_of_Sicily"},
    "Operation Market Garden": {"region": "Europe", "side": "allies", "outcome": "failure", "code_name": "MARKET GARDEN", "campaign": "Western Front Liberation", "dbpedia": "Operation_Market_Garden"},
    "Operation Bagration": {"region": "Eastern Front", "side": "allies", "outcome": "success", "code_name": "BAGRATION", "campaign": "Eastern Front Offensive", "dbpedia": "Operation_Bagration"},
    "Operation Fortitude": {"region": "Europe", "side": "allies", "outcome": "success", "code_name": "FORTITUDE", "campaign": "Deception Operations", "dbpedia": "Operation_Fortitude"},
    "Operation Neptune": {"region": "Normandy", "side": "allies", "outcome": "success", "code_name": "NEPTUNE", "campaign": "Western Front Liberation", "dbpedia": "Operation_Neptune"},
}

INTELLIGENCE_TOPICS = {
    "Ultra": {"nation": "United Kingdom", "region": "Europe", "classification": "top_secret", "report_type": "signals_intelligence", "dbpedia": "Ultra"},
    "Double-Cross System": {"nation": "United Kingdom", "region": "Europe", "classification": "secret", "report_type": "counterintelligence", "dbpedia": "Double-Cross_System"},
    "Operation Fortitude": {"nation": "United Kingdom", "region": "Europe", "classification": "secret", "report_type": "deception", "dbpedia": "Operation_Fortitude"},
    "Magic (cryptography)": {"nation": "USA", "region": "Pacific", "classification": "top_secret", "report_type": "signals_intelligence", "dbpedia": "Magic_(cryptography)"},
    "Enigma machine": {"nation": "Germany", "region": "Europe", "classification": "secret", "report_type": "signals_security", "dbpedia": "Enigma_machine"},
    "Bletchley Park": {"nation": "United Kingdom", "region": "Europe", "classification": "confidential", "report_type": "analysis", "dbpedia": "Bletchley_Park"},
}

LEADER_ASSIGNMENTS = {
    "Dwight D. Eisenhower": ["Operation Overlord", "Operation Torch", "Operation Neptune"],
    "Erwin Rommel": ["Operation Fortitude"],
    "Georgy Zhukov": ["Operation Bagration", "Operation Barbarossa"],
    "Bernard Montgomery": ["Operation Overlord", "Operation Market Garden", "Second Battle of El Alamein"],
    "Isoroku Yamamoto": ["Battle of Midway"],
    "Chester W. Nimitz": ["Battle of Midway"],
}

KAGGLE_RESOURCE_COLUMN_ALIASES = {
    "nation": ["nation", "country", "state", "nation_name"],
    "year": ["year", "snapshot_year", "date_year"],
    "oil": ["oil", "fuel", "oil_production", "petroleum"],
    "steel": ["steel", "steel_production", "iron_and_steel"],
    "manpower": ["manpower", "military_personnel", "personnel", "troops"],
    "gdp": ["gdp", "gross_domestic_product", "economy"],
    "morale": ["morale", "national_morale"],
    "source": ["source", "dataset_source", "citation"],
    "confidence": ["confidence", "confidence_level", "quality_score"],
}

COW_URLS = {
    "states": "https://correlatesofwar.org/wp-content/uploads/States2024.zip",
    "nmc": "https://correlatesofwar.org/wp-content/uploads/NMC_5_0.zip",
    "alliances": "https://correlatesofwar.org/wp-content/uploads/version4.1_csv.zip",
    "wars": "https://correlatesofwar.org/wp-content/uploads/Inter-StateWarData_v4.0.csv",
}

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

SOURCE_METADATA = {
    "wikidata": {"source": "Wikidata Query Service", "confidence": 0.84},
    "dbpedia": {"source": "DBpedia SPARQL", "confidence": 0.76},
    "cow_states": {"source": "Correlates of War State System Membership v2024", "confidence": 0.93},
    "cow_nmc": {"source": "Correlates of War National Material Capabilities v5.0", "confidence": 0.9},
    "cow_alliances": {"source": "Correlates of War Formal Alliances v4.1", "confidence": 0.88},
    "cow_wars": {"source": "Correlates of War Inter-State War Data v4.0", "confidence": 0.87},
    "kaggle": {"source": "Kaggle dataset import", "confidence": 0.72},
}
