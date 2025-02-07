# def setup_llm():
#     return ChatOpenAI(
#         openai_api_key=os.environ.get("ARK_API_KEY"),
#         openai_api_base="https://ark.cn-beijing.volces.com/api/v3/",
#         model_name="ep-20250109233000-gjphx",
#         temperature=0.0,
#         top_p=0.7,
#     )
# llm = setup_llm()
读取pdf
分段
每段提取实体
遍历原来实体
如果新实体和原来实体相同，则不创建新节点
如果新实体和原来实体不同，则创建新节点
遍历原来关系
如果新关系和原来关系相同，则不创建新关系
如果新关系和原来关系不同，则创建新关系

import os
import fitz  # PyMuPDF
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from py2neo import Graph, Node, Relationship

# 读取 PDF 文档内容
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text_content = []
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text_content.append(page.get_text())
    return "\n".join(text_content)

# 初始化 ChatOpenAI 模型
llm = ChatOpenAI(
    openai_api_key=os.environ.get("ARK_API_KEY"),
    openai_api_base="https://ark.cn-beijing.volces.com/api/v3/",
    model_name="ep-20250109233000-gjphx",
    temperature=0.0,
    top_p=0.7,
)

# 定义提取实体和关系的提示模板
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "从下面的文本中提取entities和每个实体之间的relation, 并以json可读的格式输出文本:"),
        ("user", "{text}")
    ]
)

# 提取知识
def extract_knowledge(text):
    chain = prompt_template | llm
    response = chain.invoke({"text": text})
    return response.content

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo"))

# 清空数据库（可选，仅在开发阶段使用）
graph.delete_all()

# 将知识存储到 Neo4j
def store_knowledge_to_neo4j(knowledge):
    data = json.loads(knowledge)
    # 创建节点和关系
    for entity in data["entities"]:
        node = Node(entity["type"], name=entity["name"])
        graph.create(node)

    for relationship in data["relationships"]:
        start_node = graph.nodes.match(relationship["start_type"], name=relationship["start_name"]).first()
        end_node = graph.nodes.match(relationship["end_type"], name=relationship["end_name"]).first()
        rel = Relationship(start_node, relationship["relation"], end_node)
        graph.create(rel)

# 主函数
def main(pdf_path):
    print("----------------------------------------------------")
    # 提取 PDF 文档内容
    text_content = extract_text_from_pdf(pdf_path)
    text_content = text_content[:500]
    print("PDF 文档内容提取完成。")
    print(text_content)

    # 提取知识
    print("----------------------------------------------------")
    knowledge = extract_knowledge(text_content)
    print("知识提取完成。")
    print(knowledge)
    print(type(knowledge))

    print("----------------------------------------------------")
    knowledge = """
    {
    "entities": [
        {"type": "Movie", "name": "阿甘正传"},
        {"type": "Actor", "name": "汤姆·汉克斯"},
        {"type": "Actor", "name": "罗宾·怀特"},
        {"type": "Event", "name": "越南战争"},
        {"type": "Event", "name": "水门事件"}
    ],
    "relationships": [
        {"start_type": "Actor", "start_name": "汤姆·汉克斯", "relation": "ACTED_IN", "end_type": "Movie", "end_name": "阿甘正传"},
        {"start_type": "Actor", "start_name": "罗宾·怀特", "relation": "ACTED_IN", "end_type": "Movie", "end_name": "阿甘正传"},
        {"start_type": "Movie", "start_name": "阿甘正传", "relation": "MENTIONS_EVENT", "end_type": "Event", "end_name": "越南战争"},
        {"start_type": "Movie", "start_name": "阿甘正传", "relation": "MENTIONS_EVENT", "end_type": "Event", "end_name": "水门事件"}
    ]
    }
    """
    # 将知识存储到 Neo4j
    store_knowledge_to_neo4j(knowledge)
    print("知识已存储到 Neo4j 数据库中。")

def return_entity_template(entity_type="standard"):
    '''返回空的实体模板，json格式'''
    all_entity = []
    standard = {
        "type": "standard", # entity type
        "name": "", # entity / node name
        "standard_type": "", #e.g., Specification, Recommendation, Guideline
        "version": "", #e.g., R21-11, Version 2.0
        "status": "", #e.g., Draft, Final, Approved
        "abstract": "",# brief description of the standard
        "scope": [], # what the standard covers, e.g. "networking", "security", "hardware", "software", "data", "driving", etc.
        "normative_reference": [], # e.g., ISO/IEC 24908, ISO/IEC 24909, other standards that are referenced and required for compliance
        "informative_reference": [], # e.g., ISO/IEC 24908, ISO/IEC 24909, other standards that are referenced but not required for compliance
        "url": "", # url of the standard in the internet / standard lib
        "effective_date": "", # e.g., 2021-01-01
        "contributors": [], # e.g., ["Huawei", "Baidu"]
        "leading_organization": [], # e.g., ["Automotive Standardization Association"]
    }
    all_entity.append(standard)
    for entity in all_entity:
        if entity["type"] == entity_type:
            return entity
    return None

if __name__ == "__main__":
    pdf_path = "./documents/44464.pdf"  # 替换为您的 PDF 文件路径
    main(pdf_path)

