#!/usr/bin/env python3
"""
最小 Demo 1: 如何用 Agent-Score 协议声明你的 Agent 身份

这个脚本展示了一个本地 Agent 如何通过协议获得"身份证"：
1. 定义 Agent 基本信息 (DID, Principal, 技能等)
2. 积累信用数据 (历史交互、质押、背书等)
3. 由 Credit Authority 签发 CreditVC
4. 生成 Agent Card (对外声明的名片)

运行方式:
    cd /Users/bytedance/code/agent-score
    PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:minimal-demo python3 minimal-demo/1_declare_agent.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from agent_score_engine import (
    CreditInput,
    DeviceProfile,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    sign_credit_vc,
)
from agent_score_middleware import AgentCard, sha256_json


AUTHORITY_ISSUER = "did:ethr:0x2105:0x000000000000000000000000000000000000CAFE"
AUTHORITY_SECRET = "my-credit-authority-secret-key"


def declare_my_agent() -> None:
    print("=" * 60)
    print("Step 1: 定义你的 Agent 基本身份信息")
    print("=" * 60)

    agent_name = "my-trade-agent"
    agent_did = "did:ethr:0x2105:0x1234567890123456789012345678901234567890"
    agent_principal = "did:web:my-company.com"
    agent_endpoint = "https://my-agent.my-company.com/a2a"
    agent_skills = ["trade.execute", "risk.evaluate"]
    agent_secret = "my-agent-private-key"

    print(f"  名称:     {agent_name}")
    print(f"  DID:      {agent_did}")
    print(f"  主体:     {agent_principal}")
    print(f"  端点:     {agent_endpoint}")
    print(f"  技能:     {agent_skills}")

    print("\n" + "=" * 60)
    print("Step 2: 积累 Agent 信用数据")
    print("=" * 60)

    credit_input = CreditInput(
        agent_id=agent_did,
        interactions=[
            InteractionProofRecord(client_id=f"client-{i}", success=True, on_time=True)
            for i in range(10)
        ],
        stakes=[
            StakeSnapshot(asset="USDC", usd_value=5000, lock_days_remaining=90),
        ],
        validations=[
            ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
        ],
        principal=PrincipalProfile(score=800),
        device=DeviceProfile(binding_level="strong"),
    )

    print(f"  历史交互: {len(credit_input.interactions)} 次成功")
    print(f"  质押资产: ${credit_input.stakes[0].usd_value:,} USDC")
    print(f"  验证类型: {[v.validation_type for v in credit_input.validations]}")
    print(f"  主体信用: {credit_input.principal.score} 分")
    print(f"  设备绑定: {credit_input.device.binding_level}")

    print("\n" + "=" * 60)
    print("Step 3: 计算信用分和等级")
    print("=" * 60)

    score_result = calculate_credit_score(credit_input)
    print(f"  信用分:   {score_result.score} / 1000")
    print(f"  等级:     {score_result.tier} (S/A/B/C/D)")
    print(f"  各维度:   {json.dumps(score_result.dimensions.__dict__, indent=10)}")
    if score_result.reason_codes:
        print(f"  原因码:   {list(score_result.reason_codes)}")

    print("\n" + "=" * 60)
    print("Step 4: 由 Credit Authority 签发 CreditVC")
    print("=" * 60)

    vc_payload = build_credit_vc(
        score_result,
        issuer=AUTHORITY_ISSUER,
        issued_at=datetime.now(timezone.utc),
        snapshot_root=sha256_json({"agent": agent_did, "score": score_result.score}),
        violation_count_90d=0,
    )

    signed_vc = sign_credit_vc(
        vc_payload,
        issuer=AUTHORITY_ISSUER,
        secret=AUTHORITY_SECRET,
        proof_created=datetime.now(timezone.utc),
    )

    print(f"  签发方:   {signed_vc['issuer']}")
    print(f"  有效期:   {signed_vc['validFrom']} → {signed_vc['validUntil']}")
    print(f"  证明类型: {signed_vc['proof']['type']}")
    print(f"  JWS 签名: {signed_vc['proof']['jws'][:50]}...")

    print("\n" + "=" * 60)
    print("Step 5: 生成 Agent Card (对外名片)")
    print("=" * 60)

    agent_card = AgentCard(
        name=agent_name,
        version="1.0.0",
        endpoint=agent_endpoint,
        skills=agent_skills,
        did=agent_did,
        principal=agent_principal,
        credit_vc=signed_vc,
    )

    card_dict = agent_card.to_a2a_dict()
    print(json.dumps(card_dict, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("✅ Agent 身份声明完成！")
    print("=" * 60)
    print("""
现在你可以将这个 Agent Card 发布到：
  1. 你的 Agent 端点的 GET /agent-card 接口
  2. Agent 目录服务 (Agent Directory)
  3. 链上 Identity Registry

其他 Agent 就可以通过这个 Card 验证你的信用，与你进行可信交易。
""")


if __name__ == "__main__":
    declare_my_agent()
