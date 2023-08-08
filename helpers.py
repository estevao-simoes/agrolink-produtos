def execute_sql_file(file_path, engine):
    with open(file_path, "r") as f:
        commands = f.read().split(";")

    for command in commands:
        if not command.strip():
            continue
        with engine.connect() as conn:
            conn.execute(command)
