"""Support for Our Groceries."""
from datetime import timedelta
import logging

from aiohttp import web
from ourgroceries import OurGroceries
import voluptuous as vol

from homeassistant.components import http
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.entity_component import EntityComponent


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)
DOMAIN = 'ourgroceries'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Add API for interacting with Our Groceries."""
    og_config = config[DOMAIN]

    _LOGGER.debug('creating og instance')
    hass.data[DOMAIN] = og = OurGroceries(
        username=og_config[CONF_USERNAME],
        password=og_config[CONF_PASSWORD])

    _LOGGER.debug('logging into og')
    await og.login()

    _LOGGER.debug('setting up sensor')
    hass.async_create_task(async_load_platform(hass, 'sensor', DOMAIN, {}, config))

    hass.http.register_view(OurGroceriesView(og))
    _LOGGER.debug('registered view')
    return True


class OurGroceriesView(http.HomeAssistantView):
    """View to retrieve Our Groceries content."""

    url = '/api/ourgroceries/{entity_id}'
    name = 'api:ourgroceries:ourgroceries'

    def __init__(self, og):
        """Initialize ourgroceries view."""
        self._og = og

    async def get(self, request, entity_id):
        """Return ourgroceries list details."""
        _LOGGER.debug('web get')

        list_id = request.query.get('list_id')
        if list_id is None:
            return web.Response(status=400)
        _LOGGER.debug('web get list_id {}'.format(list_id))
        
        api_data = await self._og.get_list_items(list_id)
        return self.json(api_data)
