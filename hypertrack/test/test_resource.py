import uuid
import json
import datetime
import unittest2

import pytest
import requests
from mock import patch

from .helper import DUMMY_PLACE, DUMMY_USER, DUMMY_ACTION, DUMMY_EVENT

from hypertrack.resource import HyperTrackObject
from hypertrack.resource import Event, APIResource, Place, User, Action
from hypertrack.exceptions import InvalidRequestException, RateLimitException
from hypertrack.exceptions import APIConnectionException, APIException
from hypertrack.exceptions import AuthenticationException


class MockResponse(object):
    '''
    Mock API responses
    '''
    def __init__(self, status_code, content, headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = None

    def json(self):
        return json.loads(self.content)


class HyperTrackObjectTests(unittest2.TestCase):
    '''
    Test the base hypertrack object
    '''
    def test_hypertrack_id(self):
        hypertrack_id = str(uuid.uuid4())
        ht = HyperTrackObject(id=hypertrack_id)
        self.assertEqual(ht.hypertrack_id, hypertrack_id)

    def test_str_representation(self):
        hypertrack_id = str(uuid.uuid4())
        ht = HyperTrackObject(id=hypertrack_id)
        self.assertEqual(str(ht), json.dumps({'id': hypertrack_id}, sort_keys=True, indent=2))

    def test_raise_attribute_error_for_private_attribute(self):
        hypertrack_id = str(uuid.uuid4())
        ht = HyperTrackObject(id=hypertrack_id, _blah='blah')

        with pytest.raises(AttributeError):
            ht._blah

    def test_raise_attribute_error_for_non_existing_key(self):
        hypertrack_id = str(uuid.uuid4())
        ht = HyperTrackObject(id=hypertrack_id)

        with pytest.raises(AttributeError):
            ht.blah

    def test_object_representation(self):
        hypertrack_id = str(uuid.uuid4())
        ht = HyperTrackObject(id=hypertrack_id)
        self.assertEqual(repr(ht), ht.__repr__())


class APIResourceTests(unittest2.TestCase):
    '''
    Test base resource methods
    '''
    def test_make_request_successful(self):
        response = MockResponse(200, json.dumps({}))
        method = 'get'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:
            APIResource._make_request(method, url, data, params, files)
            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_connection_error(self):
        response = MockResponse(200, json.dumps({}))
        method = 'get'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError

            with pytest.raises(APIConnectionException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_timeout(self):
        response = MockResponse(200, json.dumps({}))
        method = 'get'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout

            with pytest.raises(APIConnectionException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_invalid_request(self):
        response = MockResponse(400, json.dumps({}))
        method = 'post'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:

            with pytest.raises(InvalidRequestException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_resource_does_not_exist(self):
        response = MockResponse(404, json.dumps({}))
        method = 'post'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:

            with pytest.raises(InvalidRequestException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_authentication_error(self):
        response = MockResponse(401, json.dumps({}))
        method = 'post'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:

            with pytest.raises(AuthenticationException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_rate_limit_exception(self):
        response = MockResponse(429, json.dumps({}))
        method = 'post'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:

            with pytest.raises(RateLimitException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)

    def test_make_request_unhandled_exception(self):
        response = MockResponse(500, json.dumps({}))
        method = 'post'
        url = 'http://example.com'
        headers = APIResource._get_headers()
        data = {'test_data': 'data123'}
        params = {'test_params': 'params123'}
        files = None
        timeout = 20

        with patch.object(requests, 'request', return_value=response) as mock_request:

            with pytest.raises(APIException):
                APIResource._make_request(method, url, data, params, files)

            mock_request.assert_called_once_with(method, url, headers=headers,
                                                 data=json.dumps(data),
                                                 params=params, files=files,
                                                 timeout=timeout)


class PlaceTests(unittest2.TestCase):
    '''
    Test place methods
    '''
    def test_create_place(self):
        response = MockResponse(201, json.dumps(DUMMY_PLACE))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            place = Place.create(**DUMMY_PLACE)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/places/', data=DUMMY_PLACE, files=None)

    def test_retrieve_place(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_PLACE))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            place = Place.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/places/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_place(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_PLACE))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            place = Place(id=hypertrack_id, **DUMMY_PLACE)
            place.city = 'New York'
            place.save()
            mock_request.assert_called_once_with('patch', 'https://api.hypertrack.com/api/v1/places/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': place.city}, files=None)

    def test_list_place(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_PLACE]}))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            places = Place.list()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/places/', params={})

    def test_delete_place(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            place = Place(id=hypertrack_id, **DUMMY_PLACE)
            place.delete()
            mock_request.assert_called_once_with('delete', 'https://api.hypertrack.com/api/v1/places/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))


class UserTests(unittest2.TestCase):
    '''
    Test user methods
    '''
    def test_create_user(self):
        response = MockResponse(201, json.dumps(DUMMY_USER))

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User.create(**DUMMY_USER)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/users/', data=DUMMY_USER, files=None)
            self.assertEqual(user.name, DUMMY_USER.get('name'))

    def test_retrieve_user(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_USER))

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_user(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_USER))

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.city = 'New York'
            user.photo = 'http://photo-url.com/'
            user.save()
            mock_request.assert_called_once_with('patch', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': user.city, 'photo': user.photo}, files=None)

    def test_list_user(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_USER]}))

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            users = User.list()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/users/', params={})

    def test_user_assign_actions(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_USER))
        data = {'action_ids': [str(uuid.uuid4())]}

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.assign_actions(**data)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/assign_actions/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_user_cancel_actions(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_USER))
        data = {}

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.cancel_actions(**data)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/cancel_actions/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_user_stop_tracking(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_USER))
        data = {}

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.stop_tracking()
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/stop_tracking/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_delete_user(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.delete()
            mock_request.assert_called_once_with('delete', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_v2_user_placeline(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps({}))
        data = {}

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.placeline()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/placeline/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_v2_user_mileage(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps({}))
        data = {}

        with patch.object(User, '_make_request', return_value=response) as mock_request:
            user = User(id=hypertrack_id, **DUMMY_USER)
            user.mileage()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/users/{hypertrack_id}/mileage/'.format(hypertrack_id=hypertrack_id), data=data)

class ActionTests(unittest2.TestCase):
    '''
    Test action methods
    '''
    def test_create_action(self):
        response = MockResponse(201, json.dumps(DUMMY_ACTION))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action.create(**DUMMY_ACTION)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/actions/', data=DUMMY_ACTION, files=None)

    def test_retrieve_action(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_ACTION))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_action(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_ACTION))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action(id=hypertrack_id, **DUMMY_ACTION)
            action.city = 'New York'
            action.save()
            mock_request.assert_called_once_with('patch', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': action.city}, files=None)

    def test_list_action(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_ACTION]}))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            actions = Action.list()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/actions/', params={})

    def test_placeline_action(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_ACTION]}))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            actions = Action.placeline()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/actions/placeline/', params={})

    def test_action_completed(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_ACTION))
        completion_location = {'type': 'Point', 'coordinates': [72, 19]}
        data = {'completion_location': completion_location}

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action(id=hypertrack_id, **DUMMY_ACTION)
            action.complete(**data)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/complete/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_action_canceled(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_ACTION))
        cancelation_time = '2016-03-09T06:00:20.648785Z'
        data = {'cancelation_time': cancelation_time}

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action(id=hypertrack_id, **DUMMY_ACTION)
            action.cancel(**data)
            mock_request.assert_called_once_with('post', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/cancel/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_delete_action(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action(id=hypertrack_id, **DUMMY_ACTION)
            action.delete()
            mock_request.assert_called_once_with('delete', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_v2_action_mileage(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps({}))
        data = {}

        with patch.object(Action, '_make_request', return_value=response) as mock_request:
            action = Action(id=hypertrack_id, **DUMMY_ACTION)
            action.mileage()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/actions/{hypertrack_id}/mileage/'.format(hypertrack_id=hypertrack_id), data=data)

class EventTests(unittest2.TestCase):
    '''
    Test event methods
    '''
    def test_retrieve_event(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_EVENT))

        with patch.object(Event, '_make_request', return_value=response) as mock_request:
            event = Event.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/events/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_list_event(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_EVENT]}))

        with patch.object(Event, '_make_request', return_value=response) as mock_request:
            events = Event.list()
            mock_request.assert_called_once_with('get', 'https://api.hypertrack.com/api/v1/events/', params={})
