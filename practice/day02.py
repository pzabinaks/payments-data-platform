from pathlib import Path

p = Path('data/raw')


#Task  nr 1
file_size = p.stat().st_size
print(file_size)