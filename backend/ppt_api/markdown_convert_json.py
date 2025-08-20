import copy
import logging
import json
import markdown
from bs4 import BeautifulSoup

md_text = """# Clinical Research and Therapeutic Application Progress of Ivonescimab in Non-Small Cell Lung Cancer (NSCLC)

## Introduction
- Overview of NSCLC epidemiology and therapeutic challenges
- Rationale for targeting PD-1 and VEGF pathways
- Emergence of bispecific antibodies in NSCLC treatment

## Mechanism and Pharmacology of Ivonescimab
- Bispecific architecture: simultaneous inhibition of PD-1 and VEGF-A/VEGFR2
- Cooperative binding effects enhancing efficacy over monotherapies
- Preclinical pharmacokinetics, pharmacodynamics, and safety data
- Fc-silencing mutations and implications for safety profile

## Clinical Development and Efficacy Outcomes
### HARMONi-A and Other Key Trials in EGFR-mutated NSCLC
- Phase 3 trial design: ivonescimab plus chemotherapy vs. chemotherapy in EGFR-mutated patients post-TKI progression
- Significant improvement in progression-free survival (PFS): median 7.1 vs. 4.8 months, HR 0.46
- Objective response rate (ORR) enhancements and subgroup benefits (third-generation TKI resistance, brain metastasis)
- Manageable safety profile (grade ≥3 AEs, immune-mediated, VEGF-associated)

### HARMONi-2: First-line in PD-L1 Positive Advanced NSCLC
- Comparison between ivonescimab and pembrolizumab in untreated PD-L1-positive cases
- Doubling of median PFS with ivonescimab (11.1 vs. 5.8 months; HR 0.51)
- Consistent benefit across PD-L1 expression levels and histologies
- Safety signals: grade 3–4 adverse event rates compared to established agents
"""

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
        {'child': [], 'content': 'CAR-T细胞疗法在实体瘤治疗中的挑战与进展'},
        {'child': [{'content': 'CAR-T细胞的基本原理和发展历程'},
                   {'content': 'CAR-T细胞疗法在血液肿瘤中的成功应用'},
                   {'content': 'CAR-T细胞疗法在实体瘤中的应用现状'}],
         'content': 'CAR-T细胞疗法概述'},
        {'child': [{'content': '实体瘤中抗原异质性和抗原逃逸问题'},
                   {'content': '肿瘤微环境对CAR-T细胞的抑制作用'},
                   {'content': 'CAR-T细胞在实体瘤中的浸润和持久性问题'},
                   {'content': '实体瘤中CAR-T细胞疗法的毒性和安全性问题'}],
         'content': '实体瘤中CAR-T细胞疗法的挑战'},
        {'child': [{'content': '新型CAR结构设计与优化'},
                   {'content': '多靶点CAR-T细胞疗法的研究进展'},
                   {'content': 'CAR-T细胞与其他治疗手段的联合应用'}],
         'content': 'CAR-T细胞疗法在实体瘤中的最新进展'},
        {'child': [{'content': '增强CAR-T细胞的持久性和细胞毒性'},
                   {'content': '克服肿瘤微环境限制的策略'},
                   {'content': '新型合成生物学受体的调控'}],
         'content': '提高CAR-T细胞疗法效果的策略'},
        {'child': [{'content': 'CAR-T细胞疗法在实体瘤中的发展趋势'},
                   {'content': '未来CAR-T细胞疗法面临的机遇与挑战'},
                   {'content': 'CAR-T细胞疗法的临床应用前景'}],
         'content': 'CAR-T细胞疗法的未来展望'}
    ]

    markdown_text = data_to_markdown(data)
    print(markdown_text)

