from datetime import datetime
from infinipy.affordance import Affordance
from infinipy.statement import Statement, CompositeStatement
from infinipy.stateblock import StateBlock
from typing import List, Dict, Any, Union, Tuple, Optional, Set

class GOAPLogger:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def _log(self, entry: Dict[str, Any]):
        self.logs.append(entry)

    def log_goal_achieved(self, goal: str, entity: StateBlock, result: bool):
        self._log({
            'timestamp': datetime.now(),
            'method': 'is_goal_achieved',
            'goal': goal,
            'entity': entity.name,
            'result': result
        })

    def log_filtered_subgoals(self, goal: str, entity: StateBlock, satisfied_subgoals: List[str], target_subgoals: List[str]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'get_filtered_subgoals',
            'goal': goal,
            'entity': entity.name,
            'satisfied_subgoals': satisfied_subgoals,
            'target_subgoals': target_subgoals
        })

    def log_terminal_affordances(self, goal: str, entity: StateBlock, terminal_affordances: List[Affordance], partial_affordances: List[List[Affordance]]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_terminal_affordances',
            'goal': goal,
            'entity': entity.name,
            'terminal_affordances': [a.name for a in terminal_affordances],
            'partial_affordances': [[a.name for a in affordances] for affordances in partial_affordances]
        })

    def log_subgoals_for_affordance(self, affordance: Affordance, entity: StateBlock, subgoals: List[str]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_subgoals_for_affordance',
            'affordance': affordance.name,
            'entity': entity.name,
            'subgoals': subgoals
        })

    def log_achieve_goal(self, goal: str, entity: StateBlock, depth: int, applied_actions: List[Affordance]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'goal': goal,
            'entity': entity.name,
            'depth': depth,
            'applied_actions': [a.name for a in applied_actions]
        })

    def log_create_composite_statement(self, affordance_name: str, prerequisite_name: str, composite_statement_name: str):
        self._log({
            'timestamp': datetime.now(),
            'method': 'extract_prerequisites',
            'affordance': affordance_name,
            'prerequisite': prerequisite_name,
            'composite_statement': composite_statement_name
        })

    def log_extract_prerequisites(self, total_affordances: int, total_prerequisites: int):
        self._log({
            'timestamp': datetime.now(),
            'method': 'extract_prerequisites',
            'total_affordances': total_affordances,
            'total_prerequisites': total_prerequisites
        })

    def log_applying_affordance(self, affordance_name: str, entity_name: str, depth: int):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'affordance_applied': affordance_name,
            'entity': entity_name,
            'depth': depth
        })

    def log_recursion_limit_reached(self, goal: str, entity: StateBlock, depth: int):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'goal': goal,
            'entity': entity.name,
            'depth': depth,
            'message': 'Recursion limit reached'
        })

    def log_evaluating_affordance_applicability(self, affordance_name: str, entity_name: str):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_subgoals_for_affordance',
            'affordance': affordance_name,
            'entity': entity_name,
            'message': 'Evaluating affordance applicability'
        })

    def log_identifying_subgoal_for_affordance(self, affordance_name: str, subgoal: str, entity_name: str):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_subgoals_for_affordance',
            'affordance': affordance_name,
            'subgoal_identified': subgoal,
            'entity': entity_name
        })

    def log_achieve_goal_start(self, goal: str, entity_name: str, depth: int):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'goal': goal,
            'entity': entity_name,
            'depth': depth,
            'message': 'Start of recursion level'
        })

    def log_goal_already_achieved(self, goal: str, entity_name: str, depth: int):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'goal': goal,
            'entity': entity_name,
            'depth': depth,
            'message': 'Goal already achieved'
        })

    def log_achieve_goal_end(self, goal: str, entity_name: str, depth: int, applied_actions: List[Affordance]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'achieve_goal',
            'goal': goal,
            'entity': entity_name,
            'depth': depth,
            'applied_actions': [a.name for a in applied_actions],
            'message': 'End of recursion level'
        })
    def log_partial_affordance_found(self, affordance_names: List[str]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_terminal_affordances',
            'partial_affordances': affordance_names,
            'message': 'Partial affordances found'
        })

    def log_combined_partial_affordances(self, combined_affordances: List[str]):
        self._log({
            'timestamp': datetime.now(),
            'method': 'find_terminal_affordances',
            'combined_affordances': combined_affordances,
            'message': 'Combined partial affordances found'
        })
    def print_logs(self):
        for log in self.logs:
            print(f"{log['timestamp']}: {log['method']} - {log}")

    def print_plan(self):
        print("GOAP Planning Process Report\n" + "="*50 + "\n")

        for log in self.logs:
            timestamp = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            method = log.get('method', 'Unknown method')

            report = [f"Time: {timestamp}", f"Action: {method}"]

            # Common keys
            if 'goal' in log:
                report.append(f"Goal: {log['goal']}")
            if 'entity' in log:
                if isinstance(log['entity'], StateBlock):
                    report.append(f"Entity: {log['entity'].name}")
                report.append(f"Entity: {log['entity']}")

            # Method-specific keys
            if method == 'is_goal_achieved':
                report.append(f"Result: {'Achieved' if log['result'] else 'Not Achieved'}")

            elif method in ['get_filtered_subgoals', 'find_terminal_affordances']:
                if 'satisfied_subgoals' in log:
                    report.append(f"Satisfied Subgoals: {', '.join(log['satisfied_subgoals'])}")
                if 'target_subgoals' in log:
                    report.append(f"Target Subgoals: {', '.join(log['target_subgoals'])}")
                if 'terminal_affordances' in log:
                    report.append(f"Terminal Affordances: {', '.join(log['terminal_affordances'])}")
                # if 'partial_affordances' in log:
                #     report.append(f"Partial Affordances: {', '.join(log['partial_affordances'])}")

            elif method == 'find_subgoals_for_affordance':
                if 'subgoals' in log:
                    report.append(f"Subgoals: {', '.join(log['subgoals'])}")
                if 'affordance' in log:
                    report.append(f"Affordance: {log['affordance']}")

            elif method == 'achieve_goal':
                if 'depth' in log:
                    report.append(f"Depth: {log['depth']}")
                if 'applied_actions' in log:
                    actions = ', '.join(log['applied_actions'])
                    report.append(f"Applied Actions: {actions}")

            elif method == 'extract_prerequisites':
                if 'affordance' in log and 'prerequisite' in log and 'composite_statement' in log:
                    report.append(f"Affordance: {log['affordance']}\nPrerequisite: {log['prerequisite']}\nComposite Statement: {log['composite_statement']}")

            # Add any additional key checks for other methods

            # Printing the formatted report for the log entry
            print('\n'.join(report) + "\n" + "-"*50 + "\n")
