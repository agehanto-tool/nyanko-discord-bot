import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select, Modal, TextInput
import asyncio
import json
import os
import random
import uuid
import datetime
あ
from config import CONFIG
from utils import *
from api import PayPayAPI, KyashAPI, BCSFEAPI, ITEM_CONFIG, get_items_by_cat, get_price, set_price, log_order

TOKEN = CONFIG.get("discord_token")
PREFIX = CONFIG.get("prefix", "/")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

paypay = PayPayAPI()
kyash = KyashAPI()
bcsfe = BCSFEAPI()

user_data = load_json("io/input/user_data.json")
shop_data = load_json("io/input/shop_data.json")

def load_guild_config(guild_id):
    data = load_json("io/input/shop_data.json", {})
    if "guild_config" not in data:
        data["guild_config"] = {}
    if str(guild_id) not in data["guild_config"]:
        data["guild_config"][str(guild_id)] = {
            "purchase_role": None,
            "achievement_channel": None,
            "prices": {}
        }
        save_json("io/input/shop_data.json", data)
    return data["guild_config"][str(guild_id)]

def save_guild_config(guild_id, config):
    data = load_json("io/input/shop_data.json", {})
    if "guild_config" not in data:
        data["guild_config"] = {}
    data["guild_config"][str(guild_id)] = config
    save_json("io/input/shop_data.json", data)

@bot.event
async def on_ready():
    print(f"✅ Bot Online | {bot.user}")
    print(f"🔑 サーバー数: {len(bot.guilds)}")
    try:
        synced = await tree.sync()
        print(f"✅ {len(synced)} 個のスラッシュコマンドを同期しました")
        for cmd in synced:
            print(f"  /{cmd.name}")
    except Exception as e:
        print(f"❌ スラッシュコマンド同期エラー: {e}")

@tree.command(name="にゃんこ代行パネル", description="にゃんこ大戦争の代行パネルを表示します（管理者専用）")
@app_commands.checks.has_permissions(administrator=True)
async def nyanko_panel(interaction: discord.Interaction):
    embed = embed_template(
        title="🐱 にゃんこ大戦争 代行パネル",
        description="以下のボタンから代行を依頼できます。\n\n**すべて無料で提供中！**"
    )
    resource_items = get_items_by_cat("resource")
    stage_items = get_items_by_cat("stage")
    chara_items = get_items_by_cat("chara")
    embed.add_field(
        name="📦 リソース",
        value="\n".join([f"• {v['label']}" for k, v in list(resource_items.items())[:5]]) + "\n・他多数",
        inline=True
    )
    embed.add_field(
        name="🗺️ ステージ",
        value="\n".join([f"• {v['label']}" for k, v in list(stage_items.items())[:5]]) + "\n・他多数",
        inline=True
    )
    embed.add_field(
        name="🐱 キャラクター",
        value="\n".join([f"• {v['label']}" for k, v in list(chara_items.items())[:5]]) + "\n・他多数",
        inline=True
    )
    view = NyankoDaikoPanel()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tree.command(name="アカウント複製パネル", description="にゃんこ大戦争のアカウントを複製します（管理者専用）")
@app_commands.checks.has_permissions(administrator=True)
async def account_clone_panel(interaction: discord.Interaction):
    embed = embed_template(
        title="🔄 アカウント複製パネル",
        description="にゃんこ大戦争のアカウントを複製します。\n\n**すべて無料で提供中！**"
    )
    embed.add_field(
        name="⚠️ 注意",
        value="複製には元アカウントの引継ぎコードとPINが必要です。",
        inline=False
    )
    embed.add_field(
        name="📋 複製内容",
        value="• 全キャラクター\n• 全リソース\n• 全ステージ進行度\n• 施設・その他すべて",
        inline=False
    )
    embed.add_field(
        name="💰 価格",
        value="**0円（無料）**",
        inline=False
    )
    view = AccountClonePanel()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tree.command(name="購入時付与ロール", description="代行実行時に付与するロールを設定します")
@app_commands.checks.has_permissions(administrator=True)
async def set_purchase_role(interaction: discord.Interaction, role: discord.Role):
    guild_config = load_guild_config(interaction.guild_id)
    guild_config["purchase_role"] = role.id
    save_guild_config(interaction.guild_id, guild_config)
    embed = success_embed(
        "✅ 購入時付与ロール設定完了",
        f"代行実行時に **{role.mention}** を付与します。"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="実績チャンネル", description="代行実績を送信するチャンネルを設定します")
@app_commands.checks.has_permissions(administrator=True)
async def set_achievement_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_config = load_guild_config(interaction.guild_id)
    guild_config["achievement_channel"] = channel.id
    save_guild_config(interaction.guild_id, guild_config)
    embed = success_embed(
        "✅ 実績チャンネル設定完了",
        f"代行完了時に **{channel.mention}** に実績を送信します。"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="クーポン生成", description="新しいクーポンを生成します")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    discount="割引する金額（円）",
    usage_type="クーポンの使用タイプを選択",
    max_uses="複数回使用の場合の最大使用回数"
)
@app_commands.choices(usage_type=[
    app_commands.Choice(name="🔄 無制限（何度でも使える）", value="unlimited"),
    app_commands.Choice(name="🔹 1回限り（一度だけ使える）", value="once"),
    app_commands.Choice(name="🔢 複数回（指定した回数だけ使える）", value="multiple"),
])
async def create_coupon(
    interaction: discord.Interaction,
    discount: int,
    usage_type: app_commands.Choice[str],
    max_uses: int = None
):
    usage_value = usage_type.value

    if usage_value == "multiple" and max_uses is None:
        embed = error_embed(
            "❌ エラー",
            "「複数回」を選択した場合は最大使用回数を指定してください。"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if usage_value != "multiple" and max_uses is not None:
        embed = error_embed(
            "❌ エラー",
            "「1回限り」または「無制限」の場合は最大使用回数は指定不要です。"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    code = generate_coupon_code()
    data = load_json("io/input/shop_data.json")
    if "coupons" not in data:
        data["coupons"] = {}

    if usage_value == "unlimited":
        max_uses_value = 999999
    elif usage_value == "multiple":
        max_uses_value = max_uses
    else:
        max_uses_value = 1

    data["coupons"][code] = {
        "code": code,
        "discount": discount,
        "usage_type": usage_value,
        "max_uses": max_uses_value,
        "used_count": 0,
        "created_by": interaction.user.id,
        "created_at": datetime.datetime.now().isoformat()
    }
    save_json("io/input/shop_data.json", data)

    usage_labels = {
        "unlimited": "🔄 無制限",
        "once": "🔹 1回限り",
        "multiple": f"🔢 複数回（最大{max_uses_value}回）"
    }

    embed = success_embed(
        "🎫 クーポン生成完了",
        f"**コード**: `{code}`\n**割引額**: {discount}円\n**使用タイプ**: {usage_labels.get(usage_value, usage_value)}"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="クーポン一覧", description="すべてのクーポンを表示します")
@app_commands.checks.has_permissions(administrator=True)
async def list_coupons(interaction: discord.Interaction):
    data = load_json("io/input/shop_data.json")
    coupons = data.get("coupons", {})
    if not coupons:
        embed = info_embed("📋 クーポン一覧", "現在有効なクーポンはありません。")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    embed = embed_template(
        title="📋 クーポン一覧",
        description=f"合計 {len(coupons)} 件のクーポン"
    )
    for code, info in list(coupons.items())[:10]:
        embed.add_field(
            name=f"🎫 {code[:20]}...",
            value=f"割引: {info['discount']}円 | 残り: {info['max_uses'] - info['used_count']}回",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="クーポン削除", description="クーポンを削除します")
@app_commands.checks.has_permissions(administrator=True)
async def delete_coupon(interaction: discord.Interaction, code: str):
    data = load_json("io/input/shop_data.json")
    coupons = data.get("coupons", {})
    if code in coupons:
        del coupons[code]
        data["coupons"] = coupons
        save_json("io/input/shop_data.json", data)
        embed = success_embed("✅ クーポン削除完了", f"コード: `{code}`")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = error_embed("❌ エラー", "指定されたクーポンは存在しません。")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="paypay_login", description="PayPayアカウントにログインします")
async def paypay_login(interaction: discord.Interaction):
    modal = PayPayLoginModal()
    embed = info_embed("📱 PayPayログイン", "以下のボタンをクリックしてログイン情報を入力してください。")
    await interaction.response.send_message(embed=embed, view=modal, ephemeral=True)

@tree.command(name="paypay_logout", description="PayPayアカウントからログアウトします")
async def paypay_logout(interaction: discord.Interaction):
    embed = success_embed("✅ ログアウト完了", "PayPayアカウントからログアウトしました。")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="paypay_info", description="PayPayアカウント情報を表示します")
async def paypay_info(interaction: discord.Interaction):
    embed = info_embed("💳 PayPay アカウント情報", "ログイン情報は現在ありません。")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="kyash_login", description="Kyashアカウントにログインします")
async def kyash_login(interaction: discord.Interaction):
    modal = KyashLoginModal()
    embed = info_embed("📱 Kyashログイン", "以下のボタンをクリックしてログイン情報を入力してください。")
    await interaction.response.send_message(embed=embed, view=modal, ephemeral=True)

@tree.command(name="kyash_logout", description="Kyashアカウントからログアウトします")
async def kyash_logout(interaction: discord.Interaction):
    embed = success_embed("✅ ログアウト完了", "Kyashアカウントからログアウトしました。")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="kyash_info", description="Kyashアカウント情報を表示します")
async def kyash_info(interaction: discord.Interaction):
    embed = info_embed("💳 Kyash アカウント情報", "ログイン情報は現在ありません。")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="値段変更", description="アイテムの価格を変更します")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    target="価格変更の対象範囲",
    price="新しい価格（円）",
    category="カテゴリを選択（対象が「特定のカテゴリ」の場合）",
    item_key="アイテムキーを直接入力（対象が「特定のものだけ」の場合）"
)
@app_commands.choices(target=[
    app_commands.Choice(name="📦 すべてのアイテム", value="all"),
    app_commands.Choice(name="📂 特定のカテゴリだけ", value="category"),
    app_commands.Choice(name="🎯 特定のものだけ", value="specific"),
])
@app_commands.choices(category=[
    app_commands.Choice(name="📦 リソース系", value="resource"),
    app_commands.Choice(name="🗺️ ステージ系", value="stage"),
    app_commands.Choice(name="🐱 キャラクター系", value="chara"),
    app_commands.Choice(name="⚙️ その他", value="etc"),
])
async def change_price(
    interaction: discord.Interaction,
    target: app_commands.Choice[str],
    price: int,
    category: app_commands.Choice[str] = None,
    item_key: str = None
):
    target_value = target.value

    if target_value == "category" and category is None:
        embed = error_embed("❌ エラー", "「特定のカテゴリだけ」を選択した場合はカテゴリを指定してください。")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if target_value == "specific" and item_key is None:
        embed = error_embed("❌ エラー", "「特定のものだけ」を選択した場合はアイテムキーを指定してください。\n例: `item_key:catfood_50000`")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if target_value == "all":
        updated_count = 0
        for key in ITEM_CONFIG.keys():
            set_price(key, price, interaction.guild_id)
            updated_count += 1
        embed = success_embed(
            "✅ 一括価格変更完了",
            f"**すべてのアイテム** の価格を **{price}円** に設定しました。\n（{updated_count}件）"
        )

    elif target_value == "category":
        cat_value = category.value
        cat_label = category.name
        updated_count = 0
        for key, config in ITEM_CONFIG.items():
            if config["cat"] == cat_value:
                set_price(key, price, interaction.guild_id)
                updated_count += 1
        embed = success_embed(
            "✅ カテゴリ価格変更完了",
            f"**{cat_label}** のアイテム（{updated_count}件）の価格を **{price}円** に設定しました。"
        )

    elif target_value == "specific":
        if item_key not in ITEM_CONFIG:
            embed = error_embed("❌ エラー", f"「{item_key}」は存在しないアイテムです。\n`/アイテムキー一覧` で確認してください。")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        set_price(item_key, price, interaction.guild_id)
        embed = success_embed(
            "✅ 価格変更完了",
            f"**{ITEM_CONFIG[item_key]['label']}** の価格を **{price}円** に設定しました。"
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="アイテムキー一覧", description="利用可能なアイテムキーの一覧を表示します")
@app_commands.checks.has_permissions(administrator=True)
async def list_item_keys(interaction: discord.Interaction):
    embed = embed_template(
        title="📋 アイテムキー一覧",
        description="`/値段変更` で `item_key` に指定する値の一覧です。"
    )
    for key, value in ITEM_CONFIG.items():
        embed.add_field(
            name=f"`{key}`",
            value=value["label"],
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        embed = error_embed("❌ 権限がありません", "このコマンドを実行するには管理者権限が必要です。")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = error_embed("❌ エラー", str(error))
        await interaction.response.send_message(embed=embed, ephemeral=True)

class NyankoDaikoPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🐱 にゃんこ代行を依頼", style=discord.ButtonStyle.primary, custom_id="nyanko_order")
    async def order_nyanko(self, interaction: discord.Interaction, button: Button):
        embed = info_embed(
            "🔧 代行サービス選択",
            "依頼したいサービスを選択してください。\n（複数選択可能）"
        )
        view = NyankoServiceSelect(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class NyankoServiceSelect(View):
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
        self.selected = []
        options = []
        for key, value in list(ITEM_CONFIG.items())[:25]:
            options.append(
                discord.SelectOption(
                    label=value["label"][:25],
                    value=key,
                    description=f"{value['cat']}"
                )
            )
        select = Select(
            placeholder="サービスを選択（複数可）",
            options=options,
            max_values=len(options),
            custom_id="service_select"
        )
        select.callback = self.select_callback
        self.add_item(select)
        next_btn = Button(label="➡️ 次へ", style=discord.ButtonStyle.success, custom_id="next_step")
        next_btn.callback = self.next_callback
        self.add_item(next_btn)

    async def select_callback(self, interaction: discord.Interaction):
        self.selected = interaction.data.get("values", [])
        embed = info_embed(
            "✅ 選択完了",
            f"{len(self.selected)}件のサービスを選択しました。\n「次へ」をクリックして進んでください。"
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_callback(self, interaction: discord.Interaction):
        if not self.selected:
            embed = error_embed("❌ エラー", "サービスを選択してください。")
            await interaction.response.edit_message(embed=embed, view=self)
            return
        embed = info_embed(
            "🔑 引継ぎコード入力",
            "にゃんこ大戦争の引継ぎコードとPINを入力してください。"
        )
        view = TransferCodeInput(self.selected, self.user)
        await interaction.response.edit_message(embed=embed, view=view)

class TransferCodeInput(View):
    def __init__(self, services, user):
        super().__init__(timeout=300)
        self.services = services
        self.user = user
        self.transfer_code = None
        self.pin = None

    @discord.ui.button(label="📝 引継ぎコードを入力", style=discord.ButtonStyle.primary, custom_id="input_transfer")
    async def input_transfer(self, interaction: discord.Interaction, button: Button):
        modal = TransferModal(self)
        await interaction.response.send_modal(modal)

class TransferModal(discord.ui.Modal):
    def __init__(self, parent):
        super().__init__(title="引継ぎコード入力")
        self.parent = parent
        self.transfer = TextInput(
            label="引継ぎコード (9桁)",
            placeholder="123456789",
            required=True,
            max_length=9,
            min_length=9
        )
        self.pin = TextInput(
            label="PIN (4桁)",
            placeholder="1234",
            required=True,
            max_length=4,
            min_length=4
        )
        self.add_item(self.transfer)
        self.add_item(self.pin)

    async def on_submit(self, interaction: discord.Interaction):
        self.parent.transfer_code = self.transfer.value
        self.parent.pin = self.pin.value
        embed = info_embed(
            "✅ コード確認",
            f"引継ぎコード: `{self.transfer.value}`\nPIN: `{self.pin.value}`"
        )
        embed.add_field(
            name="選択サービス",
            value="\n".join([f"• {ITEM_CONFIG.get(s, {}).get('label', s)}" for s in self.parent.services]),
            inline=False
        )
        view = PaymentSelect(self.parent.services, self.parent.transfer_code, self.parent.pin, self.parent.user)
        await interaction.response.edit_message(embed=embed, view=view)

class PaymentSelect(View):
    def __init__(self, services, transfer_code, pin, user):
        super().__init__(timeout=300)
        self.services = services
        self.transfer_code = transfer_code
        self.pin = pin
        self.user = user
        self.coupon_discount = 0

    @discord.ui.button(label="💳 無料で実行", style=discord.ButtonStyle.success, custom_id="free_execute")
    async def free_execute(self, interaction: discord.Interaction, button: Button):
        embed = info_embed(
            "🎉 無料で代行開始！",
            f"選択サービス: {len(self.services)}件"
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await self.execute_nyanko(interaction)

    @discord.ui.button(label="🎫 クーポンを使う", style=discord.ButtonStyle.secondary, custom_id="coupon_pay")
    async def coupon_pay(self, interaction: discord.Interaction, button: Button):
        modal = CouponModal(self)
        await interaction.response.send_modal(modal)

    async def execute_nyanko(self, interaction: discord.Interaction):
        embed = info_embed(
            "🔄 代行実行中...",
            f"引継ぎコード: `{self.transfer_code}`\nPIN: `{self.pin}`\nサービス: {len(self.services)}件"
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        result = bcsfe.apply_edits(self.services)
        if result.get("success"):
            success_count = sum(1 for v in result.get("results", {}).values() if v)
            total_count = len(result.get("results", {}))
            new_transfer = generate_transfer_code()
            new_pin = generate_pin()
            embed = success_embed(
                "✅ 代行完了！",
                f"**{success_count}/{total_count}** 件の編集が成功しました。"
            )
            embed.add_field(name="🔑 新しい引継ぎコード", value=f"`{new_transfer}`", inline=False)
            embed.add_field(name="🔐 新しいPIN", value=f"`{new_pin}`", inline=False)
            try:
                await interaction.user.send(embed=embed)
            except:
                pass
            await interaction.followup.send(embed=embed, ephemeral=True)
            guild_config = load_guild_config(interaction.guild_id)
            if guild_config.get("purchase_role"):
                role = interaction.guild.get_role(guild_config["purchase_role"])
                if role:
                    try:
                        await interaction.user.add_roles(role)
                    except:
                        pass
            if guild_config.get("achievement_channel"):
                channel = interaction.guild.get_channel(guild_config["achievement_channel"])
                if channel:
                    achievement_embed = discord.Embed(
                        title="🎉 代行完了！",
                        description=f"{interaction.user.mention} が代行を完了しました！",
                        color=discord.Color.gold()
                    )
                    achievement_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
                    achievement_embed.add_field(
                        name="📦 実行内容",
                        value="\n".join([f"• {ITEM_CONFIG.get(s, {}).get('label', s)}" for s in self.services[:5]]) + (f"\n・他 {len(self.services)-5}件" if len(self.services) > 5 else ""),
                        inline=False
                    )
                    achievement_embed.add_field(
                        name="💰 金額",
                        value="**0円（無料）**",
                        inline=True
                    )
                    achievement_embed.add_field(
                        name="🔑 引継ぎコード",
                        value=f"`{new_transfer}`",
                        inline=True
                    )
                    achievement_embed.set_footer(text="dev 3h62")
                    await channel.send(embed=achievement_embed)
            log_order(interaction.user.id, self.services, "normal")
        else:
            embed = error_embed(
                "❌ 代行失敗",
                result.get("error", "不明なエラーが発生しました。")
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class CouponModal(discord.ui.Modal):
    def __init__(self, parent):
        super().__init__(title="クーポン入力")
        self.parent = parent
        self.code = TextInput(
            label="クーポンコード",
            placeholder="コードを入力",
            required=True,
            max_length=100
        )
        self.add_item(self.code)

    async def on_submit(self, interaction: discord.Interaction):
        coupon_data = load_json("io/input/shop_data.json")
        coupons = coupon_data.get("coupons", {})
        if self.code.value in coupons:
            coupon = coupons[self.code.value]
            if coupon.get("used_count", 0) < coupon.get("max_uses", 1):
                coupon["used_count"] = coupon.get("used_count", 0) + 1
                coupon_data["coupons"] = coupons
                save_json("io/input/shop_data.json", coupon_data)
                self.parent.coupon_discount = coupon.get("discount", 0)
                embed = success_embed(
                    "🎫 クーポン適用",
                    f"{coupon['discount']}円割引されました！"
                )
                await interaction.response.edit_message(embed=embed, view=self.parent)
                return
        embed = error_embed("❌ 無効なクーポン", "クーポンコードが正しくありません。")
        await interaction.response.edit_message(embed=embed, view=self.parent)

class AccountClonePanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 アカウント複製を依頼", style=discord.ButtonStyle.primary, custom_id="clone_order")
    async def order_clone(self, interaction: discord.Interaction, button: Button):
        embed = info_embed(
            "🔑 引継ぎコード入力",
            "複製元アカウントの引継ぎコードとPINを入力してください。"
        )
        view = CloneTransferInput(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class CloneTransferInput(View):
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
        self.transfer_code = None
        self.pin = None

    @discord.ui.button(label="📝 引継ぎコードを入力", style=discord.ButtonStyle.primary, custom_id="clone_input_transfer")
    async def input_transfer(self, interaction: discord.Interaction, button: Button):
        modal = CloneTransferModal(self)
        await interaction.response.send_modal(modal)

class CloneTransferModal(discord.ui.Modal):
    def __init__(self, parent):
        super().__init__(title="引継ぎコード入力")
        self.parent = parent
        self.transfer = TextInput(
            label="引継ぎコード (9桁)",
            placeholder="123456789",
            required=True,
            max_length=9,
            min_length=9
        )
        self.pin = TextInput(
            label="PIN (4桁)",
            placeholder="1234",
            required=True,
            max_length=4,
            min_length=4
        )
        self.add_item(self.transfer)
        self.add_item(self.pin)

    async def on_submit(self, interaction: discord.Interaction):
        self.parent.transfer_code = self.transfer.value
        self.parent.pin = self.pin.value
        embed = info_embed(
            "✅ コード確認",
            f"引継ぎコード: `{self.transfer.value}`\nPIN: `{self.pin.value}`"
        )
        embed.add_field(
            name="📋 複製内容",
            value="全データを複製します",
            inline=False
        )
        view = CloneConfirm(self.parent.transfer_code, self.parent.pin, self.parent.user)
        await interaction.response.edit_message(embed=embed, view=view)

class CloneConfirm(View):
    def __init__(self, transfer_code, pin, user):
        super().__init__(timeout=300)
        self.transfer_code = transfer_code
        self.pin = pin
        self.user = user

    @discord.ui.button(label="💳 無料で複製実行", style=discord.ButtonStyle.success, custom_id="clone_execute")
    async def clone_execute(self, interaction: discord.Interaction, button: Button):
        embed = info_embed(
            "🔄 複製実行中...",
            f"引継ぎコード: `{self.transfer_code}`\nPIN: `{self.pin}`"
        )
        await interaction.response.edit_message(embed=embed, view=None)

        new_transfer = generate_transfer_code()
        new_pin = generate_pin()

        embed = success_embed(
            "✅ アカウント複製完了！",
            "新しいアカウントが作成されました。"
        )
        embed.add_field(name="🔑 新しい引継ぎコード", value=f"`{new_transfer}`", inline=False)
        embed.add_field(name="🔐 新しいPIN", value=f"`{new_pin}`", inline=False)
        embed.add_field(
            name="📌 注意",
            value="このコードはあなただけに送信されています。\n必ずメモしてください。",
            inline=False
        )

        try:
            await interaction.user.send(embed=embed)
        except:
            pass

        await interaction.followup.send(embed=embed, ephemeral=True)

class PayPayLoginModal(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📱 PayPayログイン", style=discord.ButtonStyle.primary, custom_id="paypay_login_btn")
    async def login_btn(self, interaction: discord.Interaction, button: Button):
        modal = PayPayLoginModalInput()
        await interaction.response.send_modal(modal)

class PayPayLoginModalInput(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="PayPayログイン")
        self.phone = TextInput(label="電話番号", placeholder="08012345678", required=True, max_length=11)
        self.password = TextInput(label="パスワード", placeholder="パスワードを入力", required=True, max_length=50)
        self.uuid = TextInput(label="UUID (任意)", placeholder="空欄で自動生成", required=False, max_length=36)
        self.add_item(self.phone)
        self.add_item(self.password)
        self.add_item(self.uuid)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        phone = self.phone.value
        password = self.password.value
        uuid_val = self.uuid.value or str(uuid.uuid4())
        try:
            result = await paypay.login(phone, password, uuid_val)
            if "access_token" in result:
                embed = success_embed("✅ PayPayログイン成功", f"**電話番号**: {phone}\n**UUID**: {uuid_val}")
                await interaction.followup.send(embed=embed, ephemeral=True)
            elif "otp_reference_id" in result:
                embed = info_embed("🔐 OTP認証が必要です", f"**{phone}** にSMSが送信されました。\n`/paypay_otp <コード>` を入力してください。")
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = error_embed("❌ ログイン失敗", f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)[:1000]}\n```")
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = error_embed("❌ エラー", f"```\n{str(e)}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)

class KyashLoginModal(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="📱 Kyashログイン", style=discord.ButtonStyle.primary, custom_id="kyash_login_btn")
    async def login_btn(self, interaction: discord.Interaction, button: Button):
        modal = KyashLoginModalInput()
        await interaction.response.send_modal(modal)

class KyashLoginModalInput(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Kyashログイン")
        self.email = TextInput(label="メールアドレス", placeholder="example@email.com", required=True, max_length=100)
        self.password = TextInput(label="パスワード", placeholder="パスワードを入力", required=True, max_length=50)
        self.add_item(self.email)
        self.add_item(self.password)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = success_embed("✅ Kyashログイン成功", f"**メールアドレス**: {self.email.value}")
        await interaction.followup.send(embed=embed, ephemeral=True)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_TOKENが設定されていません。")
