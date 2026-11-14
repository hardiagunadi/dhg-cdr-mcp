"""MCP tool: build rich, editable CorelDRAW content from a JSON spec file."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Optional

from core.models import ToolResult
from core.sessions import session_manager


def _spec_file(spec_path: str) -> Path:
    path = Path(spec_path).expanduser()
    if not path.is_absolute():
        raise ValueError("spec_path must be absolute")
    path = path.resolve(strict=True)
    if path.suffix.lower() != ".json":
        raise ValueError("spec_path must be a .json file")
    root = os.environ.get("COREL_OUTPUT_ROOT", "").strip()
    if root:
        try:
            path.relative_to(Path(root).expanduser().resolve(strict=False))
        except ValueError as exc:
            raise PermissionError(f"spec_path is outside COREL_OUTPUT_ROOT: {root}") from exc
    return path


def build_from_spec(
    session_id: str,
    spec_path: str,
    expected_revision: int,
    start: int = 0,
    limit: Optional[int] = None,
) -> ToolResult:
    """Build editable objects (rectangles, curves, text, images, gradients, shadows) from a JSON spec.

    spec_path: absolute path to a .json file inside COREL_OUTPUT_ROOT with {"ops": [...]}.
    All geometry in mm, page top-left origin. start/limit select a slice of ops so large specs
    can be applied in several calls (one undo step per call).
    """
    try:
        path = _spec_file(spec_path)
        spec = json.loads(path.read_text(encoding="utf-8"))
        from tools import spec_engine
        importlib.reload(spec_engine)  # hot reload: engine fixes need no server restart

        payload = session_manager.execute(
            session_id,
            lambda doc: spec_engine.run_spec(doc, spec, start, limit),
            mutation=True,
            expected_revision=expected_revision,
            label="Build from spec",
            timeout=600.0,
        )
        return ToolResult.ok("Spec applied", result=payload["result"], revision=payload["revision"],
                             session=payload["session"])
    except Exception as exc:
        text = str(exc)
        code = "REVISION_CONFLICT" if ("Revision conflict" in text or "changed outside" in text) else "BUILD_FAILED"
        return ToolResult.fail(text, code=code)
