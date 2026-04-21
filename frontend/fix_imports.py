import os
import re

components_dir = r'c:\IIITH_Coursework_new\Sem6\SE\project_3\FinSight\frontend\src\components'

for filename in os.listdir(components_dir):
    if not filename.endswith('.tsx'):
        continue
    filepath = os.path.join(components_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace `import React, { ... } from 'react';` with `import { ... } from 'react';`
    content = re.sub(r"import\s+React,\s*\{\s*(.*?)\s*\}\s*from\s+['\"]react['\"];", r"import { \1 } from 'react';", content)
    
    # Remove standalone `import React from 'react';`
    content = re.sub(r"import\s+React\s+from\s+['\"]react['\"];\n?", "", content)

    if filename == 'ExpenseChart.tsx':
        content = re.sub(r"import\s+\{\s*Bar\s*\}\s*from\s+['\"]react-chartjs-2['\"];\n?", "", content)
    
    if filename == 'RecommendationsPanel.tsx':
        content = re.sub(r"TrendingUp,\s*", "", content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
