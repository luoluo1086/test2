import sys
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from utils.config_reader import ConfigReader
from utils.utils import State, display_graph
from utils.tools import save_state
from agents.Testee import Testee
from agents.TaskAgent import TaskAgent
from agents.EvalAgent import EvalAgent
from agents.DataEvalAgent import DataEvalAgent
from agents.MonitorAgent import MonitorAgent
from agents.ReportAgent import ReportAgent
from typing import Dict, Any, Optional
from functools import partial

class NormaBench:
    def __init__(self, config_path):
        self.config = ConfigReader.load_config(config_path)
        self.graph = None

    def analyze(self) -> Dict:
        # 判断self.graph是否为空
        if self.graph is None:
            print("Graph is not initialized. Please call build_graph() first.")
            exit()

        state = State(
            status = "IDLE",
            collected_results={},
            config=self.config,
            active_tasks=[], 
            completed_tasks=[]
        )
        state = self.graph.invoke(state)
        print("============================== end ================================")
        print(state['collected_results'])
        return state['collected_results']

    def build_workflow(self):
        print(self.config)
        
        # 根据test_type选择工作流模式
        test_type = self.config.get("test_type", "Agent")
        
        if test_type == "DataQuality":
            return self._build_data_quality_workflow()
        else:  # 默认Agent模式
            return self._build_agent_workflow()

    def _build_agent_workflow(self):
        """agent评估专用工作流"""
        workflow = StateGraph(State)
        
        # 创建任务器/评估器/测试用例加载器
        tasks_loader = []
        eval_loader = []
        testee_loader = []
        save_tool = []
        for i, task in enumerate(self.config["tasks"]):
            print(f"creating task {i}: {task}")
            task_loader = TaskAgent.create(task["task_type"])
            tasks_loader.append(task_loader)
            eval_loader.append(EvalAgent.create(task["metric"]))
            testee_loader.append(Testee.create(self.config["testee"], None))
            save_tool.append(partial(save_state, task_name=task["task_type"]))
        
        monitor_agent = MonitorAgent()
        report_agent = ReportAgent()
        
        # 添加节点
        workflow.add_node("monitor", monitor_agent.run)
        workflow.add_node("reportor", report_agent.run)
        for i in range(len(tasks_loader)):
            task_name = tasks_loader[i].__name__
            workflow.add_node(f"task_{task_name}", tasks_loader[i].get_next_case)
            workflow.add_node(f"eval_{task_name}", eval_loader[i].evaluate)
            eval_loader[i].set_task_name(task_name)
            workflow.add_node(f"testee_{task_name}", testee_loader[i].run)
            testee_loader[i].set_task_name(task_name)
            workflow.add_node(f"save_{task_name}", save_tool[i])

        # 任务分发节点
        workflow.add_node("dispatch_tasks", lambda state: state)

        # 设置边关系
        workflow.add_edge(START, "monitor")
        workflow.add_edge("reportor", END)
        
        # 设置条件边
        workflow.add_conditional_edges(
            "monitor",
            lambda state: "reportor" if state.status == "COMPLETED" else "dispatch_tasks",
            {
                "reportor": "reportor",
                "dispatch_tasks": "dispatch_tasks"
            }
        )
        # 任务分发节点的边
        for i in range(len(tasks_loader)):
            task_name = tasks_loader[i].__name__
            workflow.add_edge("dispatch_tasks", f"task_{task_name}")
        
        # 修改保存节点逻辑
        for i in range(len(tasks_loader)):
            task_name = tasks_loader[i].__name__
            # 添加条件分支
            workflow.add_conditional_edges(
                f"task_{task_name}",
                lambda state: "continue" if state.task_states[task_name]["remaining"] != 0 else "save",
                {
                    "continue": f"testee_{task_name}",
                    "save": f"save_{task_name}"
                }
            )
            # 其他连接关系
            workflow.add_edge(f"testee_{task_name}", f"eval_{task_name}")
            workflow.add_edge(f"eval_{task_name}", f"task_{task_name}")  # 循环处理下一个case
            workflow.add_edge(f"save_{task_name}", "monitor")

        self.graph = workflow.compile()
        return self.graph

    def _build_data_quality_workflow(self):
        """数据质量评估专用工作流"""
        workflow = StateGraph(State)
        
        # 创建质量评估器
        evaluators = [
            DataEvalAgent.create(eval_cfg["evaluator_type"]) for eval_cfg in self.config["quality_evaluators"]
        ]
        
        # 添加节点
        workflow.add_node("monitor", MonitorAgent().run)
        workflow.add_node("reportor", ReportAgent().run)
        for i, evaluator in enumerate(evaluators):
            workflow.add_node(f"eval_{i}", evaluator.evaluate)
            workflow.add_node(f"save_{i}", save_state)
        
        # 设置边关系
        workflow.add_edge(START, "monitor")
        workflow.add_edge("reportor", END)
        
        # 质量评估并行流程（新增）
        workflow.add_conditional_edges(
            "monitor",
            lambda state: "reportor" if state.final_evaluation else "dispatch_evals",
            {"reportor": "reportor", "dispatch_evals": "dispatch_evals"}
        )
        
        workflow.add_node("dispatch_evals", lambda state: state)
        for i in range(len(evaluators)):
            workflow.add_edge("dispatch_evals", f"eval_{i}")
            workflow.add_edge(f"eval_{i}", f"save_{i}")
            workflow.add_edge(f"save_{i}", "monitor")

        self.graph = workflow.compile()
        return self.graph

    # 显示graph并保存为png
    def display_graph(self):
        display_graph(self.graph)



if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/config.yaml"
    norma_bench = NormaBench(config_path)
    norma_bench.build_workflow()
    #norma_bench.display_graph()
    norma_bench.analyze()