"""
Palantir (パランティア) Foundry SDK - Ontology 動作確認スクリプト

foundry-platform-sdk (foundry_sdk) のオントロジー関連機能の
インポート・モデル定義・クライアント初期化を検証します。
実際のFoundryインスタンスへの接続は不要です。
"""

import sys

PASS = "PASS"
FAIL = "FAIL"
results = []


def assert_true(val, msg="Expected truthy value"):
    assert val, msg


def check(label, fn):
    try:
        fn()
        results.append((PASS, label))
        print(f"  [{PASS}] {label}")
    except Exception as e:
        results.append((FAIL, label))
        print(f"  [{FAIL}] {label}")
        print(f"         {type(e).__name__}: {e}")


# ─────────────────────────────────────────────
# 1. SDK インポート確認
# ─────────────────────────────────────────────
print("\n=== 1. SDK インポート確認 ===")

import foundry_sdk
import foundry_sdk.v2.ontologies.models as ont_models
from foundry_sdk import FoundryClient, UserTokenAuth
from foundry_sdk.v2.ontologies._client import OntologiesClient
from foundry_sdk.v2.ontologies.ontology import OntologyClient
from foundry_sdk.v2.ontologies.object_type import ObjectTypeClient
from foundry_sdk.v2.ontologies.ontology_object import OntologyObjectClient

check("foundry_sdk バージョン確認", lambda: print(f"         version = {foundry_sdk.__version__}"))
check("FoundryClient クラスのインポート", lambda: assert_true(FoundryClient is not None))
check("UserTokenAuth クラスのインポート", lambda: assert_true(UserTokenAuth is not None))
check("OntologiesClient クラスのインポート", lambda: assert_true(OntologiesClient is not None))
check("OntologyClient クラスのインポート", lambda: assert_true(OntologyClient is not None))
check("ObjectTypeClient クラスのインポート", lambda: assert_true(ObjectTypeClient is not None))
check("OntologyObjectClient クラスのインポート", lambda: assert_true(OntologyObjectClient is not None))

# ─────────────────────────────────────────────
# 2. オントロジーモデル定義確認
# ─────────────────────────────────────────────
print("\n=== 2. オントロジーモデル定義確認 ===")

KEY_MODELS = [
    "OntologyV2",
    "OntologyFullMetadata",
    "OntologyObjectV2",
    "OntologyObjectType",
    "OntologyRid",
    "OntologyApiName",
    "OntologyIdentifier",
    "OntologyDataType",
    "OntologyArrayType",
    "OntologyStructType",
    "OntologyStructField",
    "OntologySetType",
    "OntologyMapType",
    "ListOntologiesV2Response",
    "ActionTypeFullMetadata",
    "ActionTypeV2",
    "ActionParameterV2",
    "ActionResults",
]

for model_name in KEY_MODELS:
    check(
        f"モデル {model_name} が存在する",
        lambda mn=model_name: assert_true(hasattr(ont_models, mn)),
    )

# ─────────────────────────────────────────────
# 3. OntologyV2 モデルのフィールド確認
# ─────────────────────────────────────────────
print("\n=== 3. OntologyV2 モデルのフィールド確認 ===")

OntologyV2 = ont_models.OntologyV2


def check_ontologyv2_fields():
    fields = OntologyV2.model_fields
    # v2 SDK uses snake_case field names
    required = {"rid", "api_name", "display_name", "description"}
    missing = required - set(fields.keys())
    assert not missing, f"Missing fields: {missing}"
    print(f"         フィールド: {list(fields.keys())}")


check("OntologyV2 が必須フィールドを持つ", check_ontologyv2_fields)


def check_ontologyv2_instance():
    obj = OntologyV2(
        rid="ri.ontology.main.ontology.00000000-0000-0000-0000-000000000001",
        api_name="MyCompanyOntology",
        display_name="社内オントロジー",
        description="社内情報検索アプリ用オントロジー",
    )
    assert obj.rid == "ri.ontology.main.ontology.00000000-0000-0000-0000-000000000001"
    assert obj.api_name == "MyCompanyOntology"
    assert obj.display_name == "社内オントロジー"
    print(f"         rid={obj.rid!r}, api_name={obj.api_name!r}, display_name={obj.display_name!r}")


check("OntologyV2 インスタンスを生成できる", check_ontologyv2_instance)

# ─────────────────────────────────────────────
# 4. OntologyObjectV2 型の確認
# ─────────────────────────────────────────────
print("\n=== 4. OntologyObjectV2 型の確認 ===")

import typing

OntologyObjectV2 = ont_models.OntologyObjectV2


def check_ontology_object_type():
    # OntologyObjectV2 is a type alias for Dict[str, Any]
    assert OntologyObjectV2 is not None
    # Verify it's a dict-like type
    origin = getattr(OntologyObjectV2, "__origin__", None)
    assert origin is dict, f"Expected dict origin, got {origin}"
    print(f"         OntologyObjectV2 = {OntologyObjectV2} (Dict[str, Any]型エイリアス)")


check("OntologyObjectV2 が Dict[str, Any] 型エイリアスである", check_ontology_object_type)


def check_ontology_object_usage():
    # As a dict, we can create sample ontology objects
    employee: ont_models.OntologyObjectV2 = {
        "employeeId": "EMP001",
        "name": "山田 太郎",
        "department": "エンジニアリング",
        "role": "シニアエンジニア",
    }
    customer: ont_models.OntologyObjectV2 = {
        "customerId": "CUST001",
        "companyName": "株式会社サンプル",
        "contractType": "プレミアム",
    }
    assert employee["employeeId"] == "EMP001"
    assert customer["companyName"] == "株式会社サンプル"
    print(f"         社員オブジェクト: {employee['name']} ({employee['role']})")
    print(f"         顧客オブジェクト: {customer['companyName']} ({customer['contractType']})")


check("OntologyObjectV2 として社内データを表現できる", check_ontology_object_usage)

# ─────────────────────────────────────────────
# 5. FoundryClient 初期化確認（モック認証）
# ─────────────────────────────────────────────
print("\n=== 5. FoundryClient 初期化確認（モック認証）===")


def check_client_init():
    auth = UserTokenAuth(token="mock-token-for-testing")
    client = FoundryClient(auth=auth, hostname="mock.example.palantirfoundry.com")
    assert client is not None
    print(f"         クライアント生成成功: {type(client).__name__}")


def check_client_ontologies():
    auth = UserTokenAuth(token="mock-token-for-testing")
    client = FoundryClient(auth=auth, hostname="mock.example.palantirfoundry.com")
    ontologies_client = client.ontologies
    assert ontologies_client is not None
    print(f"         client.ontologies: {type(ontologies_client).__name__}")
    # Check sub-clients are accessible
    assert hasattr(ontologies_client, "Ontology")
    assert hasattr(ontologies_client, "OntologyObject")
    assert hasattr(ontologies_client, "OntologyObjectSet")
    assert hasattr(ontologies_client, "Action")
    print(f"         サブクライアント: Ontology, OntologyObject, OntologyObjectSet, Action")


check("UserTokenAuth を生成できる", lambda: UserTokenAuth(token="test-token"))
check("FoundryClient を初期化できる", check_client_init)
check("client.ontologies にアクセスできる", check_client_ontologies)

# ─────────────────────────────────────────────
# 6. ActionTypeV2 モデルの確認
# ─────────────────────────────────────────────
print("\n=== 6. ActionTypeV2 モデルの確認 ===")

ActionTypeV2 = ont_models.ActionTypeV2


def check_action_type_fields():
    fields = ActionTypeV2.model_fields
    required = {"api_name", "rid"}
    missing = required - set(fields.keys())
    assert not missing, f"Missing fields: {missing}"
    print(f"         フィールド: {list(fields.keys())}")


check("ActionTypeV2 が必須フィールドを持つ", check_action_type_fields)

# ─────────────────────────────────────────────
# 7. ListOntologiesV2Response モデルの確認
# ─────────────────────────────────────────────
print("\n=== 7. ListOntologiesV2Response モデルの確認 ===")

ListOntologiesV2Response = ont_models.ListOntologiesV2Response


def check_list_response():
    sample_ontology = OntologyV2(
        rid="ri.ontology.main.ontology.00000000-0000-0000-0000-000000000001",
        api_name="MyCompanyOntology",
        display_name="社内オントロジー",
        description="社内情報検索アプリ用オントロジー",
    )
    resp = ListOntologiesV2Response(data=[sample_ontology])
    assert len(resp.data) == 1
    assert resp.data[0].api_name == "MyCompanyOntology"
    print(f"         レスポンス件数: {len(resp.data)}, api_name: {resp.data[0].api_name!r}")


check("ListOntologiesV2Response にデータをセットできる", check_list_response)

# ─────────────────────────────────────────────
# 8. OntologyObjectType モデルの確認
# ─────────────────────────────────────────────
print("\n=== 8. OntologyObjectType モデルの確認 ===")

OntologyObjectType = ont_models.OntologyObjectType


def check_object_type_fields():
    fields = OntologyObjectType.model_fields
    print(f"         フィールド: {list(fields.keys())}")
    assert len(fields) > 0


check("OntologyObjectType のフィールドを確認", check_object_type_fields)

# ─────────────────────────────────────────────
# 結果サマリー
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
passed = sum(1 for s, _ in results if s == PASS)
failed = sum(1 for s, _ in results if s == FAIL)
print(f"結果: {passed} PASS / {failed} FAIL / {len(results)} 合計")
print("=" * 55)

if failed > 0:
    print("\n失敗したテスト:")
    for status, label in results:
        if status == FAIL:
            print(f"  - {label}")
    sys.exit(1)
else:
    print("\nすべてのオントロジー動作確認が成功しました。")
