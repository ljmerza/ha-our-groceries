"""Support for Our Groceries."""
import logging

from aiohttp import web
from ourgroceries import OurGroceries
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity


_LOGGER = logging.getLogger(__name__)

ATTR_RECIPES = 'recipes'
ATTR_SHOPPING_LISTS = 'shopping_lists'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the OurGroceries sensor platform."""

    og = OurGroceries(
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD])
    await og.login()

    add_entities([OurGroceriesSensor(og)], True)


class OurGroceriesSensor(Entity):
    """Representation of an Our Groceries sensor."""

    def __init__(self, og):
        """Initialize the sensor."""
        self._og = og
        self._lists = []

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'our_groceries'

    @property
    def state(self):
        """Return the state of the sensor."""
        shopping_lists = len(self._lists.get('shoppingLists', []))
        recipes = len(self._lists.get('recipes', []))
        return shopping_lists + recipes

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_RECIPES: self._lists.get('recipes'),
            ATTR_SHOPPING_LISTS: self._lists.get('shoppingLists')
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:format-list-bulleted'

    async def async_update(self):
        """Update data from API."""
        self._lists = await self._og.get_my_lists()

    async def async_grocery_list(self, hass, list_id, command=None, item_id=None, item_body=None):
        """Do something with a list."""

        if command == 'get':
            return await self._og.get_list_items(list_id)

