from time import sleep

class ImuEngine:
    """Engine to handle the receiving of Imu data (accelerometer or gyroscope)."""

    def __init__(self, name, imu_buffer, generator):
        """Initialize.

        name -- string identifier
        imu_buffer --
        generator -- """

        self.name = name or "Muse Player"
        self.imu_buffer = imu_buffer
        self.generator = generator

    def incoming_data(self, timestamp, new_data):
        """Proccess the incoming data."""
        self.imu_buffer.incoming(timestamp, new_data)

    def outgoing_data(self):
        """Generator that yields the outgoing data."""

        self.imu_buffer.clear()

        while True:
            timestamp, new_data = self.imu_buffer.outgoing()

            if timestamp is None or new_data is None:
                sleep(0.1)
                continue

            yield from self.generator.generate(timestamp, new_data)
