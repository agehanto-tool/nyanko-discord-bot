import json
import random
import os
import uuid
import datetime

from io.input import PRICE_OVERRIDES, ORDER_LOG

try:
    from bcsfe import BattleCatsSaveEditor
    from bcsfe.files.save import SaveFile
    from bcsfe.utils import get_game_data
    BCSFE_AVAILABLE = True
except ImportError:
    BCSFE_AVAILABLE = False

ITEM_CONFIG = {
    "catfood_50000": {"label": "猫缶 50,000個", "price": 0, "cat": "resource"},
    "xp_max": {"label": "XP 99,999,999", "price": 0, "cat": "resource"},
    "np_max": {"label": "NP 9,999", "price": 0, "cat": "resource"},
    "nyan_ticket_999": {"label": "にゃんチケット 999枚", "price": 0, "cat": "resource"},
    "rare_tickets_999": {"label": "レアチケット 999枚", "price": 0, "cat": "resource"},
    "platinum_29": {"label": "プラチナチケット 29枚", "price": 0, "cat": "resource"},
    "legend_29": {"label": "レジェンドチケット 29枚", "price": 0, "cat": "resource"},
    "platinum_shard_90": {"label": "プラチナのかけら 90個", "price": 0, "cat": "resource"},
    "leadership_999": {"label": "リーダーシップ 999個", "price": 0, "cat": "resource"},
    "battle_items_999": {"label": "バトルアイテム全種 999個", "price": 0, "cat": "resource"},
    "matatabi_998": {"label": "マタタビ全種 998個", "price": 0, "cat": "resource"},
    "cats_eye_999": {"label": "キャッツアイ全種 999個", "price": 0, "cat": "resource"},
    "nekovitan_999": {"label": "ネコビタン全種 999個", "price": 0, "cat": "resource"},
    "castle_parts_999": {"label": "城素材全種 999個", "price": 0, "cat": "resource"},
    "event_ticket_999": {"label": "イベントチケット 999枚", "price": 0, "cat": "resource"},
    "honnou_99": {"label": "本能玉全種 99個", "price": 0, "cat": "resource"},
    "dungeon_medal_99": {"label": "地底迷宮メダル全種 99個", "price": 0, "cat": "resource"},
    "all_missions": {"label": "全ミッション完了", "price": 0, "cat": "stage"},
    "main_clear": {"label": "メインステージ全クリア+お宝金", "price": 0, "cat": "stage"},
    "zombie_clear": {"label": "メインゾンビステージ全クリア", "price": 0, "cat": "stage"},
    "old_legend_clear": {"label": "旧レジェンド全クリア", "price": 0, "cat": "stage"},
    "true_legend_clear": {"label": "真レジェンド全クリア", "price": 0, "cat": "stage"},
    "zero_legend_clear": {"label": "零レジェンド全クリア", "price": 0, "cat": "stage"},
    "makai_clear": {"label": "魔界編全クリア", "price": 0, "cat": "stage"},
    "event_clear": {"label": "イベントステージ全クリア", "price": 0, "cat": "stage"},
    "clear_nyanko_tower": {"label": "にゃんこ塔全クリア", "price": 0, "cat": "stage"},
    "all_char_unlock": {"label": "全キャラ開放", "price": 0, "cat": "chara"},
    "error_char_delete": {"label": "エラーキャラ削除", "price": 0, "cat": "chara"},
    "all_char_lv_max": {"label": "全キャラLvMAX", "price": 0, "cat": "chara"},
    "all_char_max_form": {"label": "全キャラ最大形態", "price": 0, "cat": "chara"},
    "all_honnou_max": {"label": "全キャラ本能全開放", "price": 0, "cat": "chara"},
    "telop_delete": {"label": "開放テロップ削除", "price": 0, "cat": "etc"},
    "slot_max": {"label": "編成スロット数最大拡張", "price": 0, "cat": "etc"},
    "medal_all": {"label": "にゃんこメダル全開放", "price": 0, "cat": "etc"},
    "enemy_book_all": {"label": "敵キャラ図鑑全開放", "price": 0, "cat": "etc"},
    "user_rank_all": {"label": "ユーザーランク報酬全受取", "price": 0, "cat": "etc"},
    "playtime_max": {"label": "プレイ時間カンスト", "price": 0, "cat": "etc"},
    "gold_pass": {"label": "ゴールド会員化", "price": 0, "cat": "etc"},
    "facility_max": {"label": "施設LvMAX", "price": 0, "cat": "etc"},
    "gamatoto_max": {"label": "ガマトトLvMAX", "price": 0, "cat": "etc"},
    "gamatoto_legend": {"label": "ガマトト助手全員レジェンド", "price": 0, "cat": "etc"},
    "ad_free": {"label": "広告非表示（β）", "price": 0, "cat": "etc"},
    "ototo_max": {"label": "オトート全城強化LvMAX", "price": 0, "cat": "etc"},
    "shrine_max": {"label": "にゃんこ神社LvMAX", "price": 0, "cat": "etc"},
}

def get_items_by_cat(cat):
    return {k: v for k, v in ITEM_CONFIG.items() if v["cat"] == cat}

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_price(item_key, guild_id=None):
    overrides = load_json(PRICE_OVERRIDES, {})
    if guild_id and str(guild_id) in overrides:
        if item_key in overrides[str(guild_id)]:
            return overrides[str(guild_id)][item_key]
    return ITEM_CONFIG[item_key]["price"]

def set_price(item_key, price, guild_id):
    try:
        overrides = load_json(PRICE_OVERRIDES, {})
        gid = str(guild_id)
        if gid not in overrides:
            overrides[gid] = {}
        overrides[gid][item_key] = price
        save_json(PRICE_OVERRIDES, overrides)
        return True
    except Exception as e:
        print(f"set_price error: {e}")
        return False

def log_order(user_id, items, service_type="normal"):
    orders = load_json(ORDER_LOG, [])
    orders.append({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "items": items,
        "type": service_type,
        "time": datetime.datetime.now().isoformat()
    })
    save_json(ORDER_LOG, orders)

class BCSFEAPI:
    def __init__(self):
        self.editor = None
        self.save_file = None
        self.game_data = None
        if BCSFE_AVAILABLE:
            self.editor = BattleCatsSaveEditor()
            self.game_data = get_game_data()

    def load_save(self, save_data: dict) -> bool:
        if not BCSFE_AVAILABLE:
            return False
        try:
            self.save_file = SaveFile(save_data)
            return True
        except Exception as e:
            print(f"load_save error: {e}")
            return False

    def load_save_from_file(self, filepath: str) -> bool:
        if not BCSFE_AVAILABLE:
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.load_save(data)
        except Exception as e:
            print(f"load_save_from_file error: {e}")
            return False

    def get_edited_data(self):
        if self.save_file:
            return self.save_file.to_dict()
        return None

    def save_to_file(self, filepath: str) -> bool:
        data = self.get_edited_data()
        if data:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"save_to_file error: {e}")
        return False

    def apply_edits(self, items: list) -> dict:
        if not self.save_file:
            return {"success": False, "error": "セーブデータが読み込まれていません"}

        results = {}
        for item in items:
            try:
                if item == "catfood_50000":
                    self.save_file.set_cat_food(50000)
                    results[item] = True
                elif item == "xp_max":
                    self.save_file.set_xp(99999999)
                    results[item] = True
                elif item == "np_max":
                    self.save_file.set_np(9999)
                    results[item] = True
                elif item == "nyan_ticket_999":
                    self.save_file.set_rare_tickets(999)
                    results[item] = True
                elif item == "rare_tickets_999":
                    self.save_file.set_normal_ticket_progress(99900)
                    results[item] = True
                elif item == "platinum_29":
                    self.save_file.set_platinum_shards(290)
                    results[item] = True
                elif item == "legend_29":
                    self.save_file.set_legend_tickets(29)
                    results[item] = True
                elif item == "platinum_shard_90":
                    self.save_file.set_platinum_shards(90)
                    results[item] = True
                elif item == "leadership_999":
                    self.save_file.add_leaderships(999)
                    results[item] = True
                elif item == "battle_items_999":
                    for battle_item in ['speedup', 'catmute', 'catcpu', 'sniper', 'richcat', 'treasure']:
                        self.save_file.add_battle_item(battle_item, 999)
                    results[item] = True
                elif item == "matatabi_998":
                    for color in ['red', 'blue', 'green', 'yellow', 'purple', 'rainbow']:
                        self.save_file.add_catamin(color, 998)
                    results[item] = True
                elif item == "cats_eye_999":
                    for eye_type in ['normal', 'rare', 'super_rare', 'ultra_rare', 'legend_rare']:
                        self.save_file.add_cat_eyes(eye_type, 999)
                    results[item] = True
                elif item == "nekovitan_999":
                    self.save_file.set_nekovitan_all(999)
                    results[item] = True
                elif item == "castle_parts_999":
                    self.save_file.set_castle_parts_all(999)
                    results[item] = True
                elif item == "event_ticket_999":
                    self.save_file.set_event_tickets(999)
                    results[item] = True
                elif item == "honnou_99":
                    self.save_file.set_honnou_all(99)
                    results[item] = True
                elif item == "dungeon_medal_99":
                    self.save_file.set_dungeon_medal_all(99)
                    results[item] = True
                elif item == "all_missions":
                    self.save_file.set_all_missions_complete()
                    results[item] = True
                elif item == "main_clear":
                    for chapter in range(1, 4):
                        self.save_file.set_story_complete('eoc', chapter, True)
                        self.save_file.set_story_complete('itf', chapter, True)
                        self.save_file.set_story_complete('cotc', chapter, True)
                    for treasure_id in range(1, 500):
                        try:
                            self.save_file.set_treasure_completed(treasure_id, True)
                            self.save_file.set_treasure_quality(treasure_id, 3)
                        except:
                            pass
                    results[item] = True
                elif item == "zombie_clear":
                    self.save_file.set_zombie_stage_complete_all()
                    results[item] = True
                elif item == "old_legend_clear":
                    self.save_file.set_legend_stage_complete_all()
                    results[item] = True
                elif item == "true_legend_clear":
                    self.save_file.set_true_legend_stage_complete_all()
                    results[item] = True
                elif item == "zero_legend_clear":
                    self.save_file.set_zero_legend_stage_complete_all()
                    results[item] = True
                elif item == "makai_clear":
                    self.save_file.set_makai_stage_complete_all()
                    results[item] = True
                elif item == "event_clear":
                    self.save_file.set_event_stage_complete_all()
                    results[item] = True
                elif item == "clear_nyanko_tower":
                    self.save_file.set_nyanko_tower_complete_all()
                    results[item] = True
                elif item == "all_char_unlock":
                    for unit_id in range(1, 3000):
                        try:
                            self.save_file.set_unit_owned(unit_id, True)
                        except:
                            pass
                    results[item] = True
                elif item == "error_char_delete":
                    self.save_file.delete_error_characters()
                    results[item] = True
                elif item == "all_char_lv_max":
                    for unit_id in range(1, 3000):
                        try:
                            self.save_file.set_unit_level(unit_id, 50)
                            self.save_file.set_unit_plus_level(unit_id, 70)
                        except:
                            pass
                    results[item] = True
                elif item == "all_char_max_form":
                    for unit_id in range(1, 3000):
                        try:
                            self.save_file.set_unit_evolution(unit_id, 4)
                        except:
                            pass
                    results[item] = True
                elif item == "all_honnou_max":
                    for unit_id in range(1, 3000):
                        try:
                            self.save_file.unlock_all_talents(unit_id)
                        except:
                            pass
                    results[item] = True
                elif item == "telop_delete":
                    self.save_file.delete_telop()
                    results[item] = True
                elif item == "slot_max":
                    self.save_file.max_slots()
                    results[item] = True
                elif item == "medal_all":
                    self.save_file.unlock_all_medals()
                    results[item] = True
                elif item == "enemy_book_all":
                    self.save_file.unlock_enemy_book_all()
                    results[item] = True
                elif item == "user_rank_all":
                    self.save_file.claim_all_user_rank_rewards()
                    results[item] = True
                elif item == "playtime_max":
                    self.save_file.set_playtime(99999999)
                    results[item] = True
                elif item == "gold_pass":
                    self.save_file.enable_gold_pass()
                    results[item] = True
                elif item == "facility_max":
                    facilities = ['cat_health', 'cat_attack', 'cat_defense', 'cat_speed', 'cat_ability', 'storage', 'cat_wallet', 'cat_energy', 'cat_construction']
                    for facility in facilities:
                        try:
                            self.save_file.set_facility_level(facility, 20)
                        except:
                            pass
                    results[item] = True
                elif item == "gamatoto_max":
                    self.save_file.set_gamatoto_level(99)
                    results[item] = True
                elif item == "gamatoto_legend":
                    self.save_file.set_gamatoto_legend_all()
                    results[item] = True
                elif item == "ad_free":
                    self.save_file.enable_ad_free()
                    results[item] = True
                elif item == "ototo_max":
                    self.save_file.max_ototo_fortress()
                    results[item] = True
                elif item == "shrine_max":
                    self.save_file.set_shrine_level(99)
                    results[item] = True
                else:
                    results[item] = False
            except Exception as e:
                print(f"apply_edits error for {item}: {e}")
                results[item] = False

        return {"success": True, "results": results}

    def generate_transfer_codes(self) -> dict:
        transfer = ''.join(random.choice('0123456789') for _ in range(9))
        pin = ''.join(random.choice('0123456789') for _ in range(4))
        return {"transfer_code": transfer, "pin": pin}
