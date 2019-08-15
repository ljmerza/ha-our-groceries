"""Support for Our Groceries."""
from datetime import timedelta
from functools import wraps
import logging

from ourgroceries import OurGroceries
import voluptuous as vol

from homeassistant.components import http
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.entity_component import EntityComponent


__version__ = '1.2.0'
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

    _LOGGER.debug('creating og instance')
    conf = config[DOMAIN]
    hass.data[DOMAIN] = og = OurGroceries(
        username=conf.get(CONF_USERNAME),
        password=conf.get(CONF_PASSWORD))

    _LOGGER.debug('logging into og')
    await og.login()

    _LOGGER.debug('setting up sensor')
    hass.async_create_task(async_load_platform(hass, 'sensor', DOMAIN, {}, config))

    hass.http.register_view(OurGroceriesView(og))
    _LOGGER.debug('registered view')
    return True


def _handle_api_errors(handler):
    """Webview decorator to handle errors."""
    @wraps(handler)
    async def error_handler(view, request, *args, **kwargs):
        """Handle exceptions that raise from the wrapped request handler."""
        try:
            result = await handler(view, request, *args, **kwargs)
            return result
        except Exception as err:
            return view.json_message(msg=err, status_code=500, message_code=err.__class__.__name__.lower())

    return error_handler


class OurGroceriesView(http.HomeAssistantView):
    """View to retrieve Our Groceries content."""

    url = '/api/ourgroceries'
    name = 'api:ourgroceries:ourgroceries'

    def __init__(self, og):
        """Initialize ourgroceries view."""
        self._og = og

    @_handle_api_errors
    @RequestDataValidator(vol.Schema({
        vol.Required('command'): str,
        vol.Optional('list_id'): str,
        vol.Optional('list_type'): str,
        vol.Optional('name'): str,
        vol.Optional('value'): str,
        vol.Optional('item_id'): str,
        vol.Optional('cross_off'): bool,
    }))
    async def post(self, request, data):
        """Run an our groceries command."""
        _LOGGER.debug(data)
        command = data.get('command')
        _LOGGER.debug('web post command {}'.format(command))
        api_data = None

        if command == 'get_my_lists':
            _LOGGER.debug('web post get_my_lists')
            api_data = await self._og.get_my_lists()

        if command == 'get_list_items':
            list_id = data.get('list_id')

            _LOGGER.debug('web post get_list_items list_id:{}'.format(list_id))
            if list_id is None:
                return self.json({'error': 'missing list_id'}, status_code=400)
            api_data = await self._og.get_list_items(list_id)

        if command == 'create_list':
            name = data.get('name')
            list_type = data.get('list_type')

            _LOGGER.debug('web post get_list_items name:{}, list_type:{}'.format(name, list_type))
            if name is None or list_type is None:
                return self.json({'error': 'missing name or list_type'}, status_code=400)
            api_data = await self._og.create_list(name, list_type)

        if command == 'toggle_item_crossed_off':
            list_id = data.get('list_id')
            item_id = data.get('item_id')
            cross_off = data.get('cross_off')

            _LOGGER.debug('web post get_list_items list_id:{}, item_id:{}, cross_off:{}'.format(list_id, item_id, cross_off))
            if list_id is None or item_id is None or cross_off is None:
                return self.json({'error': 'missing name, item_id, or cross_off'}, status_code=400)
            api_data = await self._og.toggle_item_crossed_off(list_id, item_id, cross_off)

        if command == 'add_item_to_list':
            list_id = data.get('list_id')
            value = data.get('value')

            _LOGGER.debug('web post get_list_items list_id:{}, value:{}'.format(list_id, value))
            if list_id is None or value is None:
                return self.json({'error': 'missing list_id'}, status_code=400)
            api_data = await self._og.add_item_to_list(list_id, value)
        
        if command == 'remove_item_from_list':
            list_id = data.get('list_id')
            item_id = data.get('item_id')

            _LOGGER.debug('web post get_list_items list_id:{}, item_id:{}'.format(list_id, item_id))
            if list_id is None or item_id is None:
                return self.json({'error': 'missing list_id or item_id'}, status_code=400)
            api_data = await self._og.remove_item_from_list(list_id, item_id)
        
        status_code = 200
        if api_data is None:
            api_data = {'error': 'Invalid command'}
            status_code = 400

        hass = request.app['hass']
        await hass.helpers.entity_component.async_update_entity('sensor.our_groceries')

        return self.json(api_data)
