import random
import string
import discord
import json
import os

def random_color():
    return discord.Color.from_rgb(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def embed_template(title=None, description=None, color=None):
    if color is None:
        color = random_color()
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="dev 3h62")
    return embed

def success_embed(title="✅ 成功", description=None):
    embed = discord.Embed(title=title, description=description, color=discord.Color.green())
    embed.set_footer(text="dev 3h62")
    return embed

def error_embed(title="❌ エラー", description=None):
    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    embed.set_footer(text="dev 3h62")
    return embed

def info_embed(title="ℹ️ 情報", description=None):
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_footer(text="dev 3h62")
    return embed

def generate_coupon_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(100))

def generate_transfer_code():
    return ''.join(random.choice(string.digits) for _ in range(9))

def generate_pin():
    return ''.join(random.choice(string.digits) for _ in range(4))

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)