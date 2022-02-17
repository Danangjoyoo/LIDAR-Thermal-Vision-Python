from modules import executor, utils

kargv = utils.getKwargv()

program = None

def main():
    global program
    if kargv["thermal"]:
        program = executor.executeWithThermal()
    else:
        program = executor.execute()

if __name__ == "__main__":
    main()
    # executor.execute2()