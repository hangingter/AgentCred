#!/usr/bin/env python3
"""
最小 Demo 2: 双方如何利用 Agent-Score 协议进行可信交易

这个脚本展示了两个 Agent 之间的完整交易流程：
1. 买卖双方各自声明身份 (Agent Card)
2. 买方设置交易策略 (信用要求)
3. 握手：买方验证卖方信用
4. 交易：执行任务并返回结果
5. 存证：生成双签 IPR 记录
6. 结算：更新双方信用分

运行方式:
    cd /Users/bytedance/code/agent-score
    PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:minimal-demo python3 minimal-demo/2_trade_with_protocol.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from agent_score_engine import (
    CreditInput,
    DeviceProfile,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    generate_es256k_private_key_pem,
    public_key_pem_from_private_key,
    sign_credit_vc,
    sign_credit_vc_jws,
)
from agent_score_middleware import (
    AgentCard,
    AgentPolicy,
    InteractionProofRecordEnvelope,
    sha256_json,
    sign_payload,
    verify_agent_card_credit,
)


AUTHORITY_ISSUER = "did:ethr:0x2105:0x000000000000000000000000000000000000CAFE"
AUTHORITY_SECRET = "credit-authority-secret"

DEVICE_AUTHORITY_ISSUER = "did:web:device-authority.example.com"
DEVICE_AUTHORITY_PRIVATE_KEY = generate_es256k_private_key_pem()
DEVICE_AUTHORITY_PUBLIC_KEY = public_key_pem_from_private_key(DEVICE_AUTHORITY_PRIVATE_KEY)


class SimpleAgent:
    """一个最简单的 Agent 实现，用于演示协议流程"""

    def __init__(
        self,
        name: str,
        did: str,
        principal: str,
        skills: list[str],
        credit_input: CreditInput,
        agent_secret: str,
        device_country: str = "SG",
        device_asn: int = 12345,
    ) -> None:
        self.name = name
        self.did = did
        self.principal = principal
        self.skills = skills
        self.credit_input = credit_input
        self.agent_secret = agent_secret
        self.device_country = device_country
        self.device_asn = device_asn

    def current_score(self):
        return calculate_credit_score(self.credit_input)

    def get_agent_card(self) -> AgentCard:
        """生成 Agent Card (对外名片)"""
        result = self.current_score()
        vc_payload = build_credit_vc(
            result,
            issuer=AUTHORITY_ISSUER,
            issued_at=datetime.now(timezone.utc),
            snapshot_root=sha256_json({"agent": self.did, "score": result.score}),
            violation_count_90d=0,
        )
        signed_vc = sign_credit_vc(
            vc_payload,
            issuer=AUTHORITY_ISSUER,
            secret=AUTHORITY_SECRET,
            proof_created=datetime.now(timezone.utc),
        )

        device_binding_vc = self._build_device_binding_vc()
        network_fingerprint = {
            "country_code": self.device_country,
            "asn": self.device_asn,
            "ip_prefix": "203.0.113.0/24",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        return AgentCard(
            name=self.name,
            version="1.0.0",
            endpoint=f"https://{self.name}.example.com/a2a",
            skills=self.skills,
            did=self.did,
            principal=self.principal,
            credit_vc=signed_vc,
            device_binding_vc=device_binding_vc,
            network_fingerprint=network_fingerprint,
        )

    def _build_device_binding_vc(self) -> dict:
        """生成设备绑定 VC (24 小时有效期)"""
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        binding_level = self.credit_input.device.binding_level
        payload = {
            "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
            "type": ["VerifiableCredential", "AgentDeviceBindingCredential"],
            "issuer": DEVICE_AUTHORITY_ISSUER,
            "issuanceDate": now.isoformat().replace("+00:00", "Z"),
            "expirationDate": (now + timedelta(days=30)).isoformat().replace("+00:00", "Z"),
            "credentialSubject": {
                "id": self.did,
                "principal": self.principal,
                "binding_level": binding_level,
                "registered_country_code": self.device_country,
                "registered_asn": self.device_asn,
                "device_attestation": {
                    "attestation_type": "tee_sgx_ecdsa_qe3",
                    "device_pubkey_hash": "0xabc123def456",
                    "agent_did": self.did,
                    "timestamp": int(now.timestamp()),
                    "quote": "base64-encoded-tee-quote",
                    "signature": "base64-encoded-device-signature",
                },
            },
        }
        return sign_credit_vc_jws(
            payload,
            issuer=DEVICE_AUTHORITY_ISSUER,
            private_key_pem=DEVICE_AUTHORITY_PRIVATE_KEY,
        )

    def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理业务任务"""
        prompt = task.get("prompt", "")
        return {
            "task_id": task["task_id"],
            "provider": self.did,
            "status": "completed",
            "answer": f"[{self.name}] 已完成任务: {prompt}",
            "price": "10.00 USDC",
        }

    def build_ipr(
        self,
        caller: "SimpleAgent",
        task: Dict[str, Any],
        result: Dict[str, Any],
        success: bool = True,
        on_time: bool = True,
    ) -> InteractionProofRecordEnvelope:
        """生成双签 IPR (交互证明记录)"""
        result_hash = sha256_json(result)
        unsigned = {
            "caller_did": caller.did,
            "callee_did": self.did,
            "task_id": task["task_id"],
            "success": success,
            "on_time": on_time,
            "result_hash": result_hash,
        }
        return InteractionProofRecordEnvelope(
            caller_did=caller.did,
            callee_did=self.did,
            task_id=task["task_id"],
            success=success,
            on_time=on_time,
            result_hash=result_hash,
            caller_signature=sign_payload(unsigned, caller.agent_secret),
            callee_signature=sign_payload(unsigned, self.agent_secret),
        )

    def append_ipr(self, ipr: InteractionProofRecordEnvelope) -> None:
        """将 IPR 加入信用历史，用于后续评分更新"""
        self.credit_input.interactions.append(
            InteractionProofRecord(
                client_id=ipr.caller_did,
                success=ipr.success,
                on_time=ipr.on_time,
                caller_signed=bool(ipr.caller_signature),
                callee_signed=bool(ipr.callee_signature),
            )
        )


def build_buyer_agent() -> SimpleAgent:
    """创建买方 Agent (调用方)"""
    return SimpleAgent(
        name="buyer-agent",
        did="did:ethr:0x2105:0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        principal="did:web:buyer-company.com",
        skills=["trade.request", "payment.send"],
        credit_input=CreditInput(
            agent_id="buyer-did",
            interactions=[
                InteractionProofRecord(client_id=f"seller-{i}", success=True, on_time=True)
                for i in range(8)
            ],
            stakes=[StakeSnapshot(asset="USDC", usd_value=3000)],
            validations=[ValidationAttestation(validator_id="tee-lab", validation_type="tee")],
            principal=PrincipalProfile(score=750),
            device=DeviceProfile(binding_level="runtime"),
        ),
        agent_secret="buyer-secret-key",
    )


def build_seller_agent() -> SimpleAgent:
    """创建卖方 Agent (服务提供方)"""
    return SimpleAgent(
        name="seller-agent",
        did="did:ethr:0x2105:0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        principal="did:web:seller-company.com",
        skills=["trade.execute", "risk.evaluate", "data.analyze"],
        credit_input=CreditInput(
            agent_id="seller-did",
            interactions=[
                InteractionProofRecord(client_id=f"client-{i}", success=True, on_time=True)
                for i in range(15)
            ],
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=8000, lock_days_remaining=180),
                StakeSnapshot(asset="ETH", usd_value=4000, lock_days_remaining=90),
            ],
            validations=[
                ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
                ValidationAttestation(validator_id="zkml-lab", validation_type="zkml"),
            ],
            principal=PrincipalProfile(score=820),
            device=DeviceProfile(binding_level="strong"),
        ),
        agent_secret="seller-secret-key",
    )


def run_trade_demo() -> None:
    print("=" * 70)
    print("🤝 Agent-Score 协议交易演示")
    print("=" * 70)

    buyer = build_buyer_agent()
    seller = build_seller_agent()

    print("\n" + "=" * 70)
    print("Step 1: 买卖双方初始化并声明身份")
    print("=" * 70)

    buyer_score = buyer.current_score()
    seller_score = seller.current_score()

    print(f"\n【买方】 {buyer.name}")
    print(f"  DID:      {buyer.did}")
    print(f"  信用分:   {buyer_score.score} ({buyer_score.tier})")
    print(f"  技能:     {buyer.skills}")

    print(f"\n【卖方】 {seller.name}")
    print(f"  DID:      {seller.did}")
    print(f"  信用分:   {seller_score.score} ({seller_score.tier})")
    print(f"  技能:     {seller.skills}")

    seller_card = seller.get_agent_card()
    print(f"\n✅ 卖方已发布 Agent Card")
    print(f"   CreditVC 签发方: {seller_card.credit_vc['issuer']}")
    print(f"   CreditVC 有效期: {seller_card.credit_vc['validFrom'][:10]} → {seller_card.credit_vc['validUntil'][:10]}")

    print("\n" + "=" * 70)
    print("Step 2: 买方设置交易策略 (信任门槛)")
    print("=" * 70)

    buyer_policy = AgentPolicy(
        min_credit_score=600,
        min_tier="B",
        max_violation_90d=2,
        trusted_issuers={AUTHORITY_ISSUER},
        require_device_binding=True,
        min_binding_level="registration",
        trusted_device_authorities={DEVICE_AUTHORITY_ISSUER},
        allowed_countries={"SG", "US", "CN"},
    )

    print(f"\n【买方策略】")
    print(f"  最低信用分:     {buyer_policy.min_credit_score}")
    print(f"  最低等级:       {buyer_policy.min_tier}")
    print(f"  设备绑定:       要求 ≥ {buyer_policy.min_binding_level}")
    print(f"  信任签发方:     {list(buyer_policy.trusted_issuers)}")
    print(f"  信任设备机构:   {list(buyer_policy.trusted_device_authorities)}")
    print(f"  允许国家:       {list(buyer_policy.allowed_countries)}")

    print("\n" + "=" * 70)
    print("Step 3: 握手 - 买方验证卖方信用")
    print("=" * 70)

    print("\n🔍 买方正在验证卖方的 Agent Card...")
    handshake = verify_agent_card_credit(
        seller_card,
        buyer_policy,
        secret_by_issuer={AUTHORITY_ISSUER: AUTHORITY_SECRET},
        public_key_by_device_authority={DEVICE_AUTHORITY_ISSUER: DEVICE_AUTHORITY_PUBLIC_KEY},
    )

    print(f"\n【握手结果】")
    print(f"  通过:     {handshake.accepted}")
    print(f"  原因:     {handshake.reason}")
    print(f"  卖方分数: {handshake.score}")
    print(f"  卖方等级: {handshake.tier}")

    if not handshake.accepted:
        print(f"\n❌ 握手失败，交易终止！原因: {handshake.reason}")
        return

    print("\n✅ 握手成功！卖方信用符合买方要求，可以进行交易")

    print("\n" + "=" * 70)
    print("Step 4: 交易 - 执行任务")
    print("=" * 70)

    task = {
        "task_id": "trade-2026-0528-001",
        "prompt": "分析 BTC 近期风险并给出交易建议",
        "amount": "10.00 USDC",
    }

    print(f"\n【任务】")
    print(f"  ID:     {task['task_id']}")
    print(f"  内容:   {task['prompt']}")
    print(f"  金额:   {task['amount']}")

    print(f"\n📤 买方发送任务给卖方...")
    result = seller.handle_task(task)
    print(f"📥 卖方返回结果:")
    print(f"  状态:   {result['status']}")
    print(f"  结果:   {result['answer']}")
    print(f"  费用:   {result['price']}")

    print("\n" + "=" * 70)
    print("Step 5: 存证 - 生成双签 IPR 记录")
    print("=" * 70)

    print("\n✍️  买卖双方对交易结果进行双重签名...")
    ipr = seller.build_ipr(buyer, task, result)

    print(f"\n【IPR 记录】")
    print(f"  交易哈希: {ipr.ipr_hash}")
    print(f"  买方签名: {ipr.caller_signature[:40]}...")
    print(f"  卖方签名: {ipr.callee_signature[:40]}...")
    print(f"  成功:     {ipr.success}")
    print(f"  准时:     {ipr.on_time}")

    print("\n📝 IPR 哈希将锚定到链上 ReputationRegistry")
    print("   任何人都可以验证这笔交易的真实性")

    print("\n" + "=" * 70)
    print("Step 6: 结算 - 更新双方信用分")
    print("=" * 70)

    buyer_before = buyer.current_score()
    seller_before = seller.current_score()

    buyer.append_ipr(ipr)
    seller.append_ipr(ipr)

    buyer_after = buyer.current_score()
    seller_after = seller.current_score()

    print(f"\n【买方信用变化】")
    print(f"  交易前: {buyer_before.score} ({buyer_before.tier})")
    print(f"  交易后: {buyer_after.score} ({buyer_after.tier})")
    print(f"  变化:   {buyer_after.score - buyer_before.score:+d} 分")

    print(f"\n【卖方信用变化】")
    print(f"  交易前: {seller_before.score} ({seller_before.tier})")
    print(f"  交易后: {seller_after.score} ({seller_after.tier})")
    print(f"  变化:   {seller_after.score - seller_before.score:+d} 分")

    print("\n" + "=" * 70)
    print("✅ 交易完成！")
    print("=" * 70)
    print("""
📊 交易总结:
  1. 身份可信: 双方都有 DID 身份和 Principal 关联
  2. 信用可验: 通过 CreditVC 验证对方信用等级
  3. 设备绑定: 防止密钥盗用，确保 Agent 在授权设备运行
  4. 交易可溯: IPR 双签记录，链上锚定，不可抵赖
  5. 信用激励: 成功交易提升双方信用分，形成正向循环

🔒 安全保障:
  - JWS 签名防止 CreditVC 篡改
  - alg=ES256K + kid 校验防止算法降级
  - 双签 IPR 防止单方抵赖
  - 设备绑定 + 网络漂移检测防止密钥盗用
""")


if __name__ == "__main__":
    run_trade_demo()
