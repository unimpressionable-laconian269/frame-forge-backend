import re

CODE_BLOCK_PATTERN = re.compile(r"```(?:tsx|jsx|ts|js)?\n(?P<code>.*?)```", re.DOTALL)


def extract_code_block(message: str) -> str | None:
    match = CODE_BLOCK_PATTERN.search(message)
    if not match:
        return None
    return match.group("code").strip()


def strip_code_blocks(message: str) -> str:
    cleaned = CODE_BLOCK_PATTERN.sub("", message).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)
