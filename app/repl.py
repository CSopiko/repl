from app.channel import Database, IOCommand


def repl(db: Database) -> None:
    while True:
        # read command
        command_str = IOCommand().read_command()
        if command_str == "":
            break
        # evaluate
        command_type = IOCommand().evaluate_command(command_str, db)
        # print
        IOCommand().print_command(command_type, command_str)
