import logging
from pathlib import Path

logger = logging.getLogger(__name__)

HEADER = "# Knowledge Base\n\n"


def compile_output(chunks: list[str], config) -> list[str]:
    if not chunks:
        logger.warning("No content to compile")
        return []

    parts = _split_into_parts(chunks, config.chunk_size)
    output_path = Path(config.output_file)
    written_files = []

    if len(parts) == 1:
        _write_part(output_path, parts[0])
        written_files.append(str(output_path))
    else:
        stem = output_path.stem
        suffix = output_path.suffix
        parent = output_path.parent
        for i, part in enumerate(parts, 1):
            part_path = parent / f"{stem}_part{i}{suffix}"
            _write_part(part_path, part)
            written_files.append(str(part_path))

    for f in written_files:
        size = Path(f).stat().st_size
        logger.info(f"Written: {f} ({size:,} bytes)")

    return written_files


def _split_into_parts(chunks: list[str], max_size: int) -> list[list[str]]:
    parts = []
    current_part = []
    current_size = len(HEADER)

    for chunk in chunks:
        chunk_size = len(chunk)
        if current_part and current_size + chunk_size > max_size:
            parts.append(current_part)
            current_part = []
            current_size = len(HEADER)
        current_part.append(chunk)
        current_size += chunk_size

    if current_part:
        parts.append(current_part)

    return parts


def _write_part(path: Path, chunks: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        for chunk in chunks:
            f.write(chunk)
