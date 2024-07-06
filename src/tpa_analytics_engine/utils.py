import yaml  # type: ignore


def get_config(config_path: str) -> dict:
    """A shared function taking a path to the config YAML and returning the contents as a dictionary

    Args:
        config_path (str): The path to the config file or the content of the

    Returns:
        dict: A dictionary with the loaded config
    """

    with open(config_path, "r") as file:
        # Load the contents of the file
        configDict = yaml.safe_load(file)

    return configDict

    # TODO: Change argument to Pathlib type
