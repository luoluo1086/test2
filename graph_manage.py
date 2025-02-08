import os
import json
from py2neo import Graph, Node, Relationship
from utils import same_description

class GraphManager:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo"))
        self.graph.delete_all()
        self.doc_id = None
        self.doc_node = None
    
    def add_node(self, label, properties):
        node = Node(label, **properties)
        self.graph.create(node)

    def add_relationship(self, start_node, end_node, relationship_type, properties):
        relationship = Relationship(start_node, relationship_type, end_node, **properties)
        self.graph.create(relationship)
    
    def add_fixed_node(self):
        domain = ["智驾", "座舱", "其他"]
        technicaltier = ["数据", "模型", "应用", "管理", "其他"]
        governance = ["透明", "与人协作", "多样性无歧视", "隐私保护", "鲁棒", "安全", "可追溯"]

        for d in domain:
            property = {"name": d}
            self.add_node("Domain", property)
        
        for t in technicaltier:
            property = {"name": t}
            self.add_node("TechnicalTier", property)

        for g in governance:
            property = {"name": g}
            self.add_node("Governance", property)
    
    def add_doc_info(self, doc_info):
        self.doc_id = doc_info["name"] = doc_info["编号"]
        self.doc_node = doc_node = Node("Document", **doc_info)
        self.graph.create(doc_node)
        domain = doc_info["业务(多选:智驾/座舱/其他)"].split('/')
        for d in domain:
            d = d.strip()
            domain_node = self.graph.nodes.match("Domain", name=d).first()
            if domain_node:
                self.add_relationship(doc_node, domain_node, "业务", {"name": d})
        technicaltier = doc_info["涉及内容(多选: 数据/模型/应用/管理/其他)"].split('/')
        for t in technicaltier:
            t = t.strip()
            technicaltier_node = self.graph.nodes.match("TechnicalTier", name=t).first()
            if technicaltier_node:
                self.add_relationship(doc_node, technicaltier_node, "技术层级", {"name": t})
        governance = doc_info["治理类型(多选: 透明/与人协作/多样性无歧视/隐私保护/鲁棒/安全/可追溯)"].split('/')
        for g in governance:
            g = g.strip()
            governance_node = self.graph.nodes.match("Governance", name=g).first()  
            if governance_node:
                self.add_relationship(doc_node, governance_node, "治理类型", {"name": g})
        print("add doc info success")
    
    def add_requirement_info(self, requirement_info):
        for r in requirement_info:
            desc = r["name"] = r["一句话简述"]
            related_requirement_node = self.find_same_description_node(desc)
            if related_requirement_node:
                # 将desc加入related_requirement_node的描述和原文属性中
                one_sentence = related_requirement_node["一句话描述"]
                one_sentence = json.loads(one_sentence)
                length = len(one_sentence)
                one_sentence[str(length+1)+'_'+self.doc_id] = r["一句话简述"]
                related_requirement_node["一句话描述"] = json.dumps(one_sentence, ensure_ascii=False, indent=4)

                original_text = related_requirement_node["原文"]
                original_text = json.loads(original_text)
                original_text[str(length+1)+'_'+self.doc_id] = r["原文"]
                related_requirement_node["原文"] = json.dumps(original_text, ensure_ascii=False, indent=4)

                # 更新related_requirement_node的节点
                self.graph.push(related_requirement_node)

                # 将related_requirement_node和self.doc_node建立归属于关系，但如果已经建立，则不建立
                if not self.graph.match(nodes=(related_requirement_node, self.doc_node), r_type="归属于").first():
                    self.add_relationship(related_requirement_node, self.doc_node, "归属于", {"name": self.doc_id})
            else:
                del r[None]
                one_sentence = r["一句话简述"]
                r["一句话描述"] = json.dumps({'1_'+self.doc_id: one_sentence}, ensure_ascii=False, indent=4)
                original_text = r["原文"]
                r["原文"] = json.dumps({'1_'+self.doc_id: original_text}, ensure_ascii=False, indent=4)
                requirement_node = Node("Requirement", **r)
                self.graph.create(requirement_node)
                domain = r["业务(多选:智驾/座舱/其他)"].split('/')
                for d in domain:
                    d = d.strip()
                    domain_node = self.graph.nodes.match("Domain", name=d).first()
                    if domain_node:
                        self.add_relationship(requirement_node, domain_node, "业务", {"name": d})
                technicaltier = r["涉及内容(多选: 数据/模型/应用/管理/其他)"].split('/')
                for t in technicaltier:
                    t = t.strip()
                    technicaltier_node = self.graph.nodes.match("TechnicalTier", name=t).first()
                    if technicaltier_node:
                        self.add_relationship(requirement_node, technicaltier_node, "技术层级", {"name": t})
                governance = r["治理类型(多选: 透明/与人协作/多样性无歧视/隐私保护/鲁棒/安全/可追溯)"].split('/')
                for g in governance:
                    g = g.strip()
                    governance_node = self.graph.nodes.match("Governance", name=g).first()  
                    if governance_node:
                        self.add_relationship(requirement_node, governance_node, "治理类型", {"name": g})
                self.add_relationship(requirement_node, self.doc_node, "归属于", {"name": self.doc_id})
        print("add requirement info success")

    def find_same_description_node(self, desc):
        # 遍历所有的Requirement节点
        # 比较每个节点的name属性与desc是否相同
        # 如果相同，则返回该节点，否则返回None
        for node in self.graph.nodes.match("Requirement"):
            if same_description(node["name"], desc):
                return node
        return None
    