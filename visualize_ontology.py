"""
オントロジー実行内容の図解スクリプト
demo_ontology.py で実行した内容を5枚の図で可視化します。
"""

import csv
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import networkx as nx
import numpy as np

# ── 日本語フォント設定
plt.rcParams["font.family"] = "IPAPGothic"
plt.rcParams["axes.unicode_minus"] = False

# ── データ読み込み
employees = []
with open("data/社員について/社員名簿.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        employees.append({
            "id":   row["社員ID"],
            "name": row["氏名（フルネーム）"],
            "dept": row["部署"],
            "role": row["役職"],
            "type": row["従業員区分"],
            "skills": [s.strip() for s in row["スキルセット"].split(",")],
        })

customers = [
    {"id": "CUST001", "name": "グローバルフュージョン㈱",   "status": "既存"},
    {"id": "CUST002", "name": "クリスタルワークス㈱",       "status": "既存"},
    {"id": "CUST003", "name": "バーチャルビジョン合同",     "status": "既存"},
    {"id": "CUST004", "name": "デジテック・ホライズン㈱",   "status": "見込み"},
    {"id": "CUST005", "name": "フォーカスゲート㈱",         "status": "見込み"},
]

random.seed(42)
sales_emp = [e for e in employees if e["dept"] == "営業部"]
assignments = [
    {"emp": random.choice(sales_emp)["name"], "cust": c["name"], "status": c["status"]}
    for c in customers
]

# ══════════════════════════════════════════════════════════════
# 図1: オントロジー スキーマ図（ObjectType + Property + Link）
# ══════════════════════════════════════════════════════════════

fig1, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 14); ax.set_ylim(0, 8)
ax.axis("off")
fig1.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#1a1a2e")

def draw_object_box(ax, x, y, title, fields, color, width=3.2, row_h=0.38):
    h = 0.55 + len(fields) * row_h
    # 影
    shadow = FancyBboxPatch((x+0.07, y-h-0.07), width, h,
        boxstyle="round,pad=0.05", linewidth=0,
        facecolor="#00000055", zorder=2)
    ax.add_patch(shadow)
    # 本体
    box = FancyBboxPatch((x, y-h), width, h,
        boxstyle="round,pad=0.05", linewidth=1.5,
        edgecolor=color, facecolor="#16213e", zorder=3)
    ax.add_patch(box)
    # タイトル帯
    title_bar = FancyBboxPatch((x, y-0.5), width, 0.5,
        boxstyle="round,pad=0.05", linewidth=0,
        facecolor=color+"cc", zorder=4)
    ax.add_patch(title_bar)
    ax.text(x + width/2, y - 0.22, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color="white", zorder=5)
    # フィールド行
    for i, (fname, ftype, desc) in enumerate(fields):
        fy = y - 0.7 - i * row_h
        bg = "#0f3460" if i % 2 == 0 else "#16213e"
        bar = FancyBboxPatch((x+0.05, fy - row_h*0.45), width-0.1, row_h*0.9,
            boxstyle="round,pad=0.02", linewidth=0, facecolor=bg, zorder=4)
        ax.add_patch(bar)
        ax.text(x+0.18, fy, fname, ha="left", va="center",
                fontsize=8, color="#e0e0e0", zorder=5)
        ax.text(x+width-0.12, fy, ftype, ha="right", va="center",
                fontsize=7, color=color, zorder=5, style="italic")
    return (x + width/2, y - h/2)  # 中心座標

# 各ObjectTypeを描画
emp_cx, emp_cy = draw_object_box(ax, 0.3, 7.5, "社員 (Employee)", [
    ("employee_id",   "string", "社員ID"),
    ("name",          "string", "氏名"),
    ("department",    "string", "部署"),
    ("role",          "string", "役職"),
    ("employee_type", "string", "従業員区分"),
    ("skills",        "array",  "スキルセット"),
    ("hire_date",     "date",   "入社日"),
], "#4fc3f7")

dept_cx, dept_cy = draw_object_box(ax, 5.2, 7.5, "部署 (Department)", [
    ("dept_name",  "string",  "部署名"),
    ("head_count", "integer", "人数"),
], "#a5d6a7")

cust_cx, cust_cy = draw_object_box(ax, 9.8, 7.5, "顧客 (Customer)", [
    ("customer_id",  "string", "顧客ID"),
    ("company_name", "string", "会社名"),
    ("status",       "string", "既存/見込み"),
], "#ffb74d")

# サービスボックス（小さめ）
svc_cx, svc_cy = draw_object_box(ax, 5.2, 2.3, "サービス (Service)", [
    ("service_id",   "string", "サービスID"),
    ("name",         "string", "サービス名"),
    ("category",     "string", "カテゴリ"),
], "#ce93d8", width=3.2)

def draw_link(ax, x1, y1, x2, y2, label, color="#ffffff", style="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                        connectionstyle="arc3,rad=0.1"),
        zorder=6)
    mx, my = (x1+x2)/2, (y1+y2)/2
    ax.text(mx, my+0.18, label, ha="center", va="bottom",
            fontsize=8.5, color=color, fontweight="bold", zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#1a1a2e",
                      edgecolor=color, linewidth=0.8))

# リンクを描画
draw_link(ax, 1.9, 5.3, 5.2+1.6, 5.8, "所属", "#a5d6a7")
draw_link(ax, 3.5, 4.5, 9.8+1.6, 5.5, "担当", "#ffb74d")
draw_link(ax, 9.8+1.6, 3.8, 5.2+1.6, 2.3, "利用", "#ce93d8")

ax.set_title("図1: オントロジー スキーマ（ObjectType・Property・Link）",
             fontsize=14, color="white", pad=12, fontweight="bold")

fig1.tight_layout()
fig1.savefig("ontology_fig1_schema.png", dpi=130, bbox_inches="tight",
             facecolor="#1a1a2e")
plt.close(fig1)
print("✓ 図1 保存: ontology_fig1_schema.png")


# ══════════════════════════════════════════════════════════════
# 図2: オブジェクトインスタンス グラフ（実データ）
# ══════════════════════════════════════════════════════════════

fig2, ax2 = plt.subplots(figsize=(16, 10))
ax2.axis("off")
fig2.patch.set_facecolor("#0d1117")

G = nx.DiGraph()

# 部署ノード追加
depts = list({e["dept"] for e in employees})
for d in depts:
    G.add_node(d, kind="dept")

# 社員ノード（最初の15人）
shown_emp = employees[:15]
for e in shown_emp:
    G.add_node(e["name"], kind="emp")
    G.add_edge(e["name"], e["dept"], rel="所属")

# 顧客ノード
for c in customers:
    G.add_node(c["name"], kind="cust")

# 担当リンク
for a in assignments:
    if a["emp"] in [e["name"] for e in shown_emp]:
        G.add_edge(a["emp"], a["cust"], rel="担当")

# レイアウト
pos = {}
dept_list = [d for d in depts if d in G.nodes]
for i, d in enumerate(dept_list):
    angle = 2 * np.pi * i / len(dept_list)
    pos[d] = (3.5 * np.cos(angle), 3.5 * np.sin(angle))

emp_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "emp"]
for i, e in enumerate(emp_nodes):
    angle = 2 * np.pi * i / len(emp_nodes)
    pos[e] = (1.6 * np.cos(angle), 1.6 * np.sin(angle))

cust_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "cust"]
for i, c in enumerate(cust_nodes):
    angle = 2 * np.pi * i / len(cust_nodes) + np.pi / 5
    pos[c] = (5.8 * np.cos(angle), 5.8 * np.sin(angle))

# エッジ描画
edge_colors = []
for u, v, d in G.edges(data=True):
    edge_colors.append("#a5d6a7" if d.get("rel") == "所属" else "#ffb74d")

nx.draw_networkx_edges(G, pos, ax=ax2, edge_color=edge_colors,
                       arrows=True, arrowsize=12, width=1.2,
                       arrowstyle="-|>", connectionstyle="arc3,rad=0.05",
                       alpha=0.7)

# ノード描画（種別ごとに色分け）
node_colors = {
    "emp":  "#4fc3f7",
    "dept": "#a5d6a7",
    "cust": "#ffb74d",
}
for kind, color in node_colors.items():
    nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == kind]
    sizes = {"emp": 800, "dept": 1400, "cust": 1100}[kind]
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, ax=ax2,
                           node_color=color, node_size=sizes, alpha=0.9)

# ラベル
label_opts = dict(ax=ax2, font_family="IPAPGothic", font_color="white")
dept_labels = {n: n.replace("部", "\n部") for n in [n for n, d in G.nodes(data=True) if d.get("kind") == "dept"]}
emp_labels  = {n: n for n in [n for n, d in G.nodes(data=True) if d.get("kind") == "emp"]}
cust_labels = {n: n.replace("株式会社", "㈱").replace("合同会社", "合同") for n in cust_nodes}

nx.draw_networkx_labels(G, pos, labels=dept_labels, font_size=8, **label_opts)
nx.draw_networkx_labels(G, pos, labels=emp_labels,  font_size=6.5, **label_opts)
nx.draw_networkx_labels(G, pos, labels=cust_labels, font_size=7.5, **label_opts)

# 凡例
legend_items = [
    mpatches.Patch(color="#4fc3f7", label="社員 (Employee)"),
    mpatches.Patch(color="#a5d6a7", label="部署 (Department)"),
    mpatches.Patch(color="#ffb74d", label="顧客 (Customer)"),
    mpatches.Patch(color="#a5d6a7", label="─── 所属リンク"),
    mpatches.Patch(color="#ffb74d", label="─── 担当リンク"),
]
ax2.legend(handles=legend_items, loc="lower left", fontsize=9,
           facecolor="#161b22", edgecolor="#30363d", labelcolor="white")

ax2.set_title("図2: オブジェクトインスタンス グラフ（実データ・社員15名）",
              fontsize=14, color="white", pad=12, fontweight="bold")
fig2.patch.set_facecolor("#0d1117")
fig2.savefig("ontology_fig2_instances.png", dpi=130, bbox_inches="tight",
             facecolor="#0d1117")
plt.close(fig2)
print("✓ 図2 保存: ontology_fig2_instances.png")


# ══════════════════════════════════════════════════════════════
# 図3: 横断クエリ トレース図（クエリ1〜4）
# ══════════════════════════════════════════════════════════════

fig3, axes = plt.subplots(2, 2, figsize=(16, 10))
fig3.patch.set_facecolor("#0d1117")

QUERIES = [
    {
        "title": "クエリ1: Python スキルを持つ社員",
        "path":  ["ObjectType\n(Employee)", "skills\n(array)", "Python\n含む社員"],
        "arrow_labels": ["プロパティ\nフィルタ", "マッチング"],
        "result": [e["name"] for e in employees if "Python" in e["skills"]][:6],
        "colors": ["#4fc3f7", "#7986cb", "#ef9a9a"],
    },
    {
        "title": "クエリ2: 営業部が担当する顧客",
        "path":  ["部署\n(営業部)", "所属\nLink", "社員\n(営業部員)", "担当\nLink", "顧客"],
        "arrow_labels": ["逆引き", "所属", "担当"],
        "result": [f"{a['emp']} → {a['cust']}" for a in assignments],
        "colors": ["#a5d6a7", "#4fc3f7", "#4fc3f7", "#ffb74d"],
    },
    {
        "title": "クエリ3: 正社員を部署ごとにカウント",
        "path":  ["ObjectType\n(Employee)", "employee_type\n= 正社員", "department\nGroupBy", "集計結果"],
        "arrow_labels": ["フィルタ", "グループ化", "COUNT"],
        "result": [],
        "colors": ["#4fc3f7", "#4fc3f7", "#7986cb", "#ffcc80"],
        "bar_data": True,
    },
    {
        "title": "クエリ4: 見込み顧客を担当する社員のスキル",
        "path":  ["顧客\n(見込み)", "担当\nLink(逆)", "社員", "skills\nプロパティ"],
        "arrow_labels": ["逆トラバース", "取得", "展開"],
        "result": [],
        "colors": ["#ffb74d", "#4fc3f7", "#4fc3f7", "#ce93d8"],
        "skill_data": True,
    },
]

for ax_q, q in zip(axes.flat, QUERIES):
    ax_q.set_facecolor("#161b22")
    ax_q.axis("off")
    ax_q.set_title(q["title"], fontsize=10, color="white",
                   fontweight="bold", pad=6)

    path  = q["path"]
    cols  = q["colors"]
    n     = len(path)
    xs    = np.linspace(0.08, 0.92, n)
    y_box = 0.75

    # ノードボックス
    for i, (label, color) in enumerate(zip(path, cols)):
        box = FancyBboxPatch((xs[i]-0.08, y_box-0.10), 0.16, 0.20,
            boxstyle="round,pad=0.02", linewidth=1.5,
            edgecolor=color, facecolor=color+"33")
        ax_q.add_patch(box)
        ax_q.text(xs[i], y_box, label, ha="center", va="center",
                  fontsize=7.5, color="white", fontweight="bold")

    # 矢印とラベル
    for i, lbl in enumerate(q.get("arrow_labels", [])):
        x1, x2 = xs[i]+0.08, xs[i+1]-0.08
        ax_q.annotate("", xy=(x2, y_box), xytext=(x1, y_box),
            arrowprops=dict(arrowstyle="-|>", color="#ffffff88", lw=1.2),
            zorder=5)
        ax_q.text((x1+x2)/2, y_box+0.08, lbl, ha="center", va="bottom",
                  fontsize=6.5, color="#aaaaaa")

    # 結果表示
    if q.get("bar_data"):
        from collections import Counter
        counts  = Counter(e["dept"] for e in employees if e["type"] == "正社員")
        depts_s = sorted(counts.keys())
        vals    = [counts[d] for d in depts_s]
        short   = [d.replace("部", "") for d in depts_s]
        bar_colors = ["#4fc3f7","#a5d6a7","#ffb74d","#ce93d8","#ef9a9a","#80cbc4"]
        bar_ax  = ax_q.inset_axes([0.05, 0.05, 0.90, 0.50])
        bar_ax.set_facecolor("#161b22")
        xs_bar  = np.arange(len(short))
        bars    = bar_ax.bar(xs_bar, vals, color=bar_colors[:len(short)])
        for bar, v in zip(bars, vals):
            bar_ax.text(bar.get_x()+bar.get_width()/2, v+0.05, str(v),
                        ha="center", va="bottom", color="white", fontsize=8)
        bar_ax.set_xlim(-0.5, len(short)-0.5)
        bar_ax.set_ylim(0, max(vals)+1)
        bar_ax.set_xticks(xs_bar)
        bar_ax.set_xticklabels(short, fontsize=7)
        bar_ax.tick_params(colors="white", labelsize=7)
        for spine in bar_ax.spines.values():
            spine.set_edgecolor("#30363d")
        bar_ax.yaxis.set_tick_params(colors="white")

    elif q.get("skill_data"):
        prospect_reps = {a["emp"] for a in assignments if a["status"] == "見込み"}
        lines = []
        for emp in employees:
            if emp["name"] in prospect_reps:
                lines.append(f"{emp['name']}: {', '.join(emp['skills'][:3])}")
        for i, line in enumerate(lines):
            ax_q.text(0.05, 0.42 - i*0.14, f"• {line}",
                      fontsize=8, color="#e0e0e0",
                      transform=ax_q.transAxes)

    else:
        for i, r in enumerate(q["result"][:6]):
            ax_q.text(0.05, 0.52 - i*0.10, f"• {r}",
                      fontsize=8.5, color="#e0e0e0",
                      transform=ax_q.transAxes)

fig3.suptitle("図3: 横断クエリ トレース（クエリ1〜4 の実行経路）",
              fontsize=13, color="white", fontweight="bold", y=1.01)
fig3.tight_layout(pad=1.5)
fig3.savefig("ontology_fig3_queries.png", dpi=130, bbox_inches="tight",
             facecolor="#0d1117")
plt.close(fig3)
print("✓ 図3 保存: ontology_fig3_queries.png")


# ══════════════════════════════════════════════════════════════
# 図4: Action 実行フロー図
# ══════════════════════════════════════════════════════════════

fig4, ax4 = plt.subplots(figsize=(14, 6))
ax4.set_xlim(0, 14); ax4.set_ylim(0, 6)
ax4.axis("off")
fig4.patch.set_facecolor("#0d1117")
ax4.set_facecolor("#0d1117")

def rounded_box(ax, cx, cy, w, h, label, sublabel="", color="#4fc3f7", fontsize=10):
    box = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.08", linewidth=2,
        edgecolor=color, facecolor=color+"22")
    ax.add_patch(box)
    ax.text(cx, cy + (0.12 if sublabel else 0), label,
            ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold")
    if sublabel:
        ax.text(cx, cy - 0.28, sublabel, ha="center", va="center",
                fontsize=8, color=color)

def flow_arrow(ax, x1, y1, x2, y2, label="", color="white"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                        connectionstyle="arc3,rad=0.0"),
        zorder=5)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2+0.18, label, ha="center",
                fontsize=8, color=color)

# Action: update_customer_status のフロー
steps = [
    (1.2, 3.0, 2.0, 1.2, "呼び出し元\n(アプリ)",      "",                              "#7986cb"),
    (4.0, 3.0, 2.4, 1.2, "Action\nupdate_customer\n_status", "params:\ncustomer_id, new_status", "#ff8a65"),
    (7.2, 3.0, 2.4, 1.2, "バリデーション\n(Pydantic)",  "型チェック・\n権限確認",        "#4fc3f7"),
    (10.4, 3.0, 2.4, 1.2, "オブジェクト\n更新",          "Customer.status\n= '既存'",     "#a5d6a7"),
    (13.2, 3.0, 2.0, 1.2, "完了\n(ActionResults)",      "",                              "#ffcc80"),
]

for cx, cy, w, h, label, sub, color in steps:
    rounded_box(ax4, cx, cy, w, h, label, sub, color)

# 矢印
arrow_labels = ["Action呼出", "検証", "書き込み", "応答"]
xs = [s[0] for s in steps]
for i in range(len(xs)-1):
    x1 = xs[i] + steps[i][2]/2
    x2 = xs[i+1] - steps[i+1][2]/2
    flow_arrow(ax4, x1, 3.0, x2, 3.0, arrow_labels[i], "#aaaaaa")

# Before / After ボックス
ax4.text(10.4, 1.6, "Before → After", ha="center", fontsize=9,
         color="#aaaaaa", style="italic")

before_box = FancyBboxPatch((8.8, 0.3), 1.5, 0.9,
    boxstyle="round,pad=0.05", linewidth=1,
    edgecolor="#ef9a9a", facecolor="#ef9a9a22")
ax4.add_patch(before_box)
ax4.text(9.55, 0.75, "status\n= '見込み'", ha="center", va="center",
         fontsize=8, color="#ef9a9a")

after_box = FancyBboxPatch((10.6, 0.3), 1.5, 0.9,
    boxstyle="round,pad=0.05", linewidth=1,
    edgecolor="#a5d6a7", facecolor="#a5d6a722")
ax4.add_patch(after_box)
ax4.text(11.35, 0.75, "status\n= '既存'", ha="center", va="center",
         fontsize=8, color="#a5d6a7")

ax4.annotate("", xy=(10.58, 0.75), xytext=(10.32, 0.75),
    arrowprops=dict(arrowstyle="-|>", color="white", lw=1.5))

ax4.set_title(
    "図4: Action 実行フロー（update_customer_status: 見込み→既存）",
    fontsize=13, color="white", fontweight="bold", pad=10)

fig4.savefig("ontology_fig4_action.png", dpi=130, bbox_inches="tight",
             facecolor="#0d1117")
plt.close(fig4)
print("✓ 図4 保存: ontology_fig4_action.png")


# ══════════════════════════════════════════════════════════════
# 図5: RAG（現状）vs オントロジー（導入後）の比較図
# ══════════════════════════════════════════════════════════════

fig5, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(16, 8))
fig5.patch.set_facecolor("#0d1117")

for ax_side in (ax_l, ax_r):
    ax_side.set_xlim(0, 7); ax_side.set_ylim(0, 8)
    ax_side.axis("off")
    ax_side.set_facecolor("#0d1117")

# ── 左: 現在の RAG ─────────────────────────────
ax_l.set_title("現状: RAG検索（ドキュメント単位）",
               fontsize=12, color="#ef9a9a", fontweight="bold", pad=8)

docs = [
    (1.0, 6.5, "社員名簿.csv",        "#4fc3f7"),
    (3.5, 6.5, "お客様情報.pdf",      "#ffb74d"),
    (6.0, 6.5, "MTG議事録.docx",      "#a5d6a7"),
    (1.0, 5.0, "会社概要.pdf",        "#ce93d8"),
    (3.5, 5.0, "サービス資料.pdf",    "#ff8a65"),
    (6.0, 5.0, "サービス利用ガイド",  "#80cbc4"),
]
for x, y, name, color in docs:
    box = FancyBboxPatch((x-0.7, y-0.3), 1.4, 0.6,
        boxstyle="round,pad=0.04", linewidth=1,
        edgecolor=color, facecolor=color+"22")
    ax_l.add_patch(box)
    ax_l.text(x, y, name, ha="center", va="center",
              fontsize=7.5, color="white")

# ベクトルDB
vdb = FancyBboxPatch((1.5, 3.2), 4.0, 0.8,
    boxstyle="round,pad=0.05", linewidth=1.5,
    edgecolor="#7986cb", facecolor="#7986cb22")
ax_l.add_patch(vdb)
ax_l.text(3.5, 3.6, "Vector DB (ChromaDB)",
          ha="center", va="center", fontsize=9, color="white")

# ユーザークエリ→VDB
ax_l.text(3.5, 2.4, "「山田さんの担当顧客は？」", ha="center",
          fontsize=9, color="#ffcc80",
          bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffcc8022",
                    edgecolor="#ffcc80"))
ax_l.annotate("", xy=(3.5, 3.18), xytext=(3.5, 2.72),
    arrowprops=dict(arrowstyle="-|>", color="#7986cb", lw=1.5))

# 断片的な結果
ax_l.text(3.5, 1.5, "断片的な文書の切れ端が返る\n（関係性が失われている）",
          ha="center", va="center", fontsize=8.5, color="#ef9a9a",
          bbox=dict(boxstyle="round,pad=0.3", facecolor="#ef9a9a22",
                    edgecolor="#ef9a9a"))
ax_l.annotate("", xy=(3.5, 1.8), xytext=(3.5, 3.18),
    arrowprops=dict(arrowstyle="-|>", color="#ef9a9a", lw=1.5))

# バツ印
ax_l.text(3.5, 0.5, "[NG]  社員↔顧客の関係が追えない",
          ha="center", fontsize=9, color="#ef9a9a")

# ── 右: オントロジー導入後 ──────────────────────
ax_r.set_title("導入後: オントロジー検索（関係ベース）",
               fontsize=12, color="#a5d6a7", fontweight="bold", pad=8)

nodes_r = [
    (3.5, 6.8, "社員\nEMP0001", "#4fc3f7", 900),
    (1.2, 5.5, "部署\n営業部",   "#a5d6a7", 750),
    (5.8, 5.5, "顧客\nCUST003", "#ffb74d", 750),
    (3.5, 4.2, "MTG\n議事録",   "#ce93d8", 700),
    (1.5, 3.0, "スキル\nPython", "#80cbc4", 600),
    (5.5, 3.0, "サービス\nEcoTee", "#ff8a65", 650),
]
G2 = nx.Graph()
for x, y, label, color, _ in nodes_r:
    G2.add_node(label, pos=(x, y), color=color)

edges_r = [
    ("社員\nEMP0001", "部署\n営業部",   "所属"),
    ("社員\nEMP0001", "顧客\nCUST003",  "担当"),
    ("社員\nEMP0001", "MTG\n議事録",    "参加"),
    ("顧客\nCUST003", "MTG\n議事録",    "対象"),
    ("社員\nEMP0001", "スキル\nPython", "保有"),
    ("顧客\nCUST003", "サービス\nEcoTee","契約"),
]
for u, v, rel in edges_r:
    G2.add_edge(u, v, rel=rel)

pos2 = {n: d["pos"] for n, d in G2.nodes(data=True)}
colors2 = [d["color"] for _, d in G2.nodes(data=True)]
sizes2  = [d[4] for d in nodes_r]

nx.draw_networkx_edges(G2, pos2, ax=ax_r, edge_color="#ffffff55", width=1.5, arrows=False)
nx.draw_networkx_nodes(G2, pos2, ax=ax_r, node_color=colors2, node_size=sizes2, alpha=0.9)
nx.draw_networkx_labels(G2, pos2, ax=ax_r, font_color="white", font_size=7, font_family="IPAPGothic")
edge_labels = {(u, v): d["rel"] for u, v, d in G2.edges(data=True)}
nx.draw_networkx_edge_labels(G2, pos2, edge_labels, ax=ax_r,
    font_color="#ffcc80", font_size=7, font_family="IPAPGothic")

# クエリ結果
ax_r.text(3.5, 1.9, "「山田さんの担当顧客は？」", ha="center",
          fontsize=9, color="#ffcc80",
          bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffcc8022",
                    edgecolor="#ffcc80"),
          transform=ax_r.transData)
ax_r.text(3.5, 0.9, "✓  社員→[担当]→顧客 を経路でたどり\n   バーチャルビジョン合同会社 を即座に特定",
          ha="center", fontsize=8.5, color="#a5d6a7",
          bbox=dict(boxstyle="round,pad=0.3", facecolor="#a5d6a722",
                    edgecolor="#a5d6a7"),
          transform=ax_r.transData)

fig5.suptitle("図5: RAG（現状）vs オントロジー（導入後）の検索能力比較",
              fontsize=13, color="white", fontweight="bold")
fig5.tight_layout(pad=1.0)
fig5.savefig("ontology_fig5_comparison.png", dpi=130, bbox_inches="tight",
             facecolor="#0d1117")
plt.close(fig5)
print("✓ 図5 保存: ontology_fig5_comparison.png")

print("\n全5枚の図の生成が完了しました。")
