
def ser_readline(ser):
    ret_text = ""
    while True:
        c = None
        try:
            c = ser.read().decode()  # read a characters
        except UnicodeDecodeError:
            continue

        if c == "\n" or c == "" :
            ret_text += c
            break

        if ord(c) < 32 or ord(c) > 123:
            continue

        ret_text += c # append it to the string



    return ret_text
