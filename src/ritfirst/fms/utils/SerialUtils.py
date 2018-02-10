
def ser_readline(ser):
    ret_text = ""
    while True:
        c = ser.read().decode()  # read a characters
        ret_text += c # append it to the string

        if c == "\n" or c =="" :
            break

    return ret_text