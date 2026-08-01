import os

IO_DIR = os.path.dirname(__file__)

INPUT_DIR = os.path.join(IO_DIR, "input")
UNINPUT_DIR = os.path.join(IO_DIR, "uninput")

PAYPAY_DATA = os.path.join(INPUT_DIR, "paypay_data.json")
KYASH_DATA = os.path.join(INPUT_DIR, "kyash_data.json")
USER_DATA = os.path.join(INPUT_DIR, "user_data.json")
SHOP_DATA = os.path.join(INPUT_DIR, "shop_data.json")
PRICE_OVERRIDES = os.path.join(INPUT_DIR, "price_overrides.json")
ORDER_LOG = os.path.join(INPUT_DIR, "order_log.json")