import csv
import os

severity_samples = [
    # Critical (Indirect severity cues: explosion, toxic, gasoline, swallowing, smoke, hazard, collapse)
    ("Water from tap smells strongly of gasoline and has an oily chemical film floating on top.", "Water/Drainage", "Critical"),
    ("High voltage electrical transformer emitting thick black smoke and intense buzzing near plaza.", "Electricity", "Critical"),
    ("Open unlit construction pit on walking path with no barricades where pedestrians have fallen.", "Safety", "Critical"),
    ("Rotting carcass and maggots spilling from torn bags near school entrance creating biohazard.", "Waste", "Critical"),
    ("Sudden massive ground collapse swallowing vehicles near hospital emergency gate.", "Road", "Critical"),
    ("Severe raw sewage backflow pouring into multiple residential basements after pipe collapse.", "Water/Drainage", "Critical"),
    ("Exposed live electrical wiring submerged in standing rainwater near children play area.", "Electricity", "Critical"),
    ("Toxic chemical stench and dark fumes leaking from abandoned barrels near riverbank.", "Waste", "Critical"),
    ("Bridge support pillar cracked severely with visible structural shifting under heavy loads.", "Road", "Critical"),
    ("Natural gas odor leaking heavily from cracked main underground pipe junction.", "Safety", "Critical"),

    # High (Indirect severity cues: dozens, widespread, aggressive, drag racing, deep crater, broken main)
    ("Dozens of ripped garbage bags scattered by dogs leaving rotting meat across public walkway.", "Waste", "High"),
    ("Illegal late night drag racing and roaring engines keeping hundreds of residents awake until 3 AM.", "Safety", "High"),
    ("Deep crater pothole on high speed expressway causing severe wheel damage and sudden swerving.", "Road", "High"),
    ("Pack of aggressive stray dogs chasing and biting at morning commuters near transit station.", "Safety", "High"),
    ("Total power blackout affecting entire commercial district during peak business hours.", "Electricity", "High"),
    ("Clogged main storm drain causing waist deep water flooding across major avenue.", "Water/Drainage", "High"),
    ("Overhanging heavy dead tree limb dangling directly above busy bus stop bench.", "Safety", "High"),
    ("Sparking power cables touching tree branches causing localized fire flashes.", "Electricity", "High"),
    ("Massive pile of uncollected commercial food waste attracting swarms of flies and rats.", "Waste", "High"),
    ("Sharp broken glass shards and metal rusted sheets scattered across public park playground.", "Safety", "High"),
    ("Retaining wall leaning heavily with falling rocks threatening passing cars.", "Road", "High"),
    ("Flooded pedestrian underpass completely impassable after heavy thunderstorm.", "Water/Drainage", "High"),

    # Medium (Indirect severity cues: moderate disruption, single location, localized, dumped items)
    ("Five old CRT television monitors and electronic scrap dumped in creek bed.", "Waste", "Medium"),
    ("Damaged speed bump with loose asphalt chunks scattered in residential alley.", "Road", "Medium"),
    ("Low water pressure on upper floors of 4-story apartment building.", "Water/Drainage", "Medium"),
    ("Intermittent streetlight flickering every few minutes along residential street.", "Electricity", "Medium"),
    ("Abandoned derelict vehicle parked illegally blocking community alleyway.", "Safety", "Medium"),
    ("Loud commercial air conditioner unit humming continuously past midnight.", "Other", "Medium"),
    ("Overflowing public trash can behind market needing daily clearing.", "Waste", "Medium"),
    ("Sunken road section collecting stagnant puddle after rain.", "Road", "Medium"),
    ("Broken lock on public restroom booth door requiring repair.", "Other", "Medium"),
    ("Graffiti tags painted across side wall of civic community hall.", "Other", "Medium"),
    ("Loose manhole cover making loud clanking sound when driven over.", "Road", "Medium"),
    ("Stagnant water pooling in clogged roadside gutter emitting mild odor.", "Water/Drainage", "Medium"),

    # Low (Indirect severity cues: minor, cosmetic, single bulb, weeds, dandelions, slight)
    ("Public library garden overgrown with dandelions and weeds around bench.", "Other", "Low"),
    ("Streetlight pole fixture completely dark at end of quiet cul-de-sac.", "Electricity", "Low"),
    ("Single light bulb burnt out in streetlight post #402.", "Electricity", "Low"),
    ("Minor crack on concrete sidewalk pavement near park entrance.", "Road", "Low"),
    ("Faded zebra crossing lines needing repainting near community park.", "Road", "Low"),
    ("Small pile of dry leaves waiting for scheduled weekend garden pickup.", "Waste", "Low"),
    ("Public drinking water fountain button sticking slightly when pressed.", "Water/Drainage", "Low"),
    ("Notice board glass smudged at neighborhood council hall.", "Other", "Low"),
    ("Public park lawn grass slightly tall near flower beds.", "Other", "Low"),
    ("Small gravel accumulation on corner of residential street.", "Road", "Low"),
    ("Dry tree twigs lying on sidewalk after mild breeze.", "Safety", "Low")
]

csv_path = "data/training_data.csv"
if os.path.exists(csv_path):
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in severity_samples:
            writer.writerow(row)
    print(f"Successfully appended {len(severity_samples)} severity/urgency training samples to {csv_path}.")
else:
    print(f"File {csv_path} not found.")
