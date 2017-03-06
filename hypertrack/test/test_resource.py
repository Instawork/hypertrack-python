import uuid
import json
import datetime
import unittest2

import pytest
import requests
from mock import patch

from .helper import DUMMY_CUSTOMER, DUMMY_DESTINATION, DUMMY_FLEET, DUMMY_DRIVER
from .helper import DUMMY_HUB, DUMMY_TASK, DUMMY_TRIP, DUMMY_GPSLOG, DUMMY_EVENT
from .helper import DUMMY_NEIGHBORHOOD

from hypertrack.resource import HyperTrackObject
from hypertrack.resource import Trip, GPSLog, Event, APIResource, Neighborhood
from hypertrack.resource import Customer, Destination, Fleet, Driver, Hub, Task
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
    Test destination methods
    '''
    def test_create_place(self):
        response = MockResponse(201, json.dumps(DUMMY_DESTINATION))

        with patch.object(Place, '_make_request', return_value=response) as mock_request:
            destination = Destination.create(**DUMMY_DESTINATION)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/destinations/', data=DUMMY_DESTINATION, files=None)

    def test_retrieve_place(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DESTINATION))

        with patch.object(Destination, '_make_request', return_value=response) as mock_request:
            destination = Destination.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/destinations/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_destination(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DESTINATION))

        with patch.object(Destination, '_make_request', return_value=response) as mock_request:
            destination = Destination(id=hypertrack_id, **DUMMY_DESTINATION)
            destination.city = 'New York'
            destination.save()
            mock_request.assert_called_once_with('patch', 'https://app.hypertrack.io/api/v1/destinations/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': destination.city}, files=None)

    def test_list_destination(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_DESTINATION]}))

        with patch.object(Destination, '_make_request', return_value=response) as mock_request:
            destinations = Destination.list()
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/destinations/', params={})

    def test_delete_destination(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(Destination, '_make_request', return_value=response) as mock_request:
            destination = Destination(id=hypertrack_id, **DUMMY_DESTINATION)
            destination.delete()
            mock_request.assert_called_once_with('delete', 'https://app.hypertrack.io/api/v1/destinations/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))


class DriverTests(unittest2.TestCase):
    '''
    Test driver methods
    '''
    def test_create_driver(self):
        response = MockResponse(201, json.dumps(DUMMY_DRIVER))

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver.create(**DUMMY_DRIVER)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/drivers/', data=DUMMY_DRIVER, files=None)
            self.assertEqual(driver.name, DUMMY_DRIVER.get('name'))

    def test_retrieve_driver(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DRIVER))

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/drivers/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_driver(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DRIVER))

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver(id=hypertrack_id, **DUMMY_DRIVER)
            driver.city = 'New York'
            driver.photo = 'http://photo-url.com/'
            driver.save()
            mock_request.assert_called_once_with('patch', 'https://app.hypertrack.io/api/v1/drivers/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': driver.city, 'photo': driver.photo}, files=None)

    def test_list_driver(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_DRIVER]}))

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            drivers = Driver.list()
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/drivers/', params={})

    def test_driver_end_trip(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DRIVER))
        data = {}

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver(id=hypertrack_id, **DUMMY_DRIVER)
            driver.end_trip()
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/drivers/{hypertrack_id}/end_trip/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_driver_assign_tasks(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_DRIVER))
        data = {'task_ids': [str(uuid.uuid4())]}

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver(id=hypertrack_id, **DUMMY_DRIVER)
            driver.assign_tasks(**data)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/drivers/{hypertrack_id}/assign_tasks/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_delete_driver(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(Driver, '_make_request', return_value=response) as mock_request:
            driver = Driver(id=hypertrack_id, **DUMMY_DRIVER)
            driver.delete()
            mock_request.assert_called_once_with('delete', 'https://app.hypertrack.io/api/v1/drivers/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))


class TaskTests(unittest2.TestCase):
    '''
    Test task methods
    '''
    def test_create_task(self):
        response = MockResponse(201, json.dumps(DUMMY_TASK))

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task.create(**DUMMY_TASK)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/tasks/', data=DUMMY_TASK, files=None)

    def test_retrieve_task(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_TASK))

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/tasks/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_update_task(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_TASK))

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task(id=hypertrack_id, **DUMMY_TASK)
            task.city = 'New York'
            task.save()
            mock_request.assert_called_once_with('patch', 'https://app.hypertrack.io/api/v1/tasks/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id), data={'city': task.city}, files=None)

    def test_list_task(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_TASK]}))

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            tasks = Task.list()
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/tasks/', params={})

    def test_task_completed(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_TASK))
        completion_location = {'type': 'Point', 'coordinates': [72, 19]}
        data = {'completion_location': completion_location}

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task(id=hypertrack_id, **DUMMY_TASK)
            task.complete(**data)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/tasks/{hypertrack_id}/completed/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_task_canceled(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_TASK))
        cancelation_time = '2016-03-09T06:00:20.648785Z'
        data = {'cancelation_time': cancelation_time}

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task(id=hypertrack_id, **DUMMY_TASK)
            task.cancel(**data)
            mock_request.assert_called_once_with('post', 'https://app.hypertrack.io/api/v1/tasks/{hypertrack_id}/canceled/'.format(hypertrack_id=hypertrack_id), data=data)

    def test_delete_task(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(204, json.dumps({}))

        with patch.object(Task, '_make_request', return_value=response) as mock_request:
            task = Task(id=hypertrack_id, **DUMMY_TASK)
            task.delete()
            mock_request.assert_called_once_with('delete', 'https://app.hypertrack.io/api/v1/tasks/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))


class EventTests(unittest2.TestCase):
    '''
    Test event methods
    '''
    def test_retrieve_event(self):
        hypertrack_id = str(uuid.uuid4())
        response = MockResponse(200, json.dumps(DUMMY_EVENT))

        with patch.object(Event, '_make_request', return_value=response) as mock_request:
            event = Event.retrieve(hypertrack_id)
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/events/{hypertrack_id}/'.format(hypertrack_id=hypertrack_id))

    def test_list_event(self):
        response = MockResponse(200, json.dumps({'results': [DUMMY_EVENT]}))

        with patch.object(Event, '_make_request', return_value=response) as mock_request:
            events = Event.list()
            mock_request.assert_called_once_with('get', 'https://app.hypertrack.io/api/v1/events/', params={})
