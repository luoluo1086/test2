import os
import json
from graph_manage import GraphManager

def json_to_graph(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    gm = GraphManager(data)
    gm.add_regulation_node()
    gm.add_terminology_node()
    gm.add_requirement_node()


if __name__ == '__main__':
    path = "example.json"
    json_to_graph(path)