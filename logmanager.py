import json, csv, os
import datetime

DATA_ROOT = f"data/"

class LogManager:
    def __init__(self):
        self.team_info: dict = json.load(self.open_read_file(DATA_ROOT + "teams.json", default_data={}))
        self.headers = ["Date", "Length", "Type",  "Submitted On", "Submitted By", "Result, Opponent"]

        if "teams" not in self.team_info:
            self.team_info["teams"] = []
        self.teams: list = self.team_info["teams"]
        self.team_name_to_id = {team["team_name"]: team["id"] for team in self.team_info["teams"]}
        # Filling the player map
        self.player_map = {}
        for team in self.teams:
            for player in team["players"]:
                self.player_map[player] = team["id"]

        self.teams_dir = f"{DATA_ROOT}teams/"
        self.save()

    def save(self):
        json.dump(self.team_info, open(DATA_ROOT + "teams.json", "w+"), indent=4)
        print("Dumped teams")

    def open_read_file(self, path, default_data=None):
        print(os.listdir(path[:path.rfind("/")]))
        if path[path.rfind("/") + 1:] in os.listdir(path[:path.rfind("/")]):
            return open(path, "r")
        else:
            new_file = open(path, "w")
            if default_data is not None:
                json.dump(default_data, new_file, indent=4)
            new_file.close()
            return open(path, "r")

    def create_team(self, team_name: str, id: str = None, player_ids: list[int] = None, game: str = None) -> int:
        """
        This function creates a team.
        :param team_name: A name for the team.
        :param id: Optional: you can provide an id to give to the team.
        :param game: Optional: you can provide a game that a team plays.
        :param player_ids: Optional: you can provide the discord ids of the players on the team.
        :return: The team id.
        """
        assert team_name
        if not id:
            id = len(self.team_name_to_id)
            while id in self.team_name_to_id.values():
                id += 1
        self.team_name_to_id[team_name] = id  # We must update this because it isn't updated when adding a team.
        self.teams.append({
                "team_name": team_name,
                "id": id,
                "players": player_ids if player_ids else [],
                "game": game
        })
        self.create_log_file(id)
        self.save()
        return id

    def get_team_json_path(self):
        return DATA_ROOT + "teams.json"

    def create_log_file(self, id: int) -> str:
        """
        This function creates a log file and returns the path to it.
        :param id: The team id to create the log file for.
        :return: The path top the file.
        """
        log_path = f"{id}.csv"
        if log_path in os.listdir(self.teams_dir):
            raise FileExistsError(f"Log file already exists for team id: \"{id}\"!")

        log_path = self.teams_dir + log_path

        with open(log_path, "w+") as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            print(f"Log file created for team id: \"{id}\"!")
            return log_path

    def get_log_file(self, *, id: int = None, team_name: str = None) -> str:
        """
        This function returns a log file for a team by either id or team name.
        :param id: Optional: the id to find the team by.
        :param team_name: Optional: the team name to find the team by.
        :return: The path to the .csv file.
        """
        assert team_name is not None or id is not None
        if team_name:
            id = self.team_name_to_id[team_name]

        log_path = f"{id}.csv"
        if log_path not in os.listdir(self.teams_dir):
            raise FileNotFoundError(f"Log file does not exist for team id: \"{id}\"!")

        log_path = self.teams_dir + log_path

        return log_path

    def add_player_to_team(self, team_id: int, player_id: int) -> list[int]:
        """
        Adds a player to a team
        :param team_id: The id of the team.
        :param player_id: The id of the player.
        :return: The list of players on that team.
        """
        assert team_id is not None and player_id is not None
        for team in self.teams:
            if team["id"] == team_id:
                team["players"].append(player_id)
                self.player_map[player_id] = team_id
                self.save()
                return team
        raise LookupError(f"Cannot find team with team id: \"{team_id}\"!")

    def remove_player_from_team(self, team_id: int, player_id: int) -> list[int]:
        """
        Adds a player to a team
        :param team_id: The id of the team.
        :param player_id: The id of the player.
        :return: The list of players on that team.
        """
        assert team_id is not None and player_id is not None
        for team in self.teams:
            if team["id"] == team_id:
                team["players"].remove(player_id)
                del self.player_map[player_id]
                self.save()
                return team
        raise LookupError(f"Cannot find team with team id: \"{team_id}\"!")

    def get_team(self, team_id: int) -> dict:
        assert team_id is not None
        for team in self.teams:
            if team["id"] == team_id:
                return team
        raise LookupError(f"Cannot find team with team id: \"{team_id}\"!")

    def add_game_to_team(self, team_id: int, game_name: str):
        """
        Adds a player to a team
        :param team_id: The id of the team.
        :param game_name: The name of the game.
        :return: The list of players on that team.
        """
        assert team_id and game_name
        for team in self.teams:
            if team["id"] == team_id:
                team["game"] = game_name
                self.save()
                return team
        raise LookupError(f"Cannot find team with team id: \"{team_id}\"!")

    def add_log(
            self,
            team_id: int,
            date_of_practice: datetime.date,
            length: str,
            log_type: str,
            submitted_by_name: str,
            result: str,
            opponent: str = ""
    ):
        with open(self.get_log_file(id=team_id), "a", newline="") as csvfile:
            logfile = csv.writer(csvfile)
            now = datetime.date.today()

            logfile.writerow([
                date_of_practice.strftime("%m/%d/%Y"),
                length,
                log_type,
                now.strftime("%m/%d/%Y"),
                submitted_by_name,
                result,
                opponent
            ])

    def get_log_as_objects(self, team_id: int) -> [dict]:
        with open(self.get_log_file(id=team_id), "r") as csvfile:
            csv_reader = csv.DictReader(csvfile)

            deserialized = []
            for entry in csv_reader:
                deserialized.append({
                    **entry,
                    "Date": datetime.datetime.strptime(entry["Date"], "%m/%d/%Y").date(),
                    "Submitted On": datetime.datetime.strptime(entry["Submitted On"], "%m/%d/%Y").date()
                })
            return deserialized

    def get_most_recent_practice(self, team_id: int, include_matches=False) -> dict:
        log = self.get_log_as_objects(team_id)

        if len(log) == 0:
            return None
        most_recent = log[0]
        for entry in log:
            if entry["Type"] in ["Scrimmage", "Practice"] or include_matches:
                if entry["Date"] > most_recent["Date"]:
                    most_recent = entry

        return most_recent

    def get_inverse_team_map(self):
        return {name: team_id for team_id, name in self.team_name_to_id.items()}

    def get_mega_log(self):

        mega_log_path = DATA_ROOT + "mega_log.csv"
        mega_log_file = open(mega_log_path, "w+", newline="")
        
        modified_headers = ["Team Name", "Team ID", "Game"] + [header for header in self.headers]

        mega_log = csv.writer(mega_log_file)
        mega_log.writerow(modified_headers)

        for team in self.teams:
            log_path = self.teams_dir + f"{team['id']}.csv"
            with open(log_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    mega_log.writerow([
                        team["team_name"],
                        team["id"],
                        team["game"],
                        *[row[header] if header in row else "" for header in self.headers]
                    ])
        
        mega_log_file.close()
        return mega_log_path
