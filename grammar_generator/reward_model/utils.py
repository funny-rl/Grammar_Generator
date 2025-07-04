import re
import os 
from typing import Any, Optional
import timeout_decorator
from timeout_decorator.timeout_decorator import TimeoutError 
from reward_model.grammar.counting_context_free_grammar import CountingContextFreeGrammar as Ccfg

from reward_model.grammar.discriminator import discriminator  # type: ignore
from statistics import mean
from concurrent.futures import ProcessPoolExecutor, as_completed


def extract_solution(solution_str: str) -> str | None:

    think_token_occurrences = re.findall(r'</think>', solution_str)
    if len(think_token_occurrences) != 1:
        return None
    match = re.search(r'</think>(.*)', solution_str)
    return match.group(1)

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
    @timeout_decorator.timeout(timeout) 
    def _generate(degree: int) -> str:
        return ccfg.generate(degree=degree)  
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
        tuples = get_testcase(ccfg, timeout, -1, 1) # deterministic 
    except TimeoutError:
        tuples = []
        
    tuples += get_testcase(ccfg, timeout, 2, k)
    tuples += get_testcase(ccfg, timeout, 1, k)
    tuples += get_testcase(ccfg, timeout, 0, k)
    return [t[0] for t in tuples], [t[1] for t in tuples]

def check_syntactic_validness(testcase: str, gt_grammar: dict) -> bool:
    @timeout_decorator.timeout(10)  
    def _check_syntactic_validness(testcase: str, grammar: dict) -> bool:
        d = discriminator()
        productions = grammar["productions"]
        constraints = grammar["constraints"]
        return d(productions, constraints, testcase)  
    try:
        return _check_syntactic_validness(testcase, gt_grammar)
    except Exception as e:  
        return False
def calculate_validity(testcases: list[str], gt_grammar: dict) -> float:
    parsable_cases = [check_syntactic_validness(testcase, gt_grammar) for testcase in testcases]
    validity = mean(parsable_cases)
    return validity