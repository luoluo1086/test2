from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from io import BytesIO
import networkx as nx
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.channels import LastValue

# 自定义注解逻辑
def merge_dict(state_value: Dict[str, Any], new_value: Dict[str, Any]):
    """合并两个字典，新值覆盖旧值"""
    state_value.update(new_value)
    return state_value

def update_task_states(state_value: Dict[str, int], new_value: Dict[str, int]):
    """更新任务状态，新值覆盖旧值"""
    state_value.update(new_value)
    return state_value

@dataclass
class State:
    # 流程状态，包含“IDLE”、“RUNNING”、“COMPLETED”、“FAILED”、“CANCELLED”
    status: Annotated[str, LastValue] = field(default_factory=str)
    # 使用 add_messages 注解来追加列表元素
    active_tasks: Annotated[list[str], add_messages] = field(default_factory=list)
    completed_tasks: Annotated[list[str], add_messages] = field(default_factory=list)
    # 使用 merge_dict 注解来合并字典
    collected_results: Annotated[Dict[str, Any], merge_dict] = field(default_factory=dict)
    config: Annotated[Dict[str, Any], merge_dict] = field(default_factory=dict)
    # 使用 update_task_states 注解来更新任务状态
    task_states: Annotated[Dict[str, Any], update_task_states] = field(default_factory=dict)
    # current_case: Optional[Dict] = None       # 当前测试用例
    # model_output: Optional[str] = None        # 模型输出结果
    # evaluation_result: Optional[Dict] = None  # 评估结果


def display_graph(graph, show_graph = True):
    try:
        # 假设 graph.get_graph() 返回一个自定义的图形对象
        custom_graph = graph.get_graph()
        
        # 将自定义图形对象转换为 networkx 图形对象
        G = nx.Graph()
        for node in custom_graph.nodes:
            G.add_node(node)
        for edge in custom_graph.edges:
            G.add_edge(edge[0], edge[1])
        
        # 使用 NetworkX 和 matplotlib 绘制图形
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        if show_graph:
            # 将绘制的图形保存为图像数据
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            # 使用 plt.imshow 显示图像
            img = plt.imread(buf)
            plt.imshow(img)
            plt.axis('off')  # 关闭坐标轴
            plt.show()
        # 保存图形为 PNG 格式
        plt.savefig('output.png')

    except Exception as e:
        print(f"Error: {e}")