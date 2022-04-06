__CONTROL_FLOW_CURR_LABEL__: int = 0       
while True:
    if __CONTROL_FLOW_CURR_LABEL__ <= 0:   

        i = 0
        end = 3

    if __CONTROL_FLOW_CURR_LABEL__ <= 1:   
        print(i)
        i += 1
        if i != end:
            __CONTROL_FLOW_CURR_LABEL__ = 1
            continue

    break
