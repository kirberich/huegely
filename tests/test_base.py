import unittest

from huegely import features


class FeatureBaseClas(features.FeatureBase):
    pass


class FeatureBaseTests(unittest.TestCase):
    def test_featurebase_configuration(self):
        """ Tests that FeatureBase classes can only be instantiated when configured. """
        with self.assertRaises(Exception):
            FeatureBaseClas(None, None)

        FeatureBaseClas._device_url_prefix = 'something'
        with self.assertRaises(Exception):
            FeatureBaseClas(None, None)

        delattr(FeatureBaseClas, '_device_url_prefix')
        FeatureBaseClas._state_attribute = 'something'
        with self.assertRaises(Exception):
            FeatureBaseClas(None, None)

        FeatureBaseClas._device_url_prefix = 'something'
        FeatureBaseClas._state_attribute = 'something'
        FeatureBaseClas(None, None)
