"""Analyze app.py structure."""
with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
with open('app_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print('Written app_analysis.txt')