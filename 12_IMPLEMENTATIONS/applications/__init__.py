"""
Applications built on the core implementations — AURA text checker, MCP guard
server, web demo, Sol companion, CASCADE tooling.

This file exists so the directory ships as ``lycheetah.applications`` in a built
distribution. It deliberately imports nothing: several modules here carry optional
dependencies (``flask``, ``mcp``, ``rich``), and importing them eagerly would make
the whole package unimportable when an optional extra is not installed.
"""
