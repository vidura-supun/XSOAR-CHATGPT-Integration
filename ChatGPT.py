'''
Author: purpleXsec
Github: https://github.com/vidura-supun

'''

import json
import requests

QUESTION_OUTPUT_PREFIX = 'Phrase'

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member


class Client(BaseClient):
    def __init__(self, api_key: str, base_url: str, proxy: bool, verify: bool):
        super().__init__(base_url=base_url, proxy=proxy, verify=verify)
        self.api_key = api_key

        if self.api_key:
            self._headers = {'Authorization': self.api_key, 'Content-Type': 'application/json'}

    def question(self, text: str, tokens: int):
        return self._http_request(method='POST',url_suffix='/v1/completions', json_data={"model": "text-davinci-003", "prompt": text, "temperature": 0, "max_tokens": int(tokens)}, resp_type='json', ok_codes=(200,))


def test_module(client: Client) -> str:
    """
    Tests API connectivity and authentication'

    Returning 'ok' indicates that connection to the service is successful.
    Raises exceptions if something goes wrong.
    """

    try:
        response = client.question('hi ChatGPT', 50)
        ##success = demisto.get(response, 'choices.[0].text')  # Safe access to response['success']['total']
        test = response['choices'][0]['text']
        if test is None:
            return f'No Results Returned'

        return 'ok'

    except Exception as e:
        exception_text = str(e).lower()
        if 'forbidden' in exception_text or 'authorization' in exception_text:
            return 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e


def user_question(client: Client, text: str, tokens: int) -> CommandResults:
    if not text:
        raise DemistoException('the text argument cannot be empty.')

    response = client.question(text, tokens)
    answer = response['choices'][0]['text']

    if answer is None:
        raise DemistoException('Question failed: the response from server did not include `answer`.',
                               res=response)

    output = {'Question': text, 'Answer': answer}

    return CommandResults(outputs_prefix='ChatGPT',
                          outputs_key_field=f'{QUESTION_OUTPUT_PREFIX}.Original',
                          outputs={QUESTION_OUTPUT_PREFIX: output},
                          raw_response=response,
                          readable_output=tableToMarkdown(name='ChatGPT Answers...', t=output))

def main() -> None:
    params = demisto.params()
    args = demisto.args()
    command = demisto.command()

    api_key = params.get('apikey', {}).get('password')
    base_url = params.get('url', '')
    verify = not params.get('insecure', False)
    proxy = params.get('proxy', False)

    demisto.debug(f'Command being called is {command}')
    try:
        client = Client(api_key=api_key, base_url=base_url, verify=verify, proxy=proxy)

        if command == 'test-module':
            # This is the call made when clicking the integration Test button.
            return_results(test_module(client))

        elif command == 'user-question':
            return_results(user_question(client, **args))

        else:
            raise NotImplementedError(f"command {command} is not implemented.")

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error("\n".join(("Failed to execute {command} command.",
                                "Error:",
                                str(e))))


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()