from app.services.code_parser import extract_code_block, strip_code_blocks


def test_extract_code_block_returns_first_supported_block() -> None:
    message = "Intro\n```tsx\nexport default function App() { return <div /> }\n```\nFooter"
    assert extract_code_block(message) == "export default function App() { return <div /> }"


def test_strip_code_blocks_removes_code_and_preserves_text() -> None:
    message = "Fix applied\n\n```jsx\nexport default function App() { return null }\n```\n\nUse this version."
    assert strip_code_blocks(message) == "Fix applied\n\nUse this version."
