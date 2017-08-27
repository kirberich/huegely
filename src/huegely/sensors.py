from datetime import datetime

from huegely.features import (
    FeatureBase,
)


class Sensor(FeatureBase):
    _state_attribute = 'state'
    _device_url_prefix = 'sensors'


class TemperatureSensor(Sensor):
    """Hue temperature sensor, currently just an unused part of the hue motion sensor."""

    def _get_temperature(self):
        """Get current temperature in degrees Celcius."""
        return self.state()['temperature'] / 100
    temperature = _get_temperature


class MotionSensor(Sensor):
    """The hue motion sensor contains multiple sensor, this is the motion part of it."""

    def _get_presence(self):
        """Get current presence state as True or False."""
        return self.state()['presence']
    presence = _get_presence

    def _get_last_updated(self):
        """Get time the presence state was last updated."""
        datetime_string = self.state()['last_updated']
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
    last_updated = _get_last_updated


SENSOR_TYPES = {
    'ZLLTemperature': TemperatureSensor,
    'ZLLPresence': MotionSensor,
}
