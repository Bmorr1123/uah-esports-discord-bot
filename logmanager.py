import json, csv, os

DATA_ROOT = f"data/"

class LogManager:
    def __init__(self):
        self.headers: list = json.load(open(DATA_ROOT + "headers.json", "r+"))
        self.team_info: dict = json.load(open(DATA_ROOT + "teams.json", "r+"))

        self.teams: list = self.team_info["teams"]
        self.name_map = {team["team_name"]: team["id"] for team in self.team_info["teams"]}
        # Filling the player map
        self.player_map = {}
        for team in self.teams:
            for player in team["players"]:
                self.player_map[player] = team["id"]

        self.teams_dir = f"{DATA_ROOT}teams/"

    def __del__(self):
        json.dump(self.headers, open(DATA_ROOT + "headers.json", "w+"))
        json.dump(self.team_info, open(DATA_ROOT + "team_names.json", "w+"))
        print("Dumped headers and name map")

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
            id = len(self.name_map)
        self.name_map[team_name] = id  # We must update this because it isn't updated when adding a team.
        self.teams.append({
                "team_name": team_name,
                "id": id,
                "players": player_ids if player_ids else [],
                "game": game
        })
        self.create_log_file(id)
        return id

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

        file = open(log_path, "w+")
        writer = csv.DictWriter(file, fieldnames=self.headers)
        print(f"Log file created for team id: \"{id}\"!")
        return log_path

    def get_log_file(self, *, id: int = None, team_name: str = None) -> str:
        """
        This function returns a log file for a team by either id or team name.
        :param id: Optional: the id to find the team by.
        :param team_name: Optional: the team name to find the team by.
        :return: The path to the .csv file.
        """
        assert team_name or id
        if team_name:
            id = self.name_map[team_name]

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
        assert team_id and player_id
        for team in self.teams:
            if team["id"] == team_id:
                team["players"].append(player_id)
                self.player_map[player_id] = team_id
                return team["players"]
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
                return team
        raise LookupError(f"Cannot find team with team id: \"{team_id}\"!")
