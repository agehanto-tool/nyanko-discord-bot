<p align="center">
  <img src="icon.svg" width="150" height="150" alt="にゃんこ代行ボットアイコン">
</p>

<h1 align="center">🐱 にゃんこ大戦争 代行ボット</h1>

<p align="center">
  <strong>Discord スラッシュコマンドで動く にゃんこ大戦争 セーブデータ編集ボット</strong>
</p>

<p align="center">
  <a href="#-特徴">特徴</a> •
  <a href="#-コマンド一覧">コマンド</a> •
  <a href="#-インストール方法">インストール</a> •
  <a href="#-設定方法">設定</a> •
  <a href="#-ライセンス">ライセンス</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Discord.py-2.3.0+-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py">
  <img src="https://img.shields.io/badge/License-GPLv3-red?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/github-bcsfe-blue?style=for-the-badge&logo=github" alt="BCSFE">
　<img src="https://img.shields.io/badge/Discord-Support-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord">
</p>

---

## 📖 概要

**にゃんこ大戦争 代行ボット** は、[BCSFE-Python](https://github.com/fieryhenry/BCSFE-Python) ライブラリを使用して、にゃんこ大戦争のセーブデータをDiscordのスラッシュコマンドで編集できるボットです。

以下のような編集が可能です：
- 全キャラクターの解放
- リソースの追加（ネコカン、XP、NP、チケットなど）
- ステージのクリア
- 施設の強化
- その他多数

> **⚠️ 注意**: このボットは [BCSFE-Python](https://github.com/fieryhenry/BCSFE-Python) を使用しています。元のプロジェクトのライセンスと利用規約を尊重してください。

---

## ✨ 特徴

### 🎮 キャラクター管理
- 全キャラクター解放
- 全キャラクターLvMAX
- 全キャラクター最大形態
- 全キャラクター本能全開放
- エラーキャラ削除

### 📦 リソース管理
- ネコカン（50,000個）
- XP（99,999,999）
- NP（9,999）
- レアチケット（999枚）
- プラチナチケット（29枚）
- レジェンドチケット（29枚）
- リーダーシップ（999個）
- バトルアイテム全種（999個）
- マタタビ全種（998個）
- キャッツアイ全種（999個）
- ネコビタン全種（999個）
- 城素材全種（999個）

### 🗺️ ステージ進行
- メインステージ全クリア + お宝金
- ゾンビステージ全クリア
- 旧レジェンド全クリア
- 真レジェンド全クリア
- 零レジェンド全クリア
- 魔界編全クリア
- イベントステージ全クリア
- にゃんこ塔全クリア
- 全ミッション完了

### ⚙️ その他
- 施設LvMAX
- ガマトトLvMAX
- 全メダル開放
- 敵図鑑全開放
- ゴールド会員化
- 広告非表示
- ユーザーランク報酬全受取

---

## 💻 コマンド一覧

| コマンド | 説明 | 権限 |
|---------|------|------|
| `/にゃんこ代行パネル` | メインの代行パネルを表示 | 全ユーザー |
| `/購入時付与ロール` | 代行実行時に付与するロールを設定 | 管理者 |
| `/実績チャンネル` | 実績を送信するチャンネルを設定 | 管理者 |
| `/クーポン生成` | クーポンを生成 | 管理者 |
| `/クーポン一覧` | 全クーポンを表示 | 管理者 |
| `/クーポン削除` | クーポンを削除 | 管理者 |
| `/paypay_login` | PayPayにログイン | 全ユーザー |
| `/paypay_logout` | PayPayからログアウト | 全ユーザー |
| `/paypay_info` | PayPayアカウント情報を表示 | 全ユーザー |
| `/kyash_login` | Kyashにログイン | 全ユーザー |
| `/kyash_logout` | Kyashからログアウト | 全ユーザー |
| `/kyash_info` | Kyashアカウント情報を表示 | 全ユーザー |
| `/値段変更` | アイテムの価格を変更 | 管理者 |
| `/アイテムキー一覧` | 全アイテムキーを表示 | 管理者 |

---

## 🚀 インストール方法

### 必要なもの
- Python 3.9以上
- pip（Pythonパッケージマネージャー）
- Discord Bot Token（[ここで取得](https://discord.com/developers/applications)）

### 手順1: リポジトリをクローン

```bash
git clone https://github.com/agehanto-tool/nyanko-discord-bot.git
cd nyanko-discord-bot
```
### 手順2: 依存パッケージをインストール
```bash
pip install -r requirements.txt
```
### 手順3: 設定ファイルを編集
`config/config.json` にDiscordのBotトークンを設定：
```bash
{
    "discord_token": "ここにあなたのBotトークンを入れる",
    "prefix": "/",
    "prices": {
        "default": 500,
        "account_clone": 1000,
        "nyanko_daiko": 300
    }
}
```

### 手順4: BOTを起動
```bash
python main.py
```
# 📁 プロジェクト構成
```bash
nyanko-discord-bot/
│
├── main.py                         # メインエントリーポイント
├── utils.py                        # ユーティリティ関数
├── requirements.txt                # Python依存パッケージ
│
├── README.md                       # プロジェクト説明
├── SECURITY.md                     # セキュリティポリシー
├── PRIVACY.md                      # プライバシーポリシー
├── LICENSE                         # GPLv3ライセンス
├── icon.svg                        # ボットアイコン
│
├── api/                            # API関連
│   ├── __init__.py
│   ├── paypay.py                   # PayPay APIラッパー
│   ├── kyash.py                    # Kyash APIラッパー
│   └── server/
│       ├── __init__.py
│       └── bcsfe.py                # BCSFE連携（全機能）
│
├── io/                             # 入出力データ
│   ├── __init__.py
│   ├── input/                      # コマンド処理用（データ保存）
│   │   ├── __init__.py
│   │   ├── paypay_data.json        # PayPayアカウント情報
│   │   ├── kyash_data.json         # Kyashアカウント情報
│   │   ├── user_data.json          # ユーザーデータ
│   │   ├── shop_data.json          # ショップ/サーバー設定
│   │   ├── price_overrides.json    # 価格オーバーライド
│   │   └── order_log.json          # 注文履歴
│   └── uninput/                    # 将来的な拡張用
│       └── __init__.py
│
└── config/                         # 設定ファイル
    ├── __init__.py
    └── config.json                 # Bot設定（トークンなど）
```
### 🔒 ライセンス
このプロジェクトは GNU General Public License v3.0 の下でライセンスされています。詳細は LICENSE ファイルを参照してください。

## 利用規約
このボットを使用する場合、以下に同意したものとみなされます：

このボットが BCSFE-Python を使用していることを明示すること

元のBCSFEプロジェクトへのリンクを表示すること

無料で提供されているものを有料で提供しないこと

GPLv3ライセンスの条項に従うこと

## 🤝 クレジット
BCSFE-Python - セーブデータ編集ライブラリ

discord.py - Discord APIラッパー

すべてのコントリビューターとサポーター

## 📞 サポート
バグ報告: https://discord.com/users/1512652537407340674


<p align="center"> Made with ❤️ by <strong>dev 3h62</strong>
