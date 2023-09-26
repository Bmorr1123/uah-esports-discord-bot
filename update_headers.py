from logmanager import LogManager

lm = LogManager()

for team in lm.teams:
    id = team["id"]
    read_file = open(f"data/teams/{id}.csv", "r")
    lines = [line for line in read_file.readlines() if line != '\n']  # Removes \n
    print(lines)
    write_file = open(f"data/teams/{id}.csv", "w+")
    write_file.write(",".join(lm.headers) + "\n")
    write_file.writelines(lines[1:])


