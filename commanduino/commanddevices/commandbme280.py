from .commanddevice import CommandDevice

import logging
module_logger = logging.getLogger(__name__)

# bonjour info
BONJOUR_ID = 'BME280'
CLASS_NAME = 'CommandBME280'

# incoming
CMD_ANSWER_PRESSURE = 'P'
CMD_ANSWER_TEMPERATURE = 'T'
CMD_ANSWER_HUMIDITY = 'H'

# outgoing
CMD_REQUEST_PRESSURE = 'RP'
CMD_REQUEST_TEMPERATURE = 'RT'
CMD_REQUEST_HUMIDITY = 'RH'


class CommandBME280(CommandDevice):

    def __init__(self):
        CommandDevice.__init__(self)
        self.register_all_requests()

    def register_all_requests(self):
        self.register_request(
            CMD_REQUEST_PRESSURE,
            CMD_ANSWER_PRESSURE,
            'pressure',
            self.handle_pressure_command)

        self.register_request(
            CMD_REQUEST_TEMPERATURE,
            CMD_ANSWER_TEMPERATURE,
            'temperature',
            self.handle_temperature_command)

        self.register_request(
            CMD_REQUEST_HUMIDITY,
            CMD_ANSWER_HUMIDITY,
            'humidity',
            self.handle_humidity_command)

    def handle_pressure_command(self, *arg):
        if arg[0]:
            self.pressure = float(arg[0])
            self.pressure_lock.ensure_released()
    
    def handle_temperature_command(self, *arg):
        if arg[0]:
            self.temperature = float(arg[0])
            self.temperature_lock.ensure_released()
    
    def handle_humidity_command(self, *arg):
        if arg[0]:
            self.humidity = float(arg[0])
            self.humidity_lock.ensure_released()
            