import requests
import random
import hashlib
from config import BAIDU_APP_ID, BAIDU_SECRET_KEY  # Import configuration variables

def translate_sentence(original_sentence, target_language='jp'):
    """
    Translates the given sentence to the specified target language using Baidu Translate API.

    Args:
        original_sentence (str): The sentence to be translated.
        target_language (str, optional): The target language code. Defaults to 'jp'.

    Returns:
        str: The translated sentence.

    Raises:
        requests.exceptions.RequestException: If there is an error in sending the translation request.

    References:
        Baidu Translate API Documentation: https://fanyi-api.baidu.com/doc/21
    """
    
    appid = BAIDU_APP_ID  # Use appid from config.py
    secretKey = BAIDU_SECRET_KEY  # Use secretKey from config.py
    base_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    
    # Generate random number
    salt = random.randint(32768, 65536)
    # Generate signature
    sign = appid + original_sentence + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    
    # Build request parameters
    params = {
        'q': original_sentence,
        'from': 'auto',
        'to': target_language,
        'appid': appid,
        'salt': str(salt),
        'sign': sign
    }
    
    # Send request
    response = requests.get(base_url, params=params)
    print(response.json())
    
    # Parse response
    result = response.json()
    
    # Return translation result
    return result.get('trans_result', [{}])[0].get('dst', '')

# Example usage
if __name__ == "__main__":
    original_sentence = "请把土豆细切。"
    translated_sentence = translate_sentence(original_sentence)
    print("Translated Sentence:", translated_sentence)