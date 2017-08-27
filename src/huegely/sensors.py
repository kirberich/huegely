from datetime import (
    datetime,
    timedelta,
)

from huegely.features import (
    FeatureBase,
)


class Sensor(FeatureBase):
    _state_attribute = 'state'
    _device_url_prefix = 'sensors'

    def __init__(self, bridge, device_id, name=None, state=None):
        super().__init__(bridge, device_id, name=name)
        self._state = state
        self._state_set_at = datetime.now()

    def state(self, max_age=0):
        """Sensors generally get updated very rarely, so we add some simple caching."""

        if self._state and datetime.now() - self._state_set_at <= timedelta(seconds=max_age):
            state = self._state
        else:
            state = super().state()
            self._state_set_at = datetime.now()

        return state


class TemperatureSensor(Sensor):
    """Hue temperature sensor, currently just an unused part of the hue motion sensor."""

    def _get_temperature(self, max_age=0):
        """Get current temperature in degrees Celcius."""
        return self.state(max_age=max_age)['temperature'] / 100
    temperature = _get_temperature


class MotionSensor(Sensor):
    """The hue motion sensor contains multiple sensor, this is the motion part of it."""

    def _get_presence(self, max_age=0):
        """Get current presence state as True or False."""
        return self.state(max_age=max_age)['presence']
    presence = _get_presence

    def _get_last_updated(self, max_age=0):
        """Get time the presence state was last updated."""
        datetime_string = self.state(max_age=max_age)['last_updated']
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
    last_updated = _get_last_updated


SENSOR_TYPES = {
    'ZLLTemperature': TemperatureSensor,
    'ZLLPresence': MotionSensor,
}
