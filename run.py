from control_flow import label, goto
i = 0
end = 3

label start:
    print(i)
    i += 1
    if i != end:
        goto start
