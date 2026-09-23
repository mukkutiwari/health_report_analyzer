from llm_client import call_llm
from prompts import ANALYSIS_PROMPT, CHATBOT_SYSTEM_PROMPT


def analyze_report(report_text, model_cfg, temperature, max_tokens):
    """
    Core logic for health report analysis
    """
    prompt = ANALYSIS_PROMPT.format(
        report_text=report_text
    )
    return call_llm(prompt, model_cfg, temperature, max_tokens)


def chat_with_report(report_text, chat_history, model_cfg, temperature, max_tokens):
    """
    Core chat logic with report context
    """
    system_prompt = CHATBOT_SYSTEM_PROMPT.format(
        report_text=report_text
    )

    conversation = [system_prompt]
    conversation.extend(m["content"] for m in chat_history)

    full_prompt = "\n".join(conversation)

    return call_llm(full_prompt, model_cfg, temperature, max_tokens)
