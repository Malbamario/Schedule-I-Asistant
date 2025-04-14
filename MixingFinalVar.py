import yaml

with open("produce_config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

APP_VERSION                 = config['APP_VERSION']
MIXING_CALCULATOR_DATA_FILE = config['MIXING_CALCULATOR_DATA_FILE']
MAX_EFFECT                  = config['MAX_EFFECT']
SUBSTANCE_STACK             = config['SUBSTANCE_STACK']
USER_RANK                   = config['USER_RANK']
MODE                        = config['MODE']
NO_REDUNDANT_PRODUCT        = config['NO_REDUNDANT_PRODUCT']
SPLIT_PRODUCTS              = config['SPLIT_PRODUCTS']
SPLIT_TYPE                  = config['SPLIT_TYPE']
USER_SUBSTANCES             = config['USER_SUBSTANCES']
USER_PRODUCT_TYPE           = config['USER_PRODUCT_TYPE']
USER_TARGET_EFFECTS         = config['USER_TARGET_EFFECTS']

REDUNDANT_PRODUCT_CODE= "NRP" if NO_REDUNDANT_PRODUCT else "RP"
SPLIT_PRODUCTS_CODE= "" if not SPLIT_PRODUCTS else "SPFL" if SPLIT_TYPE=="File" else "SPSH" if SPLIT_TYPE=="Sheet" else ""
OUTPUT_FILENAME= f"Output-{MODE}M{MAX_EFFECT}S{SUBSTANCE_STACK}R{USER_RANK}{REDUNDANT_PRODUCT_CODE}_{SPLIT_PRODUCTS_CODE}_{APP_VERSION}.xlsx"
