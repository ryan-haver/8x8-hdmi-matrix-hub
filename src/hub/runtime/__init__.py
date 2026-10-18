"""Shared runtime composition, without optional integration imports."""

from .config import MatrixAddress, ReconfigureResult, resolve_matrix_address

__all__ = ["MatrixAddress", "ReconfigureResult", "resolve_matrix_address"]
