def convert_tulpe_to_str(tpl):
    result = ""
    if len(tpl) > 0:
        for word in tpl:
            result += str(word) + " "
        result.rstrip()
    return result