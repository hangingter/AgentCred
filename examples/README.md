# Examples

This directory contains usage examples for the Agent-Score protocol.

## Available Examples

### [Minimal Demo](../demos/minimal/)

Quick start guide for agent declaration and trading. Perfect for understanding the core concepts.

**Run:**
```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/minimal/1_declare_agent.py
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/minimal/2_trade_with_protocol.py
```

### [MVP Demo](../demos/mvp/)

Full protocol simulation with local agents, demonstrating the complete handshake and trading flow.

**Run:**
```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/mvp/demo.py
```

### [HTTP Demo](../demos/http/)

HTTP A2A integration example with FastAPI, showing how to expose Agent endpoints.

**Run:**
```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/http/demo.py
```

## Coming Soon

- Real blockchain integration example with Base Sepolia deployment
- Multi-agent orchestration example with CrewAI/LangGraph
- ZK selective disclosure example for privacy-preserving credit verification
- TypeScript SDK usage examples
- Device binding integration with real TPM/TEE hardware
