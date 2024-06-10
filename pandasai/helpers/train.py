import re
from typing import Tuple


def parse_qa_doc(doc) -> Tuple[str, str]:
    question_pattern = r"Q:\s*(.+?)\s*A:"
    answer_pattern = r"A:\s*(.+)"

    # Find the question using regex
    question_match = re.search(question_pattern, doc)
    question = question_match.group(1).strip() if question_match else None

    # Find the answer using regex
    answer_match = re.search(answer_pattern, doc, re.DOTALL)
    answer = answer_match.group(1).strip() if answer_match else None

    return question, answer
