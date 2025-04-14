import requests
import uuid
from requests.exceptions import RequestException
from fake_useragent import UserAgent
import re
from utils.translation import translate_text

def generate_pseudocode_from_logic(logic):
    try:
        # Translate the logic to English
        logic_in_english = translate_text(logic)  # Translate to English

        with requests.Session() as session:
            session.headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Host": "www.blackbox.ai",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Site": "same-origin",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f"{UserAgent.random}"
            }

            response = session.get('https://www.blackbox.ai/agent/Pseudofyk2iogPd', allow_redirects=True, verify=True)
            sessionId = session.cookies.get_dict().get('sessionId', None)

            if not sessionId:
                return ('error', 'Failed to retrieve sessionId')

            data = {
                "messages": [
                    {
                        "id": "ngWed8m7zBnTAb3BdFxZ7",
                        "content": f"\"{logic_in_english} without using function",
                        "role": "user"
                    }
                ],
                "id": "ngWed8m7zBnTAb3BdFxZ7",
                "previewToken": None,
                "userId": f"{uuid.uuid4()}",
                "codeModelMode": True,
                "agentMode": {
                    "mode": True,
                    "id": "Pseudofyk2iogPd",
                    "name": "Pseudofy"
                },
                "trendingAgentMode": {},
                "isMicMode": False,
                "isChromeExt": False,
                "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94",
                "githubToken": None
            }

            session.headers.update({
                "Referer": "https://www.blackbox.ai/agent/Pseudofyk2iogPd",
                "Content-Length": f"{len(str(data))}",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": "https://www.blackbox.ai",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Cookie": f"sessionId={sessionId};"
            })

            try:
                response2 = session.post('https://www.blackbox.ai/api/chat', json=data, allow_redirects=False, verify=True, timeout=10)
                response2.raise_for_status()  # Check for request errors
            except RequestException as e:
                return ('error', f'Error making POST request: {str(e)}')

            if '```' in response2.text:
                response_strings = re.search(r'```(.*?)```', response2.text, re.DOTALL)
                if response_strings:
                    result = response_strings.group(1).strip()

                    # Translate the pseudocode into English
                    translated_result = translate_text(result, 'en')

                    # Return translated pseudocode
                    return translated_result
                else:
                    return ('error', 'No valid pseudocode found in the response text.')
            else:
                return ('error', 'No pseudocode found in the response text.')

    except Exception as e:
        return ('error', f'An error occurred: {str(e)}')
