#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/8/20
# @File  : test_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 测试 FastAPI 接口（特斯拉主题）

import asyncio
import os
import json
import unittest
from uuid import uuid4
import httpx   # 用于异步 HTTP 请求

class FastAPITestCase(unittest.IsolatedAsyncioTestCase):
    """
    测试 FastAPI API
    """
    BASE_URL = "http://localhost:8000"
    if os.environ.get("FASTAPI_URL"):
        BASE_URL = os.environ.get("FASTAPI_URL")

    async def test_generate_ppt(self):
        """
        测试 /ppt 接口（特斯拉PPT）
        """
        url = f"{self.BASE_URL}/ppt"
        payload = {
            "message": {
                "sessionId": uuid4().hex,
                "userId": 20001,
                "prompt": {
                    "data": [
                        {"content": "Tesla 2025: Innovation and Market Outlook", "child": []},
                        {"content": "Introduction", "child": [
                            {"content": "Overview of Tesla's growth in EV market"},
                            {"content": "Vision of sustainable energy and transportation"}
                        ]},
                        {"content": "Technology Innovations", "child": [
                            {"content": "Full Self-Driving (FSD) progress"},
                            {"content": "4680 battery technology and energy density improvements"},
                            {"content": "Tesla Dojo supercomputer for AI training"}
                        ]},
                        {"content": "Global Expansion", "child": [
                            {"content": "Gigafactories in US, China, Germany, Mexico"},
                            {"content": "Production scaling and supply chain optimization"}
                        ]},
                        {"content": "Financial Performance", "child": [
                            {"content": "Revenue growth and profitability trends"},
                            {"content": "Stock performance and market capitalization"}
                        ]},
                        {"content": "Future Outlook", "child": [
                            {"content": "Cybertruck and next-gen Roadster"},
                            {"content": "Expansion into energy storage and solar"},
                            {"content": "Challenges from competition (BYD, traditional OEMs)"}
                        ]}
                    ],
                }
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            print("PPT接口返回结果:", resp.json())
            self.assertEqual(resp.status_code, 200)
            self.assertIn("status", resp.json())

    async def test_generate_outline(self):
        """
        测试 /outline 接口（特斯拉大纲）
        """
        url = f"{self.BASE_URL}/outline"
        payload = {
            "message": {
                "sessionId": uuid4().hex,
                "userId": 20002,
                "prompt": "Tesla's role in accelerating the world's transition to sustainable energy",
                "language": "English"
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            print("Outline接口返回结果:", resp.json())
            self.assertEqual(resp.status_code, 200)
            self.assertIn("status", resp.json())

async def main():
    test_case = FastAPITestCase()
    await test_case.test_generate_ppt()
    await test_case.test_generate_outline()


if __name__ == "__main__":
    asyncio.run(main())
