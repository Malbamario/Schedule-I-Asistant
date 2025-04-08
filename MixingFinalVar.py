APP_VERSION="V2.7"
MIXING_CALCULATOR_DATA_FILE = "mix_effects_dataV0.4.json"
MAX_EFFECT = 8
SUBSTANCE_STACK = 8
USER_RANK = 26
NO_REDUNDANT_PRODUCT = True
SPLIT_PRODUCTS=True
SPLIT_TYPE="File" #File or Sheet
REDUNDANT_PRODUCT_CODE = "NRP" if NO_REDUNDANT_PRODUCT else "RP"
SPLIT_PRODUCTS_CODE = "" if not SPLIT_PRODUCTS else "SPFL" if SPLIT_TYPE=="File" else "SPSH" if SPLIT_TYPE=="Sheet" else ""
OUTPUT_FILENAME = f"Output-M{MAX_EFFECT}S{SUBSTANCE_STACK}R{USER_RANK}{REDUNDANT_PRODUCT_CODE}_{SPLIT_PRODUCTS_CODE}_{APP_VERSION}.xlsx"
USER_SUBSTANCES = [
    # "Cuke",
    # "Flu Medicine",
    # "Gasoline",
    # "Donut",
    # "Energy Drink",
    # "Mouth Wash",
    # "Motor Oil",
    # "Banana",
    # "Chili",
    # "Iodine",
    # "Paracetamol",
    # "Viagra",
    # "Horse Semen",
    # "Mega Bean",
    # "Addy",
    # "Battery"
]
USER_PRODUCT_TYPE = [
    # "W01",
    # "W02",
    # "W03",
    # "W04",
    # "M01",
    # "C01",
]
USER_TARGET_EFFECTS = [
    # "Calming",
    # "Refreshing",
    # "Energizing",
    # "Sedating",
    # "Bright-Eyed",
    # "Calorie-Dense",
    # "Euphoric",
    # "Toxic",
    # "Athletic",
    # "Balding",
    # "Anti-Gravity",
    # "Munchies",
    # "Slippery",
    # "Gingeritis",
    # "Sneaky",
    # "Thought-Provoking",
    # "Spicy",
    # "Paranoia",
    # "Tropic Thunder",
    # "Glowing",
    # "Cyclopean",
    # "Foggy",
    # "Explosive",
    # "Laxative",
    # "Long Faced",
    # "Jennerising",
    # "Electrifying",
    # "Disorienting",
    # "Schizophrenia",
    # "Seizure-Inducing",
    # "Zombifying",
    # "Focused",
    # "Smelly",
    # "Shrinking"
]