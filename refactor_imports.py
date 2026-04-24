import os
import glob

services_dir = "services"

replacements = {
    "from core.": "from shared.core.",
    "import core.": "import shared.core.",
    "from database ": "from shared.database ",
    "import database": "import shared.database",
    "from models ": "from shared.models ",
    "import models": "import shared.models",
    "from alembic": "from shared.alembic"
}

for root, _, files in os.walk(services_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r") as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
                
            if new_content != content:
                print(f"Refactoring imports in {path}")
                with open(path, "w") as f:
                    f.write(new_content)
