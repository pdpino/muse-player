class CommandHandler:
    """Save the commands that can be used during the run of the player."""

    def __init__(self):
        self.saved_commands = dict()

    def add_command(self, command, action, notification, return_value):
        """Add a known command to the handler.

        If return value is:
        'command' -- return the command itself
        'result' -- return the value returned from action
        'notification' -- return the notification
        """
        self.saved_commands[command] = [action, notification, return_value]

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
