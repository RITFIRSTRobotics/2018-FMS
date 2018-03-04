
def ser_readline(ser):
    ret_text = ""
    while True:
        c = None
        try:
            c = ser.read().decode()  # read a characters
        except UnicodeDecodeError:
            continue

        ret_text += c # append it to the string

        if c.endswith("\n") or c =="" :
            break

    return ret_text
