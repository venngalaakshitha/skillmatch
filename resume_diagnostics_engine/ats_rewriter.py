def generate_ats_friendly_text(text: str) -> str:
    """
    Removes symbols & excessive formatting.
    """
    cleaned = []
    for line in text.splitlines():
        line = line.replace("•", "-").strip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)
