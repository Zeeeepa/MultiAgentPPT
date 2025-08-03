#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/7/25 17:12
# @File  : xml_convert_json.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : XML格式转换成json格式，方便ppt下载
import os
import re
import uuid
import requests
import json
import dotenv
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
dotenv.load_dotenv()

logger = logging.getLogger(__name__)

def parse_div(div):
    children = []
    for elem in div:
        if elem.tag == "H3":
            children.append({
                "type": "h3",
                "children": [{"text": elem.text.strip()}]
            })
        elif elem.tag == "P":
            children.append({
                "type": "p",
                "children": [{"text": elem.text.strip()}]
            })
    return {
        "type": "bullet",
        "children": children
    }

# 解析每个 SECTION 页面
def parse_section(section):
    result = {
        "id": str(uuid.uuid4()),
        "content": [],
        "rootImage": None,
        "layoutType": section.attrib.get("layout", "vertical"),
        "alignment": "center"
    }

    # H1 标题
    h1 = section.find("H1")
    if h1 is not None:
        result["content"].append({
            "type": "h1",
            "children": [{"text": h1.text.strip()}]
        })

    # 支持的结构体标签
    structured_tags = ["BULLETS", "COLUMNS", "STAIRCASE", "TIMELINE"]
    for tag in structured_tags:
        node = section.find(tag)
        if node is not None:
            bullets = []
            for div in node.findall("DIV"):
                bullets.append(parse_div(div))
            result["content"].append({
                "type": "bullets",
                "children": bullets
            })

    # 图片
    img = section.find("IMG")
    if img is not None:
        result["rootImage"] = {
            "url": img.attrib.get("src", ""),
            "query": "",
            "background": img.attrib.get("background", "false").lower() == "true",
            "alt": img.attrib.get("alt", "")
        }

    return result


def generate_pptx_file(title, sections, references):
    """
    title： str
    sections： list:[stream,stream] ppt生成的Stream流
    references: list
    """
    front_data = {
        "title": title,
        "sections": sections,
        "references": references
    }
    download_url = os.environ["DOWNLOAD_URL"]
    response = requests.post(f"{download_url}/generate-ppt", json=front_data, timeout=120)  # 增加超时时间
    print(f"Status Code: {response.status_code}")
    response_json = response.json()
    print(f"Response Body: {response_json}")
    assert "ppt_url" in response_json, "PPT URL没有在结果中出现，请检查"
    assert response_json["ppt_url"].endswith(".pptx")
    ppt_url = response_json["ppt_url"]
    return ppt_url

def parse_trunk_data(trunk_list, references, title):
    """

    :param trunks: 大模型生成的结果,列表
    :return:
    """
    # 用于存储每个页码对应的XML内容，键为页码，值为XML字符串
    page_xml_map = {}

    # 用于存储 <PRESENTATION> 和 </PRESENTATION> 这类非页码部分的XML
    overall_start_xml = ""
    overall_end_xml = ""

    # 存储最新的references
    latest_references = []

    # 正则表达式用于从 <SECTION> 标签中提取 page_number 属性
    # pattern = re.compile(r'<SECTION[^>]*page_number=(\d+)[^>]*>')
    # 改进的正则表达式，以匹配 page_number="1" 或 page_number=1 等多种情况
    # 同时确保只匹配 <SECTION ...> 标签中的 page_number
    # [^>]* 匹配除了 > 之外的任何字符，0次或多次
    # page_number=(\d+|"\d+") 匹配 page_number=数字 或 page_number="数字"
    page_number_pattern = re.compile(r'<SECTION[^>]+page_number\s*=\s*["\']?(\d+)["\']?[^>]*>')

    for one in trunk_list:
        # 提取 XML 文本内容
        content_parts = one["text"]["result"]["status"]["message"]["parts"]
        text_content = content_parts[0]["text"]

        # --- 移除 Markdown XML block 分隔符 ---
        start_delimiter = "```xml\n"
        end_delimiter = "```"
        if text_content.startswith(start_delimiter):
            text_content = text_content[len(start_delimiter):]
        if text_content.endswith(end_delimiter):
            text_content = text_content[:-len(end_delimiter)]

        # 移除 XML 注释行，例如 <!-- 第1页开始-->
        text_content = re.sub(r'<!--.*?-->\n?', '', text_content)

        # 更新 references，始终保留最新的
        latest_references = one["text"]["result"]["status"]["message"]["metadata"]["references"]

        # 尝试匹配 page_number
        match = page_number_pattern.search(text_content)

        if match:
            # 如果找到 page_number，则将其作为键存储，值是整个 SECTION 块的 XML
            page_number = int(match.group(1))
            page_xml_map[page_number] = text_content.strip()  # .strip() 移除多余的空白行
        elif text_content.strip() == '<PRESENTATION>':
            overall_start_xml = text_content.strip()
        elif text_content.strip() == '</PRESENTATION>':
            overall_end_xml = text_content.strip()

    # 按照页码顺序拼接最终的 XML 内容
    final_xml_parts = []

    if overall_start_xml:
        final_xml_parts.append(overall_start_xml)

    # 获取所有页码，并进行排序
    sorted_page_numbers = sorted(page_xml_map.keys())

    for page_num in sorted_page_numbers:
        final_xml_parts.append(page_xml_map[page_num])

    if overall_end_xml:
        final_xml_parts.append(overall_end_xml)

    PPT_content = "\n".join(final_xml_parts)  # 使用换行符连接各部分，保持可读性
    try:
        soup = BeautifulSoup(PPT_content, "xml")  # 或 "html.parser" 更宽松
        clean_xml = str(soup)  # 转换为良好结构的 XML 字符串
        parser = ET.XMLParser()
        root = ET.fromstring(clean_xml, parser=parser)
        sections = root.findall("SECTION")
        sections_data = [parse_section(sec) for sec in sections]
    except Exception as e:
        print(f"XML解析错误: {e}")
        logger.error(f"XML解析错误: {e}")
    # 输出 JSON（格式化）
    print(json.dumps(sections_data, ensure_ascii=False, indent=2))
    ppt_url = generate_pptx_file(title=title,sections=sections_data, references=references)
    return ppt_url

def main_test_parse_xml():
    # 解析主结构
    # xml_data, references = generate_ppt_xml()
    xml_data, references = generate_ppt_xml_third()
    title = "Cart-T cell research"
    soup = BeautifulSoup(xml_data, "xml")  # 或 "html.parser" 更宽松
    clean_xml = str(soup)  # 转换为良好结构的 XML 字符串
    parser = ET.XMLParser()
    root = ET.fromstring(clean_xml, parser=parser)
    sections = root.findall("SECTION")
    sections_data = [parse_section(sec) for sec in sections]
    # 输出 JSON（格式化）
    print(json.dumps(sections_data, ensure_ascii=False, indent=2))
    ppt_url = generate_pptx_file(title=title,sections=sections_data, references=references)
    print(f"生成的ppt_url是: {ppt_url}")
    return ppt_url

if __name__ == '__main__':
    main_test_parse_xml()