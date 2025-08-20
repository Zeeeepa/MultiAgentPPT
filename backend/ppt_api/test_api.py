#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/6/5 11:50
# @File  : test_api.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 测试Rabbit MQ的写入

import asyncio
import base64
import os
import urllib
import sys
from uuid import uuid4
import json
import unittest
import random
import string

class A2AClientTestCase(unittest.IsolatedAsyncioTestCase):
    """
    测试 A2A 客户端的功能
    """
    AGENT_URL = "http://localhost:10006"
    if os.environ.get("AGENT_URL"):
        AGENT_URL = os.environ.get("AGENT_URL")

    def test_publish_message(self):
        # type为1表示生成ppt
        data = {
            "message": {
                "functionId": 5538134,
                "linkId": "4a3ec4dc4674499791059b68a6bb70fe",
                "attachment": {
                    "isRestock": 0,
                    "selectType": "system",
                    "type": "1",
                    "language": "japanese",
                    "time": [{"sTimeYear": 0, "eTimeYear": 0}],
                },
                "sessionId": uuid4().hex,
                "userId": 1040598,
                # "prompt": "{\"data\":[{\"child\":[],\"content\":\"CAR-T细胞疗法在实体瘤治疗中的挑战与进展\"},{\"child\":[{\"content\":\"CAR-T细胞的基本原理和发展历程\"},{\"content\":\"CAR-T细胞疗法在血液肿瘤中的成功应用\"},{\"content\":\"CAR-T细胞疗法在实体瘤中的应用现状\"}],\"content\":\"CAR-T细胞疗法概述\"},{\"child\":[{\"content\":\"实体瘤中抗原异质性和抗原逃逸问题\"},{\"content\":\"肿瘤微环境对CAR-T细胞的抑制作用\"},{\"content\":\"CAR-T细胞在实体瘤中的浸润和持久性问题\"},{\"content\":\"实体瘤中CAR-T细胞疗法的毒性和安全性问题\"}],\"content\":\"实体瘤中CAR-T细胞疗法的挑战\"},{\"child\":[{\"content\":\"新型CAR结构设计与优化\"},{\"content\":\"多靶点CAR-T细胞疗法的研究进展\"},{\"content\":\"CAR-T细胞与其他治疗手段的联合应用\"}],\"content\":\"CAR-T细胞疗法在实体瘤中的最新进展\"},{\"child\":[{\"content\":\"增强CAR-T细胞的持久性和细胞毒性\"},{\"content\":\"克服肿瘤微环境限制的策略\"},{\"content\":\"新型合成生物学受体的调控\"}],\"content\":\"提高CAR-T细胞疗法效果的策略\"},{\"child\":[{\"content\":\"CAR-T细胞疗法在实体瘤中的发展趋势\"},{\"content\":\"未来CAR-T细胞疗法面临的机遇与挑战\"},{\"content\":\"CAR-T细胞疗法的临床应用前景\"}],\"content\":\"CAR-T细胞疗法的未来展望\"}]}"
                "prompt": {"data": [{"content": "Clinical Research and Therapeutic Application Progress of Ivonescimab in Non-Small Cell Lung Cancer (NSCLC)", "child": []}, 
                                    {"content": "Introduction", "child": [{"content": "Overview of NSCLC and its clinical burden."}, 
                                                                          {"content": "Introduction to Ivonescimab as a bispecific antibody targeting PD-1 and VEGF-A."}, 
                                                                          {"content": "Rationale for dual-targeting in NSCLC therapy."}]}, 
                                    {"content": "Mechanism of Action and Pharmacological Characteristics", "child": [{"content": "Dual blockade of PD-1/PD-L1 and VEGF/VEGFR2 pathways."}, 
                                                                                                                     {"content": "Cooperative binding and enhanced affinity to PD-1 in the presence of VEGF."}, 
                                                                                                                     {"content": "Pharmacokinetics and pharmacodynamics of Ivonescimab."}]}, 
                                    {"content": "Clinical Trial Progress", "child": [{"content": "Phase I Studies"}, 
                                                                                     {"content": "Phase II Studies"}, 
                                                                                     {"content": "Phase III Studies"}]}, 
                                    {"content": "Phase I Studies", "child": [{"content": "Safety and tolerability in advanced solid tumors, including NSCLC."}, 
                                                                             {"content": "Dose-escalation findings and maximum tolerated dose (MTD)."}, 
                                                                             {"content": "Preliminary efficacy signals in NSCLC and other cancers."}]}, 
                                    {"content": "Phase II Studies", "child": [{"content": "Efficacy in combination with chemotherapy for first-line treatment of advanced NSCLC."}, 
                                                                              {"content": "Objective response rates (ORR) and disease control rates (DCR) in squamous and non-squamous NSCLC."}, 
                                                                              {"content": "Safety profile and common adverse events (e.g., epistaxis, proteinuria)."}]}, 
                                    {"content": "Phase III Studies", "child": [{"content": "HARMONi-A trial: Ivonescimab plus chemotherapy vs. chemotherapy alone in EGFR-mutated NSCLC."}, 
                                                                               {"content": "Progression-free survival (PFS) benefits across subgroups, including brain metastases."}, 
                                                                               {"content": "Safety and tolerability data."}, {"content": "HARMONi-2 trial: Ivonescimab vs. pembrolizumab in PD-L1-positive NSCLC."}, 
                                                                               {"content": "Superior PFS with Ivonescimab."}, {"content": "Comparative safety profiles."}]}, 
                                    {"content": "Therapeutic Applications and Indications", "child": [{"content": "Approved indications in China for EGFR-mutated NSCLC post-TKI therapy."}, 
                                                                                                      {"content": "Potential applications in other solid tumors (e.g., breast cancer, liver cancer)."}, 
                                                                                                      {"content": "Ongoing trials exploring combinations with other therapies (e.g., chemotherapy, TKIs)."}]}, 
                                    {"content": "Comparison with Other Drugs", "child": [{"content": "Efficacy and safety comparison with pembrolizumab in PD-L1-positive NSCLC."}, 
                                                                                         {"content": "Advantages over single-target PD-1 inhibitors (e.g., nivolumab, atezolizumab)."}, 
                                                                                         {"content": "Cost-effectiveness analysis vs. chemotherapy alone in EGFR-mutated NSCLC."}]}, 
                                    {"content": "Future Trends and Challenges", "child": [{"content": "Exploration of alternative dosing regimens and combination therapies."}, 
                                                                                          {"content": "Biomarker development for patient selection (e.g., PD-L1 expression, EGFR status)."}, 
                                                                                          {"content": "Addressing resistance mechanisms and optimizing long-term outcomes."}, 
                                                                                          {"content": "Global expansion of clinical trials and regulatory approvals."}]}]},
                # "prompt": {"data": [{"content": "Clinical Research Progress of Lisaftoclax (APG-2575)", "child": []}, 
                #                     {"content": "Mechanism of Action and Preclinical Studies", "child": [{"content": "Selectively binds to BCL-2 with high affinity (Ki < 0.1 nmol/L)"}, 
                #                                                                                          {"content": "Induces BAX/BAK-dependent, caspase-mediated apoptosis in malignant cells"}, 
                #                                                                                          {"content": "Demonstrates potent antitumor activity in hematologic cancer cell lines, primary patient samples (CLL, MM, WM)"}, 
                #                                                                                          {"content": "Disrupts BCL-2:BIM complexes and compromises mitochondrial membrane potential"}, 
                #                                                                                          {"content": "Combined with agents like rituximab or bendamustine/rituximab enhances antitumor activity in preclinical models"}
                #                                                                                         ]}, 
                #                     {"content": "Early-phase Clinical Trials and Pharmacokinetics", "child": [{"content": "Global phase I studies in relapsed/refractory (R/R) CLL/SLL and other hematologic malignancies"}, 
                #                                                                                               {"content": "Maximum tolerated dose (MTD) not reached up to 1,200 mg/day; recommended phase II dose (RP2D) of 600 mg established"}, 
                #                                                                                               {"content": "Pharmacokinetics: limited plasma residence, rapid clearance, half-life ~4-6 hours, compatible with daily oral administration and rapid ramp-up schedule"}, 
                #                                                                                               {"content": "No evidence of tumor lysis syndrome (TLS) in phase I, differing from venetoclax"}
                #                                                                                              ]}, 
                #                     {"content": "Safety and Tolerability Profile", "child": [{"content": "Most common adverse events: diarrhea, fatigue, nausea, anemia, thrombocytopenia, neutropenia"}, 
                #                                                                              {"content": "Grade ≥3 events: predominantly neutropenia and thrombocytopenia, but rarely led to discontinuation"}, 
                #                                                                              {"content": "Serious adverse events infrequent and mostly not treatment-related"}, 
                #                                                                              {"content": "Well tolerated as monotherapy and in combination regimens, including elderly and high-risk patients"}
                #                                                                             ]}, 
                #                     {"content": "Future Trends and Clinical Development", "child": [{"content": "Ongoing phase 2 and phase 3 trials in AML, CLL, SLL, WM, and solid tumors"}, 
                #                                                                                     {"content": "Focus on overcoming venetoclax resistance, broadening patient populations (elderly, relapsed/refractory, genetically defined subtypes)"}, 
                #                                                                                     {"content": "Optimizing combination strategies based on mechanistic and preclinical synergy data"}, 
                #                                                                                     {"content": "Advancement of more convenient and rapid ramp-up regimens to enhance safety and patient adherence"}, 
                #                                                                                     {"content": "Continued monitoring for differentiation from other BCL-2 inhibitors with respect to TLS, dosing flexibility, and tolerability"}
                #                                                                                    ]}, 
                #                     ]},
                # 带有pmidList
                # "prompt": "{\"data\":[{\"child\":[],\"content\":\"CAR-T细胞疗法在实体瘤治疗中的挑战与进展\"},{\"child\":[{\"content\":\"CAR-T细胞的基本原理和发展历程\"},{\"content\":\"CAR-T细胞疗法在血液肿瘤中的成功应用\"},{\"content\":\"CAR-T细胞疗法在实体瘤中的应用现状\"}],\"content\":\"CAR-T细胞疗法概述\"},{\"child\":[{\"content\":\"实体瘤中抗原异质性和抗原逃逸问题\"},{\"content\":\"肿瘤微环境对CAR-T细胞的抑制作用\"},{\"content\":\"CAR-T细胞在实体瘤中的浸润和持久性问题\"},{\"content\":\"实体瘤中CAR-T细胞疗法的毒性和安全性问题\"}],\"content\":\"实体瘤中CAR-T细胞疗法的挑战\"},{\"child\":[{\"content\":\"新型CAR结构设计与优化\"},{\"content\":\"多靶点CAR-T细胞疗法的研究进展\"},{\"content\":\"CAR-T细胞与其他治疗手段的联合应用\"}],\"content\":\"CAR-T细胞疗法在实体瘤中的最新进展\"},{\"child\":[{\"content\":\"增强CAR-T细胞的持久性和细胞毒性\"},{\"content\":\"克服肿瘤微环境限制的策略\"},{\"content\":\"新型合成生物学受体的调控\"}],\"content\":\"提高CAR-T细胞疗法效果的策略\"},{\"child\":[{\"content\":\"CAR-T细胞疗法在实体瘤中的发展趋势\"},{\"content\":\"未来CAR-T细胞疗法面临的机遇与挑战\"},{\"content\":\"CAR-T细胞疗法的临床应用前景\"}],\"content\":\"CAR-T细胞疗法的未来展望\"}],\"pmidList\":[\"32361713\",\"37824640\",\"37371075\",\"39134804\",\"40233718\"]}"
            },
            "type": 1
        }

        json_data = json.dumps(data, ensure_ascii=False)
        nest_json_data = json.dumps(json_data)
        # 建立与RabbitMQ服务器的连接
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host=RABBITMQ_VIRTUAL_HOST,
                credentials=credentials
            )
        )
        channel = connection.channel()
        # 声明一个队列
        channel.queue_declare(queue=QUEUE_NAME_QUESTION, durable=True)

        # 发送消息
        channel.basic_publish(exchange='',
                              routing_key=QUEUE_NAME_QUESTION,
                              body=nest_json_data)
        print(f"发送一条消息到Rabbit MQ完成: '{data}'")
        # 关闭连接
        connection.close()
async def main():
    test_case = A2AClientTestCase()
    test_case.test_publish_message()

if __name__ == "__main__":
    asyncio.run(main())