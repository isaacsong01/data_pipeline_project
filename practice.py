secret_num = 10
found = False
for i in range(1,11):
    if i == secret_num:
        found = True
        print('Found')

if not found:
    print('Not Found')

