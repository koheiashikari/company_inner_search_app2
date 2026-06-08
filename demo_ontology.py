"""
オントロジー (Ontology) とは何か — 実演デモ
このプロジェクトの実データ（社員・顧客・サービス）を使って説明します。
"""

import csv
import textwrap
from dataclasses import dataclass, field
from typing import Any

# ──────────────────────────────────────────────────────────────
# ユーティリティ
# ──────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{'━' * 60}")
    print(f"  {title}")
    print(f"{'━' * 60}")

def comment(text: str):
    for line in textwrap.wrap(text, width=56):
        print(f"  💬 {line}")

def show(label: str, value: Any):
    print(f"  {label:22s} → {value}")


# ══════════════════════════════════════════════════════════════
#  STEP 1  オントロジーとは「言葉の定義集」
# ══════════════════════════════════════════════════════════════
section("STEP 1 ｜ オントロジーとは何か")

comment(
    "オントロジー (Ontology) とは、世界に存在するモノの種類・"
    "属性・関係を形式的に定義したもの。"
    "「社内に何が存在して、それらがどう繋がっているか」を"
    "コンピュータが理解できる形で表現します。"
)
print()
comment(
    "Palantir Foundry のオントロジーは３つの要素で構成されます:"
)
print("""
  ┌─────────────────────────────────────────────────┐
  │  ① ObjectType  ── モノの「種類」の定義          │
  │     例: 社員, 顧客, サービス, 部署               │
  │                                                  │
  │  ② Property    ── ObjectType が持つ「属性」      │
  │     例: 社員.氏名, 社員.部署, 顧客.会社名        │
  │                                                  │
  │  ③ Link        ── ObjectType 間の「関係」        │
  │     例: 社員 ──[所属]──▶ 部署                    │
  │          社員 ──[担当]──▶ 顧客                   │
  └─────────────────────────────────────────────────┘
""")


# ══════════════════════════════════════════════════════════════
#  STEP 2  ObjectType を定義する
# ══════════════════════════════════════════════════════════════
section("STEP 2 ｜ ObjectType（モノの種類）を定義する")

@dataclass
class PropertyDef:
    name: str
    data_type: str
    description: str

@dataclass
class ObjectTypeDef:
    api_name: str
    display_name: str
    primary_key: str
    properties: list[PropertyDef]

# 社員 ObjectType
employee_type = ObjectTypeDef(
    api_name="Employee",
    display_name="社員",
    primary_key="employee_id",
    properties=[
        PropertyDef("employee_id",  "string",  "社員ID (例: EMP0001)"),
        PropertyDef("name",         "string",  "氏名"),
        PropertyDef("department",   "string",  "所属部署"),
        PropertyDef("role",         "string",  "役職"),
        PropertyDef("skills",       "array",   "スキルセット"),
        PropertyDef("hire_date",    "date",    "入社日"),
        PropertyDef("employee_type","string",  "従業員区分"),
    ],
)

# 顧客 ObjectType
customer_type = ObjectTypeDef(
    api_name="Customer",
    display_name="顧客",
    primary_key="customer_id",
    properties=[
        PropertyDef("customer_id",   "string", "顧客ID"),
        PropertyDef("company_name",  "string", "会社名"),
        PropertyDef("status",        "string", "ステータス (既存/見込み)"),
    ],
)

# 部署 ObjectType
dept_type = ObjectTypeDef(
    api_name="Department",
    display_name="部署",
    primary_key="dept_name",
    properties=[
        PropertyDef("dept_name",  "string", "部署名"),
        PropertyDef("head_count", "integer","人数"),
    ],
)

for ot in [employee_type, customer_type, dept_type]:
    print(f"\n  ObjectType: {ot.display_name} (api_name={ot.api_name!r})")
    print(f"  主キー    : {ot.primary_key}")
    print(f"  プロパティ:")
    for p in ot.properties:
        print(f"    - {p.name:<18} [{p.data_type:<8}]  {p.description}")


# ══════════════════════════════════════════════════════════════
#  STEP 3  実データからオブジェクトを生成する
# ══════════════════════════════════════════════════════════════
section("STEP 3 ｜ 実データ（社員名簿.csv）からオブジェクトを生成")

comment(
    "ObjectType の定義に従って、CSVの各行が"
    "「オブジェクト（実体）」になります。"
)

employees = []
with open("data/社員について/社員名簿.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        employees.append({
            "employee_id":   row["社員ID"],
            "name":          row["氏名（フルネーム）"],
            "department":    row["部署"],
            "role":          row["役職"],
            "skills":        [s.strip() for s in row["スキルセット"].split(",")],
            "hire_date":     row["入社日"],
            "employee_type": row["従業員区分"],
        })

print(f"\n  → {len(employees)} 件のオブジェクトを生成しました\n")
for emp in employees[:4]:
    print(f"  ┌── Employee: {emp['employee_id']}")
    print(f"  │   name          = {emp['name']}")
    print(f"  │   department    = {emp['department']}")
    print(f"  │   role          = {emp['role']}")
    print(f"  │   employee_type = {emp['employee_type']}")
    print(f"  └   skills        = {emp['skills'][:2]} ...")

customers = [
    {"customer_id": "CUST001", "company_name": "グローバルフュージョン株式会社",  "status": "既存"},
    {"customer_id": "CUST002", "company_name": "クリスタルワークス株式会社",      "status": "既存"},
    {"customer_id": "CUST003", "company_name": "バーチャルビジョン合同会社",      "status": "既存"},
    {"customer_id": "CUST004", "company_name": "デジテック・ホライズン株式会社",  "status": "見込み"},
    {"customer_id": "CUST005", "company_name": "フォーカスゲート株式会社",        "status": "見込み"},
]


# ══════════════════════════════════════════════════════════════
#  STEP 4  Link（関係）を定義・表示する
# ══════════════════════════════════════════════════════════════
section("STEP 4 ｜ Link（オブジェクト間の関係）")

comment(
    "単なるデータベースと違い、オントロジーでは"
    "オブジェクト同士の「関係」を明示的に定義します。"
    "これにより「山田さんの担当顧客は？」のような"
    "横断的な問いに答えられます。"
)

# 社員→部署の所属関係
dept_map: dict[str, list] = {}
for emp in employees:
    dept_map.setdefault(emp["department"], []).append(emp["name"])

print("\n  【Link: 社員 ──[所属]──▶ 部署】")
for dept, members in sorted(dept_map.items()):
    print(f"    {dept:<16} ← {', '.join(members)}")

# 社員→顧客の担当関係（サンプル割り当て）
import random
random.seed(42)
assignments: list[dict] = []
sales_employees = [e for e in employees if e["department"] == "営業部"]
for cust in customers:
    assigned = random.choice(sales_employees) if sales_employees else employees[0]
    assignments.append({"employee": assigned["name"], "customer": cust["company_name"], "status": cust["status"]})

print("\n  【Link: 社員 ──[担当]──▶ 顧客】")
for a in assignments:
    tag = "★既存" if a["status"] == "既存" else "  見込"
    print(f"    {a['employee']:<12} → {tag} {a['customer']}")


# ══════════════════════════════════════════════════════════════
#  STEP 5  オントロジーを使った「横断検索」
# ══════════════════════════════════════════════════════════════
section("STEP 5 ｜ オントロジーならではの「横断クエリ」")

comment(
    "オントロジーがあると、バラバラなデータを"
    "繋いで問いに答えられます。"
)

# 問い１: Python スキルを持つ社員は？
print("\n  ◆ クエリ1: Python スキルを持つ社員は？")
python_devs = [e for e in employees if "Python" in e["skills"]]
if python_devs:
    for e in python_devs:
        print(f"    → {e['name']} ({e['department']} / {e['role']})")
else:
    print("    → 該当者なし")

# 問い２: 営業部の担当顧客一覧
print("\n  ◆ クエリ2: 営業部の社員が担当する顧客は？")
sales_names = {e["name"] for e in employees if e["department"] == "営業部"}
for a in assignments:
    if a["employee"] in sales_names:
        print(f"    {a['employee']} → {a['customer']} [{a['status']}]")

# 問い３: 正社員のみ、部署ごとの人数
print("\n  ◆ クエリ3: 正社員を部署ごとにカウント")
from collections import Counter
fulltime_depts = Counter(
    e["department"] for e in employees if e["employee_type"] == "正社員"
)
for dept, cnt in sorted(fulltime_depts.items()):
    print(f"    {dept:<16} {cnt} 名")

# 問い４: 見込み顧客の担当者スキル
print("\n  ◆ クエリ4: 見込み顧客を担当している社員のスキルは？")
prospect_reps = {a["employee"] for a in assignments if a["status"] == "見込み"}
for emp in employees:
    if emp["name"] in prospect_reps:
        print(f"    {emp['name']}: {', '.join(emp['skills'][:3])}")


# ══════════════════════════════════════════════════════════════
#  STEP 6  Action（オントロジー上の操作）
# ══════════════════════════════════════════════════════════════
section("STEP 6 ｜ Action（オントロジー上の操作を定義する）")

comment(
    "Palantir では Action としてオントロジー上の書き込み操作も定義できます。"
    "「担当変更」「顧客ステータス更新」などをオントロジーの文脈で管理します。"
)

@dataclass
class ActionDef:
    api_name: str
    display_name: str
    parameters: list[dict]
    description: str

actions = [
    ActionDef(
        api_name="assign_customer",
        display_name="顧客担当割り当て",
        parameters=[
            {"name": "employee_id", "type": "Employee", "description": "担当社員"},
            {"name": "customer_id", "type": "Customer", "description": "担当顧客"},
        ],
        description="社員に顧客を担当させる",
    ),
    ActionDef(
        api_name="update_customer_status",
        display_name="顧客ステータス更新",
        parameters=[
            {"name": "customer_id", "type": "Customer", "description": "対象顧客"},
            {"name": "new_status",  "type": "string",   "description": "新ステータス"},
        ],
        description="見込み顧客を既存顧客に昇格させるなど",
    ),
]

for act in actions:
    print(f"\n  Action: {act.display_name} (api_name={act.api_name!r})")
    print(f"  説明  : {act.description}")
    print(f"  パラメータ:")
    for p in act.parameters:
        print(f"    - {p['name']:<18} [{p['type']}]  {p['description']}")

# Actionの実行シミュレーション
print("\n  ▶ Action 実行シミュレーション: update_customer_status")
target = customers[3]
old_status = target["status"]
target["status"] = "既存"
print(f"    customer_id = {target['customer_id']}")
print(f"    {target['company_name']}: {old_status!r} → {target['status']!r}")


# ══════════════════════════════════════════════════════════════
#  STEP 7  Palantir foundry_sdk モデルで表現
# ══════════════════════════════════════════════════════════════
section("STEP 7 ｜ Palantir foundry_sdk の実モデルで表現")

comment(
    "ここまでの概念を Palantir foundry_sdk の実際のモデルに対応させます。"
)

from foundry_sdk.v2.ontologies.models import (
    OntologyV2,
    ActionTypeV2,
    ListOntologiesV2Response,
)
from foundry_sdk import FoundryClient, UserTokenAuth

# オントロジー定義
my_ontology = OntologyV2(
    rid="ri.ontology.main.ontology.00000000-0000-0000-0000-000000000001",
    api_name="CompanyInnerSearchOntology",
    display_name="社内情報検索オントロジー",
    description="社員・顧客・サービス・部署の関係を管理するオントロジー",
)

print(f"\n  OntologyV2 インスタンス:")
show("rid",          my_ontology.rid)
show("api_name",     my_ontology.api_name)
show("display_name", my_ontology.display_name)
show("description",  my_ontology.description)

# クライアント（実接続なし）
auth   = UserTokenAuth(token="<your-token-here>")
client = FoundryClient(auth=auth, hostname="<your-foundry-host>.palantirfoundry.com")

print(f"\n  FoundryClient を使ったオントロジー操作 (API形式):")
print(f"    # オントロジー一覧の取得")
print(f"    client.ontologies.Ontology.list()")
print(f"")
print(f"    # オブジェクトタイプの取得")
print(f"    client.ontologies.OntologyObject.list(")
print(f"        ontology={my_ontology.api_name!r},")
print(f"        object_type='Employee',")
print(f"    )")
print(f"")
print(f"    # Action の実行")
print(f"    client.ontologies.Action.apply(")
print(f"        ontology={my_ontology.api_name!r},")
print(f"        action='assign_customer',")
print(f"        parameters={{")
print(f"            'employee_id': 'EMP0001',")
print(f"            'customer_id': 'CUST001',")
print(f"        }},")
print(f"    )")


# ══════════════════════════════════════════════════════════════
#  まとめ
# ══════════════════════════════════════════════════════════════
section("まとめ ｜ オントロジーがもたらす価値")

print("""
  従来のRAG検索（このアプリの現状）:
    ・ドキュメントを断片的に検索
    ・「社員名簿.csv」と「顧客MTG議事録」は繋がっていない

  オントロジーを導入すると:
    ・「山田さんが担当する顧客のMTG議事録を全部見せて」
      → 社員オブジェクト ─[担当]─▶ 顧客オブジェクト ─[議事録]─▶ 文書
      という経路で横断検索できる

    ・データの意味が明確になり、AIが文脈を理解しやすくなる
    ・組織変更や担当変更も Action で一元管理できる
""")
