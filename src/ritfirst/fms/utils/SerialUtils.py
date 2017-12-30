
def ser_readline(ser):
    ret_text = ""
    while True:
        c = ser.read()  # read a character
        ret_text += c  # append it to the string

        if c == "\n":
            break

    return ret_text