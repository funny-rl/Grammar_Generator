import re
import ast
from pprint import pprint 

from typing import Any, Optional
import timeout_decorator
from timeout_decorator.timeout_decorator import TimeoutError 
from reward_model.grammar.counting_context_free_grammar import CountingContextFreeGrammar as Ccfg



def is_invalid_terminal(s: str) -> bool:
    return bool(
        any(
            re.search(pattern, s)
            for pattern in [
                r"\[[^\]]+\]\+",
                r"\\d\+",
                r"\\w\+",
                r"\\s\+",
                r"\\b",
                r"\\S",
                r"\\W",
            ]
        )
    )
    
def get_testcase(
    ccfg: Ccfg,
    timeout: int,
    min_degree: int,
    k: int,
) -> list[tuple[str, int]]:
    """
    throw: Error
    """
    @timeout_decorator.timeout(timeout)  # type: ignore
    def _generate(degree: int) -> str:
        return ccfg.generate(degree=degree)  # type: ignore
    if min_degree == -1:
        assert k == 1
        val = _generate(-1)
        if is_invalid_terminal(val):
            raise ValueError(f"Invalid testcase generated: {val}")
        return [(val, -1)]
    testcases: list[tuple[str, int]] = []
    degree = min_degree
    for _ in range(k):
        while True:
            try:
                val = _generate(degree)
                if is_invalid_terminal(val):
                    raise ValueError(f"Invalid testcase generated: {val}")
                testcases.append((val, degree))
                break
            except TimeoutError as e:
                if degree >= 2:
                    raise e
                degree += 1
    return testcases

def get_testcases(
        grammar: dict[str, Any],
        k: int,
        timeout: int, 
    )-> Optional[tuple[list[str], list[int]]]:
    
    productions = grammar["productions"]
    constraints = grammar["constraints"]
    
    # Raise error if any regex production contains a '+' quantifier
    for prod in productions:
        if re.search(r"\[[^\]]+\]\+", prod) or re.search(r"\\[dws]\+", prod):
            raise ValueError(f"Invalid regex pattern with '+' found in production: {prod}")
        if re.search(r"\[[^\]]*\]\*", prod) or re.search(r"\\[dws]\*", prod):
            raise ValueError(f"Invalid regex pattern with '*' found in production: {prod}")
    
    ccfg = Ccfg(productions, constraints)
    try:
        tuples = get_testcase(ccfg, timeout, -1, 1)
    except TimeoutError:
        tuples = []
        
    tuples += get_testcase(ccfg, timeout, 2, k)
    tuples += get_testcase(ccfg, timeout, 1, k)
    tuples += get_testcase(ccfg, timeout, 0, k)
    return [t[0] for t in tuples], [t[1] for t in tuples]

def extract_solution(solution_str):
    answers = list(re.finditer(r"</think>", solution_str))
    if not answers:
        return None
    end_pos = answers[-1].end()
    return solution_str[end_pos:].strip()    

def compute_score(
        data_source, 
        solution_str, 
        ground_truth, 
        extra_info=None,
        test = False, 
    ):
    """
    compute the reward score of the solution string based on the data source and ground truth.
    """
    solution = solution_str #extract_solution(solution_str)
    total_reward = 0.0
    if solution is None:
        return total_reward
    else:
        try:
            solution = ast.literal_eval(solution)
            if set(solution.keys()) != {"grammar"}:
                return total_reward
            
            grammar = solution["grammar"]
            if set(grammar.keys()) != {"productions", "constraints"}:
                return total_reward

        except Exception as e:
            return total_reward
        if not test:
            total_reward += 0.01

        try:
            testcases, methods = get_testcases(
                grammar = grammar,
                k=10,
                timeout = 10,
            )
            if not test:
                print(f"\nOutput: {solution}")
                print(f"Testcases: {testcases}")
                print(f"Methods: {methods}\n")
            # else:
            #     print(f"\nTest output: {solution}")
            #     print(f"Test Testcases: {testcases}")
            #     print(f"Test Methods: {methods}\n")
            if not test:
                total_reward += 0.99
            else:
                total_reward += 1.00
            return total_reward
            
        except Exception as e:
            #print(f"\nError: {e}\n")
            return total_reward