import os
  
empty = []
valid = []
for root, dirs, files in os.walk('output_files/'):
    if not len(dirs) and not len(files):
  
        empty.append(root)
    else:
        valid.append(root)
  
print(f"Empty Directories {len(empty)}:")
for path in empty:
    print(path)

print(f"\nFilled Directories {len(valid)}/{len(empty) + len(valid)}")