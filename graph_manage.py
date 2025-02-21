import os
import json
from py2neo import Graph, Node, Relationship
from utils import same_description
from llm import run_llm

class GraphManager:
    def __init__(self, data):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo"))
        self.graph.delete_all()
        self.data = data
    
    def add_regulation_node(self):
        # 新建一个类为Regulation的实体, name为data中的“编号”, 并返回这个实体
        attr = {}
        attr["name"] = self.data["编号"]
        attr["编号"] = self.data["编号"]
        attr["名称"] = self.data["标题"]
        # 强制or推荐
        prompt = '''
        "对于给出的编号，如果是标准编号，格式是GB xxx，则说明其是强制性标准，如果标准编号格式是GB/T xxx，则说明其是推荐性标准；如果判断其是法规条款，则是强制性法规。
        对于强制性标准或强制性法规，返回“强制”，否则返回“推荐”。
        例如：
        编号：GB/T 2020.12345
        输出：推荐
        编号：GB 2020.12345
        输出：强制

        编号：{text}
        请给出以上编号的输出
        '''
        # res = run_llm(prompt.format(text=self.data["编号"]))
        res = "推荐"
        attr["强制or推荐"] = "强制" if "强制" in res else "推荐"

        regulation_node = Node("Regulation", **attr)
        self.graph.create(regulation_node)
        return regulation_node
    
    def add_terminology_node(self):
        # 新建一个类为Terminology的实体, name为data中的“术语”，并返回这个实体
        for term in self.data["各节内容"]:
            prompt = '''
            判断给出的文本内容是否是对于术语的解释，如果是，则返回。。。。

            '''
            # res = run_llm(prompt.format(text=term))
            attr = {} # TODO 填入属性
            terminology_node = Node("Terminology", **attr)
            self.graph.create(terminology_node)
    
    def add_requirement_node(self):
        # 新建一个类为Requirement的实体, name为data中的“编号”，并返回这个实体
        for term in self.data["各节内容"]:
            prompt = '''
            判断给出的文本内容是否属于一种要求，如果是，则返回。。。。

            '''
            # res = run_llm(prompt.format(text=term))
            attr = {} # TODO 填入属性
            requirement_node = Node("Requirement", **attr)
            self.graph.create(requirement_node)