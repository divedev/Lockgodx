f = open('chat_log_formatted.txt', 'r+', encoding='utf-8')

new_file: list[str] = []

for line in f:
    new_file.append(line.split('\t')[1][:-1])

with open("chat_log_formatted_noname.txt", "w+") as file:
    for i in new_file:
        try:
            file.write(i+'\n')
        except:
            pass
