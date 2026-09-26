#!/usr/bin/env python3
"""
Byzantine Swarm Sentinel Root CLI Entrypoint.
Delegates directly to byzantine_swarm_sentinel.cli.main().
Zero external dependencies (pure Python standard library).
"""

from byzantine_swarm_sentinel.cli import main

if __name__ == "__main__":
    main()
