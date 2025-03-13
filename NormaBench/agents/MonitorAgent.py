from langgraph.graph import END
from utils.utils import State

class MonitorAgent:
    def run(self, state: State):
        print("MonitorAgent running...")
        print(state)
        # 检查是否有活跃任务， 如果没有活跃任务且没有完成任何任务，初始化任务
        if state.status == "IDLE":
            state = self.__initialize_task__(state)
        elif state.status == "RUNNING":
            # 检查是否有任务完成, 并更新active_tasks
            state = self.__update_tasks_state__(state)
            # 判断是否所有任务都已完成
            if len(state.active_tasks) == 0:
                state.status = "COMPLETED"
        print("status: {}".format(state.status))
        print("MonitorAgent ended.")
        return state
    
    def __initialize_task__(self, state: State) -> State:
        # 初始化任务
        print("No active tasks, initializing tasks...")
        for task in state.config["tasks"]:
            state.active_tasks.append(task["task_type"])
            state.task_states[task["task_type"]] = {"remaining":-1}  # -1表示未完成, 0表示所有case已测试完, 数字表示剩余case数
        print("Tasks initialized.")
        state.status = "RUNNING"
        print(state)
        return state

    def __update_tasks_state__(self, state: State):
        print("Updating tasks state...")
        for task in state.config["tasks"]:
            if task["task_type"] in state.completed_tasks:
                state.active_tasks.remove(task["task_type"])
                state.task_states[task["task_type"]]["remaining"] = 0
        return state