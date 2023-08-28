# simple_api_test_codegen

Тул для генерации простых автотестов по cURL запроса.  
Тул генерирует класс клиент, файл conftest.py и простые тесты в директории test.  
Чтобы запустить, необходимо установить requirements.txt, набрать в терминале 

```shell
 git https://github.com/ValeriyMenshikov/simple_api_test_codegen
 cd simple_api_test_codegen
 pip install -r requirements.txt
```

Запустить файл main, например:
```python
from generator.generator import to_parse, generate_test_code, generate_conftest, generate_client, generate_method_code

if __name__ == '__main__':
    # Скопируй сюда свой cURL, например:
    curl = """
    curl -X 'POST' \
      'https://petstore.swagger.io/v2/pet' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "id": 0,
      "category": {
        "id": 0,
        "name": "string"
      },
      "name": "doggie",
      "photoUrls": [
        "string"
      ],
      "tags": [
        {
          "id": 0,
          "name": "string"
        }
      ],
      "status": "available"
    }'
    """
    parsed_command = to_parse(curl)
    client_code = generate_client(parsed_command)
    generate_method_code(parsed_command)
    code = generate_test_code(parsed_command)
    conftest_code = generate_conftest(parsed_command)
```

В корне директории сгенерируется два пакета, с тестами и клиентом.