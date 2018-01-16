class CommandHandler:
    """Save the commands that can be used during the run of the player."""

    def __init__(self, use_help=True):
        self.saved_commands = dict()
        self.commands_help = dict()

        if use_help:
            self.add_help_command()

    def add_command(self, command, action, notification, return_value, cmd_help=None):
        """Add a known command to the handler.

        If return value is:
        'command' -- return the command itself
        'result' -- return the value returned from action
        'notification' -- return the notification
        """
        self.saved_commands[command] = [action, notification, return_value]

        if not cmd_help is None:
            self.commands_help[command] = str(cmd_help)

    def add_help_command(self):
        self.add_command("-h", self.show_help, None, None, "Show this help message")

    def exist_command(self, command):
        return command in self.saved_commands

    def apply_command(self, command, *args, **kwargs):
        """Assume that the command exist."""
        action, notification, return_value = self.saved_commands[command]

        result = action(*args, **kwargs)

        if not notification is None:
            print("\t{}".format(notification))

        possible_returns = {
            'command': command,
            'result': result,
            'notification': notification,
        }

        # Return the value get with return_value, and the default (in case not found) is return value
        return possible_returns.get(return_value, return_value)

    def show_help(self):
        for cmd in self.saved_commands:
            cmd_help = self.commands_help.get(cmd, "")
            print("'{}' -- {}".format(cmd, cmd_help))
