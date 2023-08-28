from generator.generator import to_parse, generate_test_code, generate_conftest, generate_client, generate_method_code

if __name__ == '__main__':
    # Скопируй сюда свой cURL
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
