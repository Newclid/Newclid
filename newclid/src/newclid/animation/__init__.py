"""Subpackage for animation of Newclid proofs."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from matplotlib.animation import FuncAnimation, HTMLWriter

from newclid.animation.proof_animation import ProofAnimation

__all__ = [
    "ProofAnimation",
    "html_animation",
]


def html_animation(ani: FuncAnimation) -> str:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir, "temp.html")
        writer = HTMLWriter(embed_frames=True, fps=2, embed_limit=100_000_000)
        writer.frame_format = "jpeg"
        ani.save(str(path), writer=writer)
        html_representation = path.read_text()
    return html_representation
