import copy
import logging
import json
import markdown
from bs4 import BeautifulSoup

def markdown_to_json(markdown_text: str) -> dict:
    """
    将 Markdown 文本解析为结构化 JSON 格式。
    参数:
        markdown_text (str): 原始 Markdown 文本
    返回:
        dict: 包含层级结构的 JSON 对象
    """
    print(f"输入药解析的markdown内容： {markdown_text}")
    try:
        html = markdown.markdown(markdown_text)
        soup = BeautifulSoup(html, 'html.parser')

        output = {"data": []}
        current_h1 = None
        current_h2 = None
        current_h3 = None

        for tag in soup.children:
            if not hasattr(tag, 'name'):
                continue  # 忽略文本节点等

            if tag.name == 'h1':
                current_h1 = {"content": tag.text.strip(), "child": []}
                output["data"].append(current_h1)
                current_h2 = None
                current_h3 = None

            elif tag.name == 'h2':
                current_h2 = {"content": tag.text.strip(), "child": []}
                output["data"].append(current_h2)
                current_h3 = None

            elif tag.name == 'h3':
                if not current_h2:
                    logging.warning("h3 出现在没有 h2 的情况下，自动添加默认 h2")
                    current_h2 = {"content": "Untitled Subsection", "child": []}
                    if current_h1:
                        current_h1["child"].append(current_h2)
                    else:
                        current_h1 = {"content": "Untitled Section", "child": [current_h2]}
                        output["data"].append(current_h1)

                current_h3 = {"content": tag.text.strip(), "child": []}
                current_h2["child"].append(current_h3)

            elif tag.name == 'ul':
                items = [{"content": li.text.strip()} for li in tag.find_all('li')]
                if current_h3:
                    current_h3.setdefault("child", []).extend(items)
                elif current_h2:
                    current_h2.setdefault("child", []).extend(items)
                elif current_h1:
                    current_h1.setdefault("child", []).extend(items)
                else:
                    logging.warning("ul 出现在没有标题的情况下，忽略")
        # Step 4: Output JSON
        print("步骤1: 解析成Json后")
        print(json.dumps(output, indent=2, ensure_ascii=False))
        output = flatten_to_two_levels(data=copy.deepcopy(output["data"]))

    except Exception as e:
        logging.exception("解析 Markdown 失败")
        output = {"error": str(e)}
    if not output:
        output = {"error": f"解析失败:{markdown_text}"}
    return output

def flatten_to_two_levels(data):
    new_data = []

    for section in data:
        new_section = {
            "content": section["content"],
            "child": []
        }

        for child in section.get("child", []):
            # 如果 child 自身有 child（即第三层），进行展开合并
            if "child" in child and child["child"]:
                for grandchild in child["child"]:
                    merged_content = f'{child["content"]}: {grandchild["content"]}'
                    new_section["child"].append({"content": merged_content})
            else:
                new_section["child"].append({"content": child["content"]})

        new_data.append(new_section)

    return {"data": new_data}

def data_to_markdown(data):
    lines = []
    if data:
        # 第一个元素作为标题
        lines.append(f"# {data[0]['content']}")
        # 处理其余元素
        for item in data[1:]:
            lines.append(f"\n## {item['content']}")
            for child in item.get("child", []):
                lines.append(f"### {child['content']}")
    return "\n".join(lines)

if __name__ == '__main__':
    # data = markdown_to_json(md_text)
    # 步骤2，变成2层结构
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    data = [
        {'child': [], 'content': '特斯拉汽车的技术与发展概述'},
        {'child': [{'content': '特斯拉的创立背景与使命'},
                   {'content': '电动汽车产业的变革与特斯拉的引领作用'},
                   {'content': '可持续能源战略与发展愿景'}],
         'content': '特斯拉公司概述'},
        {'child': [{'content': '动力电池的技术突破与能量密度提升'},
                   {'content': '超级充电网络的建设与全球布局'},
                   {'content': '电驱动系统的性能与效率优化'},
                   {'content': '软件与OTA远程升级的独特优势'}],
         'content': '核心技术与创新'},
        {'child': [{'content': '自动驾驶系统（Autopilot/FSD）的演进'},
                   {'content': '人工智能与大数据在自动驾驶中的应用'},
                   {'content': '传感器与芯片硬件平台的发展'},
                   {'content': '自动驾驶安全性与监管挑战'}],
         'content': '自动驾驶与智能化'},
        {'child': [{'content': 'Cybertruck、Roadster 等新车型的研发'},
                   {'content': '4680 电池产业化进展'},
                   {'content': '能源产品（Powerwall、Megapack）的市场拓展'}],
         'content': '产品线与产业布局'},
        {'child': [{'content': '全球工厂（上海、柏林、德州）的扩张与产能提升'},
                   {'content': '供应链管理与原材料战略'},
                   {'content': '全球市场竞争与政策环境'}],
         'content': '全球化与产业生态'},
        {'child': [{'content': '未来在电动化与智能化的持续突破'},
                   {'content': '能源生态系统的一体化发展'},
                   {'content': '在全球碳中和目标中的作用与影响'}],
         'content': '未来展望'}
    ]

    markdown_text = data_to_markdown(data)
    print(markdown_text)

    md_text = """
# 特斯拉汽车的技术与发展概述

## 特斯拉公司概述
- 特斯拉的创立背景与使命
- 电动汽车产业的变革与特斯拉的引领作用
- 可持续能源战略与发展愿景

## 核心技术与创新
- 动力电池的技术突破与能量密度提升
- 超级充电网络的建设与全球布局
- 电驱动系统的性能与效率优化
- 软件与OTA远程升级的独特优势

## 自动驾驶与智能化
- 自动驾驶系统（Autopilot/FSD）的演进
- 人工智能与大数据在自动驾驶中的应用
- 传感器与芯片硬件平台的发展
- 自动驾驶安全性与监管挑战

## 产品线与产业布局
- Cybertruck、Roadster 等新车型的研发
- 4680 电池产业化进展
- 能源产品（Powerwall、Megapack）的市场拓展

## 全球化与产业生态
- 全球工厂（上海、柏林、德州）的扩张与产能提升
- 供应链管理与原材料战略
- 全球市场竞争与政策环境

## 未来展望
- 未来在电动化与智能化的持续突破
- 能源生态系统的一体化发展
- 在全球碳中和目标中的作用与影响
    """
    print(markdown_to_json(markdown_text=md_text))


