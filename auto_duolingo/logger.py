import logging
from typing import Any, Dict


def log_incorrect_answer(result: Dict[str, Any]) -> None:
    logging.basicConfig(filename='incorrect_answers.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if result["status"] == "incorrect":
        message = f"Incorrect Answer - Original: {result['original_sentence']}, Correct: {result['correct_answer']}, Selected: {', '.join(result['selected_answer'])}"
        logging.error(message)
        print(message.replace(", Selected:", "\nSelected:").replace(
            "Correct:", "\nCorrect:") + "\n")
