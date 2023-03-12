def get_input():
    input_word = input("请输入名称: ")
    input_word = input_word.strip().replace('（', '(').replace('）', ')').split('(')  # 替换中文括号
    if len(input_word) != 2:  # 检查格式
        print("长度不一致，请重新输入")
        return -1
    else:  # 格式正确
        input_word[1] = input_word[1].strip(')').title()  # 提取输入
        print((input_word[0], input_word[1]))
        format_name = input_word[0] + " " + input_word[1]
        return input_word, format_name
