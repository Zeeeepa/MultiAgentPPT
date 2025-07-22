# 📄 MultiAgentPPT 之 自动生成PPT大纲

本项目基于 FastMCP 与 A2A 多智能体框架，自动生成结构化的演示文稿大纲（如调研报告、技术汇总等），支持流式SSE输出。

---

## 🧪 一、MCP 工具（必须启动MCP工具）

1. 检查配置文件：

   ```bash
   cat mcp_config.json
   ```

2. 启动 SSE 模式的 MCP 服务：

   ```bash
   cd backend/slide_outline
   fastmcp run --transport sse mcpserver/rag_tool.py
   ```

3. 启动主服务程序：

   ```bash
   python main_api.py
   ```

---

## 📤 二、A2A Client 请求后的输出（`a2a_client.py`）

以下为客户端请求日志示例，通过 A2A 接口发送问题并接收自动生成的大纲内容：

````
发送 message 信息:
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "我想调研电动汽车发展"
      }
    ],
    "messageId": "ffc01d8723734a048378ae31da45b277"
  }
}

任务状态更新：
- submitted
- working
- completed ✅

返回的结果大纲如下：

```text
# 电动汽车发展概述
- 电动汽车的定义与分类
- 电动汽车发展历程：早期探索、技术突破、政策推动
- 电动汽车的优势与劣势：环保、节能、经济性 vs 续航、充电、成本

# 电动汽车技术发展
- 电池技术：类型（锂离子、固态电池等）、能量密度、充电速度
- 电机技术：类型、效率、功率密度
- 电控技术：BMS、MCU、VCU
- 充电技术：充电桩类型、标准、无线充电

# 电动汽车市场分析
- 全球及主要国家电动汽车销量与保有量
- 市场格局：主流厂商、份额
- 消费群体画像与购买决策因素
- 市场发展趋势预测

# 电动汽车政策环境
- 各国补贴政策
- 碳排法规与禁售时间表
- 充电基础设施规划
- 行业标准与安全规范

# 面临的挑战与未来机遇
- 续航焦虑与充电便利性
- 成本控制与价格挑战
- 电池回收与环保问题
- 智能化与自动驾驶发展机遇
````
# MCP测试程序
[mcp_test_client.py](mcp_test_client.py)