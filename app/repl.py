from app.channel import CLI, IDatabase


def repl(db: IDatabase) -> None:
    while True:
        # read command
        cmd = CLI().read_cmd()
        if cmd == "":
            break
        # evaluate
        command = CLI().parse_cmd(cmd, db)
        # print
        CLI().run(command, cmd)
