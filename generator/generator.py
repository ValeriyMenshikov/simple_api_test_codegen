import curlparser
from collections import namedtuple
import inflection
import pathlib
import re
import json


def parse_url(url):
    pattern = r'^((?:https?|ftp):\/\/)?([^\/\s]+)(.*)$'
    match = re.match(pattern, url)

    if match:
        service_name = match.group(2)
        base_url = match.group(1) + match.group(2)
        endpoint = match.group(3)
        return service_name, base_url, endpoint
    else:
        return None, None, None


def to_parse(curl):
    params = curlparser.parse(curl)
    service_name, base_url, endpoint = parse_url(params.url)
    result = params._asdict()
    result.update(
        dict(
            path=endpoint,
            service_name=re.sub(r'[ ()-/.]', '_', service_name),
            base_url=base_url,
            endpoint=endpoint.replace('/', '_')[1:],
            json=json.dumps(json.loads(params.data or '{}'), indent=4),
            header=dict(params.header),
            method=inflection.underscore(params.method),
        )
    )
    parsed_command = namedtuple('ParserCommand', result.keys())(*result.values())
    return parsed_command


def write_test_code(parsed_command, code):
    base_path = pathlib.Path(__file__)
    tests_folder = base_path.parent.joinpath('tests')
    tests_folder.mkdir(parents=True, exist_ok=True)
    tests_folder.joinpath('__init__.py').touch(exist_ok=True)
    test_file = f'test_{parsed_command.method}_{parsed_command.endpoint}.py'

    with open(tests_folder.joinpath(test_file), 'a+') as file:
        file.write(code)


def generate_conftest(parsed_command):
    service_name = inflection.camelize(parsed_command.service_name)
    headers = {k: v.strip() for k, v in parsed_command.header.items()}
    conftest_template = f"""import pytest
from client.{parsed_command.service_name} import {service_name}
    
    
@pytest.fixture
def client():
    host = '{parsed_command.base_url}'
    headers = {headers}
    return {service_name}(host=host, headers=headers)
    """

    base_path = pathlib.Path(__file__).parent.joinpath('tests')
    base_path.mkdir(parents=True, exist_ok=True)
    conftest_file = base_path.joinpath('conftest.py')
    if not conftest_file.is_file():
        with open(conftest_file, 'w') as file:
            file.write(conftest_template)

    return conftest_template


def generate_client(parsed_command):
    client_template = f"""from requests import session
    
    
class {inflection.camelize(parsed_command.service_name)}:
    def __init__(self, host='{parsed_command.base_url}', headers=None):
        self.host = host
        self.session = session()
        if headers:
            self.session.headers.update(headers)
    """

    base_path = pathlib.Path(__file__)
    client_path = base_path.parent.joinpath('client')
    client_path.mkdir(parents=True, exist_ok=True)
    client_path.joinpath('__init__.py').touch(exist_ok=True)
    client = client_path.joinpath(f'{parsed_command.service_name}.py')
    if not client.is_file():
        with open(client, 'w') as file:
            file.write(client_template)
    return client_template


def generate_method_code(parsed_command):
    template = f"""
    # Отредактируй метод при необходимости
    def {parsed_command.method}_{parsed_command.endpoint}(self, **kwargs):
        response = self.session.{parsed_command.method}(f'{{self.host}}{parsed_command.path}', **kwargs)
        return response
        
"""
    base_path = pathlib.Path(__file__)
    client_path = base_path.parent.joinpath('client')
    client_path.mkdir(parents=True, exist_ok=True)
    client_path.joinpath('__init__.py').touch(exist_ok=True)
    client = client_path.joinpath(f'{parsed_command.service_name}.py')
    if client.is_file():
        with open(client, 'a') as file:
            file.write(template)

    return template


def generate_test_code(parsed_command):
    method = parsed_command.method
    endpoint = parsed_command.endpoint
    json = parsed_command.json

    template = f"""
def test_{method}_{endpoint}(client):
    # При необходимости удали или добавь нужные параметры и передай в метод
    json = {json}
    response = client.{method}_{endpoint}(json=json)
    assert 200 <= response.status_code < 300, "Статус код не соответствует ожидаемым"
"""

    base_path = pathlib.Path(__file__)
    tests_folder = base_path.parent.joinpath('tests')
    tests_folder.mkdir(parents=True, exist_ok=True)
    tests_folder.joinpath('__init__.py').touch(exist_ok=True)
    test_file = tests_folder.joinpath(f'test_{parsed_command.method}_{parsed_command.endpoint}.py')
    if test_file.is_file():
        mode = 'a+'
    else:
        mode = 'w'
    with open(tests_folder.joinpath(test_file), mode) as file:
        file.write(template)

    return template
