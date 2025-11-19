#!/usr/bin/env python3
"""
Fix relative imports in all agent files
Replaces: from ..base_agent import BaseAgent, AgentConfig
With: import sys; os.path; sys.path.insert...; from base_agent import...
"""
import os
import re

# List of agent files to fix
agent_files = [
    "agents/market_agent/market_agent.py",
    "agents/finance_agent/finance_agent.py",
    "agents/tax_agent/tax_agent.py",
    "agents/distribution_agent/distribution_agent.py",
    "agents/investment_agent/investment_agent.py",
    "agents/legal_agent/legal_agent.py",
    "agents/news_agent/news_agent.py",
]

def fix_import(file_path):
    """Fix relative import in a file"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Pattern to match: from ..base_agent import ...
    pattern = r'from \.\.base_agent import (.+)'

    if re.search(pattern, content):
        # Replace with absolute import
        new_import = r'''import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import \1'''

        content = re.sub(pattern, new_import, content)

        # Write back
        with open(file_path, 'w') as f:
            f.write(content)

        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"⏭️  Skipped: {file_path} (no relative import found)")
        return False

if __name__ == "__main__":
    print("Fixing relative imports in agent files...")
    fixed_count = 0

    for file_path in agent_files:
        if os.path.exists(file_path):
            if fix_import(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  Not found: {file_path}")

    print(f"\n✅ Fixed {fixed_count} files")
