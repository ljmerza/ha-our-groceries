"""Support for Our Groceries."""
import logging

from aiohttp import web

from homeassistant.components import http
from homeassistant.helpers.entity_component import EntityComponent


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)
DOMAIN = 'ourgroceries'


async def async_setup(hass, config):
    """Add API for interacting with Our Groceries."""
    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL, DOMAIN)

    hass.http.register_view(OurGroceriesView(component))
    await component.async_setup(config)
    return True


class OurGroceriesView(http.HomeAssistantView):
    """View to retrieve Our Groceries content."""

    url = '/api/ourgroceries/{entity_id}'
    name = 'api:ourgroceries:ourgroceries'

    def __init__(self, component):
        """Initialize ourgroceries view."""
        self.component = component

    async def get(self, request, entity_id):
        """Return ourgroceries list details."""
        entity = self.component.get_entity(entity_id)
        list_id = request.query.get('list_id')

        if None in (list_id, entity):
            return web.Response(status=400)

        api_data = await entity.async_grocery_list(request.app['hass'], list_id)
        return self.json(api_data)
