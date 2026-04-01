"""
Seed database with initial WW2 historical data
"""

from datetime import datetime
from database import db


def seed_database():
    """Populate database with sample WW2 data"""
    from models import (
        Battle,
        Operation,
        Resource,
        Territory,
        IntelligenceReport,
        Leader,
        CommandAssignment,
        Campaign,
        WarCrime,
        EconomicStat,
        Tactic,
        MilitaryInnovation,
    )
    
    # Sample Battles
    battles = [
        Battle(
            name='Battle of Stalingrad',
            start_date=datetime(1942, 8, 23),
            end_date=datetime(1943, 2, 2),
            location='Stalingrad, USSR',
            axis_forces=1000000,
            allied_forces=1100000,
            axis_casualties=850000,
            allied_casualties=1100000,
            victor='allies',
            description='One of the deadliest battles in history, turning point on Eastern Front',
            latitude=48.7080,
            longitude=44.5133
        ),
        Battle(
            name='Battle of Normandy',
            start_date=datetime(1944, 6, 6),
            end_date=datetime(1944, 8, 30),
            location='Normandy, France',
            axis_forces=380000,
            allied_forces=1560000,
            axis_casualties=200000,
            allied_casualties=226000,
            victor='allies',
            description='D-Day landings and subsequent liberation of France',
            latitude=49.1829,
            longitude=-0.3707
        ),
        Battle(
            name='Battle of Midway',
            start_date=datetime(1942, 6, 4),
            end_date=datetime(1942, 6, 7),
            location='Midway Atoll, Pacific',
            axis_forces=4,
            allied_forces=3,
            axis_casualties=3057,
            allied_casualties=307,
            victor='allies',
            description='Decisive naval battle in the Pacific Theater',
            latitude=28.2072,
            longitude=-177.3733
        ),
        Battle(
            name='Battle of Britain',
            start_date=datetime(1940, 7, 10),
            end_date=datetime(1940, 10, 31),
            location='United Kingdom',
            axis_forces=2600,
            allied_forces=1963,
            axis_casualties=2500,
            allied_casualties=1544,
            victor='allies',
            description='Aerial battle preventing German invasion of Britain',
            latitude=51.5074,
            longitude=-0.1278
        ),
        Battle(
            name='Operation Barbarossa',
            start_date=datetime(1941, 6, 22),
            end_date=datetime(1941, 12, 5),
            location='Eastern Front',
            axis_forces=4000000,
            allied_forces=2900000,
            axis_casualties=830000,
            allied_casualties=2500000,
            victor='axis',
            description='German invasion of the Soviet Union',
            latitude=55.7558,
            longitude=37.6173
        )
    ]
    
    for battle in battles:
        db.session.add(battle)

    db.session.flush()

    # Sample Campaigns
    campaigns = [
        Campaign(
            name='Western Front Liberation',
            theater='Europe',
            region='Western Europe',
            start_date=datetime(1944, 6, 6),
            end_date=datetime(1945, 5, 8),
            description='Allied operations to liberate Western Europe culminating in the defeat of Nazi Germany.',
            outcome='success',
            strategic_value=10
        ),
        Campaign(
            name='Eastern Front Offensive',
            theater='Europe',
            region='Eastern Front',
            start_date=datetime(1941, 6, 22),
            end_date=datetime(1945, 5, 9),
            description='Axis invasion of the Soviet Union followed by massive Soviet counteroffensives.',
            outcome='allied',
            strategic_value=10
        ),
        Campaign(
            name='Pacific Island Hopping',
            theater='Pacific',
            region='Pacific Ocean',
            start_date=datetime(1942, 6, 4),
            end_date=datetime(1945, 9, 2),
            description='Allied offensive strategy capturing key islands to approach the Japanese mainland.',
            outcome='success',
            strategic_value=9
        ),
        Campaign(
            name='North African Theater',
            theater='Africa',
            region='North Africa',
            start_date=datetime(1940, 6, 10),
            end_date=datetime(1943, 5, 13),
            description='Axis and Allied struggle for control of North Africa and the Mediterranean.',
            outcome='allied',
            strategic_value=7
        )
    ]

    for campaign in campaigns:
        db.session.add(campaign)

    db.session.flush()
    
    # Sample Tactics
    tactics = [
        Tactic(
            name='Blitzkrieg',
            domain='land',
            description='Rapid combined-arms assaults to penetrate enemy lines and encircle forces.',
            period_start=1939,
            period_end=1943,
            doctrine_notes='Relies on coordination between armor, infantry, and air support.',
            visualization_svg='svg/tactics/blitzkrieg.svg',
            innovation_highlights='["Panzer divisions", "Close air support"]'
        ),
        Tactic(
            name='Island Hopping',
            domain='naval',
            description='Selective capture of strategic islands to advance toward Japan.',
            period_start=1942,
            period_end=1945,
            doctrine_notes='Bypass heavily fortified islands to isolate and neutralize them.',
            visualization_svg='svg/tactics/island_hopping.svg',
            innovation_highlights='["Amphibious warfare", "Carrier strike groups"]'
        ),
        Tactic(
            name='Scorched Earth',
            domain='land',
            description='Deliberate destruction of resources to deny enemy use.',
            period_start=1812,
            period_end=1945,
            doctrine_notes='Used by retreating Soviet forces to slow German advances.',
            visualization_svg='svg/tactics/scorched_earth.svg',
            innovation_highlights='[]'
        ),
        Tactic(
            name='Strategic Bombing',
            domain='air',
            description='Air campaigns targeting industrial capacity and civilian morale.',
            period_start=1940,
            period_end=1945,
            doctrine_notes='Used extensively by Allied air forces against Axis cities.',
            visualization_svg='svg/tactics/strategic_bombing.svg',
            innovation_highlights='["Long-range bombers", "Radar navigation"]'
        )
    ]

    for tactic in tactics:
        db.session.add(tactic)

    db.session.flush()

    # Sample Operations with extended data
    operations = [
        Operation(
            name='Operation Overlord',
            code_name='OVERLORD',
            start_date=datetime(1944, 6, 6),
            end_date=datetime(1944, 8, 30),
            side='allies',
            objective='Liberate Western Europe from Nazi occupation',
            outcome='success',
            description='The Allied invasion of Normandy.',
            region='Europe',
            campaign=campaigns[0],
            objectives_detail='["Secure Normandy beaches", "Establish western front", "Liberate Paris"]',
            participating_nations='["USA", "United Kingdom", "Canada", "France"]',
            casualties_axis=200000,
            casualties_allies=226000,
            resources_fuel=250000.0,
            resources_aircraft=11000,
            resources_naval=500,
            analysis='Amphibious landings reinforced by airborne drops broke German defenses and opened Western Front.',
            tactics_summary='Combined amphibious assault and airborne operations with overwhelming logistics.',
            map_overlay='maps/operation_overlord.geojson',
            intelligence_notes='ULTRA decrypts revealed German defensive dispositions.',
            battle=battles[1]
        ),
        Operation(
            name='Operation Barbarossa',
            code_name='BARBAROSSA',
            start_date=datetime(1941, 6, 22),
            end_date=datetime(1941, 12, 5),
            side='axis',
            objective='Invade and conquer the Soviet Union',
            outcome='partial',
            description='Largest military operation in history targeting the Soviet Union.',
            region='Europe',
            campaign=campaigns[1],
            objectives_detail='["Capture Moscow", "Destroy Red Army", "Secure oil fields"]',
            participating_nations='["Germany", "Romania", "Finland", "Italy"]',
            casualties_axis=830000,
            casualties_allies=2500000,
            resources_fuel=600000.0,
            resources_aircraft=2700,
            resources_naval=0,
            analysis='Initial success stalled by logistics, Soviet resistance, and harsh winter.',
            tactics_summary='Rapid mechanized thrusts overextended supply lines.',
            map_overlay='maps/operation_barbarossa.geojson',
            intelligence_notes='Soviet intelligence had warnings but leadership dismissed many reports.',
            battle=battles[4]
        ),
        Operation(
            name='Operation Market Garden',
            code_name='MARKET GARDEN',
            start_date=datetime(1944, 9, 17),
            end_date=datetime(1944, 9, 25),
            side='allies',
            objective='Capture bridges across the Rhine and outflank German defenses',
            outcome='failure',
            description='Ambitious airborne operation in the Netherlands.',
            region='Europe',
            campaign=campaigns[0],
            objectives_detail='["Secure Eindhoven", "Capture Nijmegen bridge", "Hold Arnhem"]',
            participating_nations='["United Kingdom", "USA", "Poland", "Canada"]',
            casualties_axis=13000,
            casualties_allies=17000,
            resources_fuel=95000.0,
            resources_aircraft=1700,
            resources_naval=20,
            analysis='Insufficient intelligence on German armor and overstretched airborne supply lines.',
            tactics_summary='Large-scale airborne drop with ground armored thrust along single road.',
            map_overlay='maps/operation_market_garden.geojson',
            intelligence_notes='Ultra decrypts suggested armored units nearby but warnings not fully heeded.'
        ),
        Operation(
            name='Operation Torch',
            code_name='TORCH',
            start_date=datetime(1942, 11, 8),
            end_date=datetime(1942, 11, 16),
            side='allies',
            objective='Invade North Africa and open a new front',
            outcome='success',
            description='Allied invasion of French North Africa.',
            region='Africa',
            campaign=campaigns[3],
            objectives_detail='["Secure Casablanca", "Capture Oran", "Take Algiers"]',
            participating_nations='["USA", "United Kingdom", "Free French"]',
            casualties_axis=3000,
            casualties_allies=2500,
            resources_fuel=180000.0,
            resources_aircraft=600,
            resources_naval=350,
            analysis='Coordinated landings weakened Vichy French resistance and paved way for Tunisian campaign.',
            tactics_summary='Multiple amphibious landings supported by naval bombardment and airborne drops.',
            map_overlay='maps/operation_torch.geojson',
            intelligence_notes='Negotiations with Vichy elements reduced resistance.'
        ),
        Operation(
            name='Operation Bagration',
            code_name='BAGRATION',
            start_date=datetime(1944, 6, 22),
            end_date=datetime(1944, 8, 19),
            side='allies',
            objective='Destroy German Army Group Centre',
            outcome='success',
            description='Massive Soviet offensive liberating Belarus.',
            region='Europe',
            campaign=campaigns[1],
            objectives_detail='["Break through at Vitebsk", "Encircle Minsk", "Reach the Vistula"]',
            participating_nations='["USSR"]',
            casualties_axis=450000,
            casualties_allies=765000,
            resources_fuel=400000.0,
            resources_aircraft=2500,
            resources_naval=0,
            analysis='Deception tactics and artillery concentrations shattered German defenses.',
            tactics_summary='Maskirovka deception, overwhelming artillery barrages, deep battle doctrine.',
            map_overlay='maps/operation_bagration.geojson',
            intelligence_notes='Soviet partisans disrupted German logistics before the offensive.'
        ),
        Operation(
            name='Operation Uranus',
            code_name='URANUS',
            start_date=datetime(1942, 11, 19),
            end_date=datetime(1942, 11, 23),
            side='allies',
            objective='Encircle Axis forces at Stalingrad',
            outcome='success',
            description='Soviet counteroffensive encircling the German 6th Army.',
            region='Europe',
            campaign=campaigns[1],
            objectives_detail='["Break Romanian lines", "Link pincers at Kalach", "Cut supply routes"]',
            participating_nations='["USSR"]',
            casualties_axis=150000,
            casualties_allies=48500,
            resources_fuel=220000.0,
            resources_aircraft=1400,
            resources_naval=0,
            analysis='Coordinated pincer movements exploited weaker Axis allied forces guarding flanks.',
            tactics_summary='Deep encirclement using armor and cavalry-mechanized groups.',
            map_overlay='maps/operation_uranus.geojson',
            intelligence_notes='Soviet maskirovka concealed force build-up on flanks.'
        )
    ]

    for op in operations:
        db.session.add(op)

    db.session.flush()

    # Associate tactics with operations
    blitzkrieg = tactics[0]
    island_hopping = tactics[1]
    scorched_earth = tactics[2]
    strategic_bombing = tactics[3]

    operations[0].tactics.extend([strategic_bombing])
    operations[1].tactics.extend([blitzkrieg, scorched_earth])
    operations[2].tactics.extend([strategic_bombing])
    operations[3].tactics.extend([strategic_bombing, island_hopping])
    operations[4].tactics.extend([scorched_earth])
    operations[5].tactics.extend([scorched_earth])

    db.session.flush()

    # Sample Leaders
    leaders = [
        Leader(
            name='Winston Churchill',
            country='United Kingdom',
            title='Prime Minister',
            role_type='political',
            biography='British Prime Minister who led the United Kingdom through World War II.',
            ideology='Conservative, staunch anti-Nazi coalition builder.',
            portrait_url='img/leaders/churchill.jpg',
            notable_quotes='["We shall fight on the beaches."]',
            key_operations='["Operation Overlord", "Battle of Britain"]',
            influence_score=92.0
        ),
        Leader(
            name='Dwight D. Eisenhower',
            country='USA',
            title='Supreme Allied Commander',
            role_type='military',
            biography='Oversaw Allied Expeditionary Force in Western Europe.',
            ideology='Professional soldier, coalition strategist.',
            portrait_url='img/leaders/eisenhower.jpg',
            notable_quotes='["Plans are worthless, but planning is everything."]',
            key_operations='["Operation Overlord", "Operation Torch"]',
            influence_score=95.0
        ),
        Leader(
            name='Georgy Zhukov',
            country='USSR',
            title='Marshal of the Soviet Union',
            role_type='military',
            biography='Key Soviet commander renowned for defensive and offensive operations.',
            ideology='Communist military leadership loyal to Stalin.',
            portrait_url='img/leaders/zhukov.jpg',
            notable_quotes='["There are no invincible armies."]',
            key_operations='["Battle of Moscow", "Operation Bagration", "Battle of Berlin"]',
            influence_score=97.0
        ),
        Leader(
            name='Erwin Rommel',
            country='Germany',
            title='Field Marshal',
            role_type='military',
            biography='German commander famed for North African campaign.',
            ideology='Wehrmacht professional; critical of Nazi leadership late-war.',
            portrait_url='img/leaders/rommel.jpg',
            notable_quotes='["Sweat saves blood, blood saves lives."]',
            key_operations='["North African Campaign"]',
            influence_score=88.0
        ),
        Leader(
            name='Isoroku Yamamoto',
            country='Japan',
            title='Admiral of the Fleet',
            role_type='military',
            biography='Commander-in-chief of the Japanese Combined Fleet.',
            ideology='Imperial Japanese Navy strategist.',
            portrait_url='img/leaders/yamamoto.jpg',
            notable_quotes='["I fear all we have done is to awaken a sleeping giant."]',
            key_operations='["Attack on Pearl Harbor", "Battle of Midway"]',
            influence_score=90.0
        ),
        Leader(
            name='Franklin D. Roosevelt',
            country='USA',
            title='President',
            role_type='political',
            biography='U.S. President who led the nation during most of WWII.',
            ideology='New Deal liberalism, arsenal of democracy.',
            portrait_url='img/leaders/roosevelt.jpg',
            notable_quotes='["The only thing we have to fear is fear itself."]',
            key_operations='["Lend-Lease", "Operation Torch"]',
            influence_score=94.0
        ),
        Leader(
            name='Adolf Hitler',
            country='Germany',
            title='Führer',
            role_type='political',
            biography='Dictator of Nazi Germany responsible for initiating WWII and the Holocaust.',
            ideology='National Socialism, expansionism, racial supremacy.',
            portrait_url='img/leaders/hitler.jpg',
            notable_quotes='["Today we rule Germany, tomorrow the world."]',
            key_operations='["Operation Barbarossa", "Battle of Britain"]',
            influence_score=100.0
        ),
        Leader(
            name='Hideki Tojo',
            country='Japan',
            title='Prime Minister',
            role_type='political',
            biography='Japanese Prime Minister and general who approved the attack on Pearl Harbor.',
            ideology='Militarist nationalism.',
            portrait_url='img/leaders/tojo.jpg',
            notable_quotes='["It goes without saying that when survival is threatened, struggles erupt between peoples, and unfortunate wars between nations result."]',
            key_operations='["Pacific War"]',
            influence_score=89.0
        )
    ]

    for leader in leaders:
        db.session.add(leader)

    db.session.flush()

    # Command assignments linking leaders to operations/campaigns
    assignments = [
        CommandAssignment(
            leader=leaders[0],
            campaign=campaigns[0],
            position='Political leader supporting Allied strategy',
            start_date=datetime(1940, 5, 10),
            end_date=datetime(1945, 7, 26),
            notes='Key advocate for cross-channel invasion.'
        ),
        CommandAssignment(
            leader=leaders[1],
            operation=operations[0],
            position='Supreme Allied Commander',
            start_date=datetime(1943, 12, 24),
            end_date=datetime(1944, 8, 30),
            notes='Oversaw planning and execution of D-Day landings.'
        ),
        CommandAssignment(
            leader=leaders[2],
            operation=operations[4],
            position='Front Commander',
            start_date=datetime(1944, 6, 1),
            end_date=datetime(1944, 8, 19),
            notes='Directed massive Soviet offensive that liberated Belarus.'
        ),
        CommandAssignment(
            leader=leaders[3],
            campaign=campaigns[3],
            position='Afrika Korps Commander',
            start_date=datetime(1941, 2, 12),
            end_date=datetime(1943, 3, 9),
            notes='Applied maneuver warfare in desert campaigns.'
        ),
        CommandAssignment(
            leader=leaders[4],
            campaign=campaigns[2],
            position='Japanese Combined Fleet Commander',
            start_date=datetime(1941, 4, 1),
            end_date=datetime(1943, 4, 18),
            notes='Strategist behind Pearl Harbor and Midway operations.'
        ),
        CommandAssignment(
            leader=leaders[6],
            operation=operations[1],
            position='Supreme Commander of the Wehrmacht',
            start_date=datetime(1941, 6, 22),
            end_date=datetime(1941, 12, 5),
            notes='Initiated invasion against Soviet Union.'
        )
    ]

    for assignment in assignments:
        db.session.add(assignment)
    
    # Sample Territories
    territories = [
        Territory(name='France', latitude=46.2276, longitude=2.2137, controlled_by='Germany', 
                 date_controlled=datetime(1940, 6, 22), strategic_value=9, region='Europe'),
        Territory(name='Poland', latitude=51.9194, longitude=19.1451, controlled_by='Germany', 
                 date_controlled=datetime(1939, 10, 6), strategic_value=7, region='Europe'),
        Territory(name='Stalingrad', latitude=48.7080, longitude=44.5133, controlled_by='USSR', 
                 date_controlled=datetime(1943, 2, 2), strategic_value=10, region='Europe'),
        Territory(name='Normandy', latitude=49.1829, longitude=-0.3707, controlled_by='Allies', 
                 date_controlled=datetime(1944, 8, 30), strategic_value=8, region='Europe'),
        Territory(name='Pearl Harbor', latitude=21.3099, longitude=-157.8581, controlled_by='USA', 
                 date_controlled=datetime(1941, 12, 7), strategic_value=9, region='Pacific'),
        Territory(name='Midway Atoll', latitude=28.2072, longitude=-177.3733, controlled_by='USA', 
                 date_controlled=datetime(1942, 6, 7), strategic_value=6, region='Pacific'),
        Territory(name='North Africa', latitude=30.0444, longitude=31.2357, controlled_by='Allies', 
                 date_controlled=datetime(1943, 5, 13), strategic_value=7, region='Africa'),
        Territory(name='Berlin', latitude=52.5200, longitude=13.4050, controlled_by='Germany', 
                 date_controlled=datetime(1945, 5, 2), strategic_value=10, region='Europe')
    ]
    
    for territory in territories:
        db.session.add(territory)
    
    # Sample Resources (1941 data)
    resources_1941 = [
        Resource(nation='Germany', date=datetime(1941, 1, 1), oil=5000, steel=8000, 
                manpower=5000000, gdp=43000000000, morale=75, territory_count=15),
        Resource(nation='USA', date=datetime(1941, 1, 1), oil=15000, steel=12000, 
                manpower=8000000, gdp=200000000000, morale=70, territory_count=3),
        Resource(nation='USSR', date=datetime(1941, 1, 1), oil=8000, steel=10000, 
                manpower=12000000, gdp=42000000000, morale=65, territory_count=12),
        Resource(nation='United Kingdom', date=datetime(1941, 1, 1), oil=3000, steel=5000, 
                manpower=4000000, gdp=38000000000, morale=70, territory_count=8),
        Resource(nation='Japan', date=datetime(1941, 1, 1), oil=2000, steel=6000, 
                manpower=3000000, gdp=19000000000, morale=80, territory_count=10)
    ]
    
    # Sample Resources (1944 data)
    resources_1944 = [
        Resource(nation='Germany', date=datetime(1944, 1, 1), oil=2000, steel=5000, 
                manpower=3000000, gdp=35000000000, morale=45, territory_count=8),
        Resource(nation='USA', date=datetime(1944, 1, 1), oil=20000, steel=18000, 
                manpower=12000000, gdp=250000000000, morale=85, territory_count=5),
        Resource(nation='USSR', date=datetime(1944, 1, 1), oil=10000, steel=12000, 
                manpower=10000000, gdp=50000000000, morale=75, territory_count=15),
        Resource(nation='United Kingdom', date=datetime(1944, 1, 1), oil=4000, steel=7000, 
                manpower=5000000, gdp=45000000000, morale=80, territory_count=10),
        Resource(nation='Japan', date=datetime(1944, 1, 1), oil=500, steel=3000, 
                manpower=2000000, gdp=15000000000, morale=50, territory_count=5)
    ]
    
    for resource in resources_1941 + resources_1944:
        db.session.add(resource)
    
    # Sample Intelligence Reports
    intelligence = [
        IntelligenceReport(
            date=datetime(1941, 12, 6),
            classification='top_secret',
            source='radio_intercept',
            content='ENIGMA DECRYPT: Japanese fleet movements detected near Hawaii. Possible attack imminent.',
            decoded=True,
            side='axis',
            location='Pacific'
        ),
        IntelligenceReport(
            date=datetime(1944, 6, 5),
            classification='secret',
            source='spy',
            content='Allied forces massing in southern England. Large-scale operation expected within 48 hours.',
            decoded=False,
            side='allies',
            location='English Channel'
        ),
        IntelligenceReport(
            date=datetime(1942, 6, 3),
            classification='top_secret',
            source='decrypt',
            content='Japanese naval code broken. Midway operation details intercepted.',
            decoded=True,
            side='allies',
            location='Pacific'
        )
    ]
    
    for intel in intelligence:
        db.session.add(intel)

    # War crimes / humanitarian atrocities
    war_crimes = [
        WarCrime(
            title='Holocaust in Poland',
            event_date=datetime(1941, 7, 1),
            end_date=datetime(1945, 1, 27),
            location='Occupied Poland',
            region='Europe',
            perpetrators='Nazi Germany',
            victims='European Jews, Roma, political prisoners',
            death_toll=3000000,
            description='Systematic genocide carried out in extermination camps such as Auschwitz-Birkenau and Treblinka.',
            sources='["United States Holocaust Memorial Museum", "Nuremberg Trials"]',
            media_url='img/aftermath/holocaust.jpg',
            category='genocide'
        ),
        WarCrime(
            title='Nanjing Massacre',
            event_date=datetime(1937, 12, 13),
            end_date=datetime(1938, 2, 1),
            location='Nanjing, China',
            region='Asia',
            perpetrators='Imperial Japanese Army',
            victims='Chinese civilians and POWs',
            death_toll=200000,
            description='Mass murder and mass rape committed following the Japanese capture of Nanjing.',
            sources='["International Military Tribunal for the Far East", "Eyewitness accounts"]',
            media_url='img/aftermath/nanjing.jpg',
            category='atrocity'
        ),
        WarCrime(
            title='Bombing of Dresden',
            event_date=datetime(1945, 2, 13),
            end_date=datetime(1945, 2, 15),
            location='Dresden, Germany',
            region='Europe',
            perpetrators='Allied Strategic Bomber Forces',
            victims='German civilians',
            death_toll=25000,
            description='Firebombing campaign that devastated Dresden, raising debates about strategic bombing.',
            sources='["RAF Bomber Command reports", "USAAF mission logs"]',
            media_url='img/aftermath/dresden.jpg',
            category='civilian_bombing'
        ),
        WarCrime(
            title='Hiroshima Atomic Bombing',
            event_date=datetime(1945, 8, 6),
            end_date=datetime(1945, 8, 6),
            location='Hiroshima, Japan',
            region='Asia',
            perpetrators='United States Army Air Forces',
            victims='Japanese civilians',
            death_toll=140000,
            description='First use of atomic weapon in war resulting in massive civilian casualties.',
            sources='["US Strategic Bombing Survey", "Japanese government reports"]',
            media_url='img/aftermath/hiroshima.jpg',
            category='civilian_bombing'
        ),
        WarCrime(
            title='Katyn Massacre',
            event_date=datetime(1940, 4, 1),
            end_date=datetime(1940, 5, 1),
            location='Katyn Forest, USSR',
            region='Europe',
            perpetrators='NKVD (Soviet Secret Police)',
            victims='Polish officers and intelligentsia',
            death_toll=22000,
            description='Mass execution of captured Polish officers ordered by Soviet authorities.',
            sources='["Polish Red Cross", "Soviet archives"]',
            media_url='img/aftermath/katyn.jpg',
            category='mass_execution'
        )
    ]

    for crime in war_crimes:
        db.session.add(crime)

    # Economic data
    economic_stats = [
        EconomicStat(country='USA', year=1939, gdp=142.0, military_spending=1.9, production_tanks=0, production_aircraft=2000,
                     production_ships=12, production_artillery=500, trade_balance=3.0, inflation_index=1.0, war_debt=40.4, strain_index=15.0,
                     notes='Pre-war mobilization with lend-lease ramping up.'),
        EconomicStat(country='USA', year=1944, gdp=219.8, military_spending=90.9, production_tanks=29497, production_aircraft=96650,
                     production_ships=121, production_artillery=7000, trade_balance=10.5, inflation_index=1.7, war_debt=201.0, strain_index=68.2,
                     notes='Arsenal of Democracy at peak output.'),
        EconomicStat(country='Germany', year=1939, gdp=55.0, military_spending=23.5, production_tanks=2471, production_aircraft=8200,
                     production_ships=26, production_artillery=3200, trade_balance=-1.2, inflation_index=1.3, war_debt=80.3, strain_index=52.5,
                     notes='Economy geared toward rearmament.'),
        EconomicStat(country='Germany', year=1944, gdp=42.0, military_spending=38.0, production_tanks=18900, production_aircraft=39600,
                     production_ships=18, production_artillery=24000, trade_balance=-4.5, inflation_index=2.6, war_debt=230.0, strain_index=88.6,
                     notes='Strategic bombing and resource shortages degrading output.'),
        EconomicStat(country='USSR', year=1940, gdp=45.0, military_spending=15.6, production_tanks=27939, production_aircraft=10500,
                     production_ships=12, production_artillery=17000, trade_balance=-0.8, inflation_index=1.4, war_debt=95.0, strain_index=61.0,
                     notes='Industrial relocation eastward underway.'),
        EconomicStat(country='USSR', year=1944, gdp=50.5, military_spending=30.2, production_tanks=29100, production_aircraft=40100,
                     production_ships=20, production_artillery=141000, trade_balance=-1.5, inflation_index=2.1, war_debt=190.0, strain_index=84.7,
                     notes='Recovered capacity fueling major offensives.'),
        EconomicStat(country='Japan', year=1941, gdp=23.5, military_spending=11.3, production_tanks=1050, production_aircraft=5200,
                     production_ships=130, production_artillery=4200, trade_balance=-0.5, inflation_index=1.6, war_debt=60.0, strain_index=49.8,
                     notes='Empire reliant on imports; embargo pressure intense.'),
        EconomicStat(country='Japan', year=1944, gdp=21.0, military_spending=15.9, production_tanks=950, production_aircraft=28700,
                     production_ships=60, production_artillery=7200, trade_balance=-3.2, inflation_index=3.1, war_debt=140.0, strain_index=92.3,
                     notes='Naval blockade strangling economy; severe inflation.'),
        EconomicStat(country='United Kingdom', year=1939, gdp=29.7, military_spending=7.0, production_tanks=969, production_aircraft=7938,
                     production_ships=36, production_artillery=2200, trade_balance=-1.8, inflation_index=1.2, war_debt=60.5, strain_index=48.0,
                     notes='Mobilizing empire resources.'),
        EconomicStat(country='United Kingdom', year=1944, gdp=32.1, military_spending=17.5, production_tanks=4128, production_aircraft=26461,
                     production_ships=74, production_artillery=8700, trade_balance=-2.5, inflation_index=2.0, war_debt=230.0, strain_index=85.4,
                     notes='Total war economy under rationing.'),
    ]

    for stat in economic_stats:
        db.session.add(stat)

    # Military innovations timeline
    innovations = [
        MilitaryInnovation(
            name='Panzerkampfwagen V Panther',
            category='weapon',
            description='German medium tank combining firepower, armor, and mobility.',
            nation='Germany',
            year=1943,
            image_url='img/innovations/panther.jpg',
            notes='Developed in response to Soviet T-34. Strong frontal armor.'
        ),
        MilitaryInnovation(
            name='Supermarine Spitfire',
            category='weapon',
            description='British single-seat fighter aircraft crucial in Battle of Britain.',
            nation='United Kingdom',
            year=1938,
            image_url='img/innovations/spitfire.jpg',
            notes='Elliptical wing design excelled in dogfights.'
        ),
        MilitaryInnovation(
            name='Radar Early Warning Chain',
            category='technology',
            description='Integrated radar network providing early warning of incoming raids.',
            nation='United Kingdom',
            year=1940,
            image_url='img/innovations/radar.jpg',
            notes='Allowed RAF to vector fighters efficiently.'
        ),
        MilitaryInnovation(
            name='Enigma Decryption (ULTRA)',
            category='intelligence',
            description='Allied cryptanalysis project that decrypted German communications.',
            nation='Allied',
            year=1941,
            image_url='img/innovations/ultra.jpg',
            notes='Provided critical intelligence on Axis operations.'
        ),
        MilitaryInnovation(
            name='B-29 Superfortress',
            category='weapon',
            description='Long-range bomber used by the United States to strike Japan.',
            nation='USA',
            year=1944,
            image_url='img/innovations/b29.jpg',
            notes='Pressurized cabins and remote-controlled turrets.'
        )
    ]

    for innovation in innovations:
        db.session.add(innovation)
    
    db.session.commit()
    print("Database seeded successfully!")

