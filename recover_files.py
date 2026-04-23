import re
import os

log_files = [
    "/home/lokesh/.gemini/antigravity/brain/6c4d3f48-461f-4170-bceb-f530f3a721b5/.system_generated/logs/frontend_auth_and_api_integration.txt",
    "/home/lokesh/.gemini/antigravity/brain/6c4d3f48-461f-4170-bceb-f530f3a721b5/.system_generated/logs/backend_database_and_persistence.txt"
]

files_to_find = [
    "LoginPage.tsx", "RegisterPage.tsx", "ManualEntryForm.tsx", "CSVUpload.tsx", 
    "api.ts", "Header.tsx", "TransactionTable.tsx", "BudgetPanel.tsx", 
    "ExpenseChart.tsx", "PortfolioPanel.tsx"
]

found_contents = {}

for log_path in log_files:
    if not os.path.exists(log_path): continue
    with open(log_path, 'r') as f:
        content = f.read()
    
    # We look for write_to_file calls or CodeContent
    # This is a basic regex, might need adjusting depending on the log format.
    # The log contains prompt/response pairs. Tool calls might look like:
    # "CodeContent": "import React..."
    # "TargetFile": ".../front(...)"
    pass

# Alternatively, I can just use a python script that writes all "TargetFile": "..." "CodeContent": "..." to disk.
import json

paths = []
for log_path in log_files:
    with open(log_path, 'r') as f:
        data = f.read()
        # Find all JSON-like tool calls
        # Let's print out how write_to_file is structured in the log.
        print(f"Log: {log_path}, Size: {len(data)}")
        
