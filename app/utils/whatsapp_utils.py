import logging
from flask import current_app, jsonify
import json
import requests
from app.services.openai_out import getanswer
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


# def generate_response(response):
#     # Return text in uppercase
#     return response.upper()


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]
    message_type = body["entry"][0]["changes"][0]["value"]["messages"][0]["type"]

    # response = generate_response(message_body)

    # OpenAI Integration
    response = getanswer(message_body)
    response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    if message_type == "text":
        send_message(data)
    else:
        send_whatsapp_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


def send_whatsapp_message(info):
    ACCESS_TOKEN = current_app.config['ACCESS_TOKEN']
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    print(ACCESS_TOKEN)
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    print(current_app.config['RECIPIENT_WAID'])

    data = {
        "messaging_product": "whatsapp",
        "to" : current_app.config['RECIPIENT_WAID'],
        "type": info["type"],
        "interactive": info.get("interactive", {}),
    }
    print(data)
    try:
        response = requests.post(
            url, json=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response
    
def send_whatsapp_message_text(info):
    ACCESS_TOKEN = current_app.config['ACCESS_TOKEN']
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    print(ACCESS_TOKEN)
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    print(current_app.config['RECIPIENT_WAID'])

    data = {
        "messaging_product": "whatsapp",
        "to" : current_app.config['RECIPIENT_WAID'],
        "type": info["type"],
        "text": info.get("text", {}),
    }
    print(data)
    try:
        response = requests.post(
            url, json=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def create_interactive_message():
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Choose from below option or enter your query in textbox"
            },
            "body": {
                "text": "Please choose an option:"
            },
            "action": {
                "button": "Choose",
                "sections": [
                    {
                        "title": "Tax Sections",
                        "rows": [
                            {
                                "id": "section_80C",
                                "title": "80C",
                                "description": "FAQs about Section 80C"
                            },
                            {
                                "id": "section_80CCC",
                                "title": "80CCC",
                                "description": "FAQs about Section 80CCC"
                            },
                            {
                                "id": "section_80CCD",
                                "title": "80CCD",
                                "description": "FAQs about Section 80CCD"
                            },
                            {
                                "id": "section_80D",
                                "title": "80D",
                                "description": "FAQs about Section 80D"
                            }
                        ]
                    }
                ]
            }
        },
    }

def create_faqs_message_80C():
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Choose from below option or enter your query in textbox"
            },
            "body": {
                "text": "Please choose an option:"
            },
            "action": {
                "button": "Choose",
                "sections": [
                    {
                        "title": "Tax Section 80C",
                        "rows": [
                            {
                                "id": "section_80C1",
                                "title": "Deduction limit"
                            },
                            {
                                "id": "section_80C2",
                                "title": "Eligibility"
                            },
                            {
                                "id": "section_80C3",
                                "title": "Coverage under 80C"
                            }
                        ]
                    }
                ]
            }
        },
    }

def create_faqs_message_80CCC():
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Choose from below option or enter your query in textbox"
            },
            "body": {
                "text": "Please choose an option:"
            },
            "action": {
                "button": "Choose",
                "sections": [
                    {
                        "title": "Tax Section 80CCC FAQs",
                        "rows": [
                            {
                                "id": "section_80CCC1",
                                "title": "Eligibility"
                            },
                            {
                                "id": "section_80CCC2",
                                "title": "How much Claimable"
                            }
                        ]
                    }
                ]
            }
        }
    }



def create_faqs_message_80CCD():
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Choose from below option or enter your query in textbox"
            },
            "body": {
                "text": "Please choose an option:"
            },
            "action": {
                "button": "Choose",
                "sections": [
                    {
                        "title": "Tax Section 80CCD FAQs",
                        "rows": [
                            {
                                "id": "section_80CCD1",
                                "title": "What is Section 80CCD?"
                            },
                            {
                                "id": "section_80CCD2",
                                "title": "How much can I claim?"
                            }
                        ]
                    }
                ]
            }
        }
    }

def create_faqs_message_80D():
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Choose from below option or enter your query in textbox"
            },
            "body": {
                "text": "Please choose an option:"
            },
            "action": {
                "button": "Choose",
                "sections": [
                    {
                        "title": "Tax Section 80D FAQs",
                        "rows": [
                            {
                                "id": "section_80D1",
                                "title": "What is Section 80D?"
                            },
                            {
                                "id": "section_80D2",
                                "title": "Deduction limit?"
                            }
                        ]
                    }
                ]
            }
        }
    }


def create_faq_answer_80C_1():
    return {
        "type": "text",
        "text": {
            "body": "The deduction limit under Section 80C is Rs 1.5 lakhs per financial year."
        }
    }

def create_faq_answer_80C_2():
    return {
        "type": "text",
        "text": {
            "body": "Eligibility for Section 80C includes individuals and HUFs. Investments must be made in specified financial products."
        }
    }

def create_faq_answer_80C_3():
    return {
        "type": "text",
        "text": {
            "body": "Section 80C covers investments in PPF, NSC, life insurance premiums, ELSS, etc."
        }
    }

def create_faq_answer_80CCC_1():
    return {
        "type": "text",
        "text": {
            "body": "Any individual who has paid premium for annuity plan of LIC or other insurer can claim deduction under Section 80CCC."
        }
    }

def create_faq_answer_80CCC_2():
    return {
        "type": "text",
        "text": {
            "body": "You can claim up to Rs 1.5 lakhs under Section 80CCC. This limit is part of the overall limit of Section 80C."
        }
    }

def create_faq_answer_80CCD_1():
    return {
        "type": "text",
        "text": {
            "body": "Section 80CCD allows deduction for contributions made to the NPS and Atal Pension Yojana."
        }
    }

def create_faq_answer_80CCD_2():
    return {
        "type": "text",
        "text": {
            "body": "You can claim deduction up to 10% of salary (for employees) or 20% of gross income (for self-employed) under Section 80CCD."
        }
    }

def create_faq_answer_80D_1():
    return {
        "type": "text",
        "text": {
            "body": "Section 80D allows deduction for premiums paid for medical insurance for self, family, and parents."
        }
    }

def create_faq_answer_80D_2():
    return {
        "type": "text",
        "text": {
            "body": "The deduction limit under Section 80D is Rs 25,000 for self, spouse, and children, and an additional Rs 25,000 for parents."
        }
    }


FAQ_ANSWERS = {
    "section_80C1": create_faq_answer_80C_1,
    "section_80C2": create_faq_answer_80C_2,
    "section_80C3": create_faq_answer_80C_3,
    "section_80CCC1": create_faq_answer_80CCC_1,
    "section_80CCC2": create_faq_answer_80CCC_2,
    "section_80CCD1": create_faq_answer_80CCD_1,
    "section_80CCD2": create_faq_answer_80CCD_2,
    "section_80D1": create_faq_answer_80D_1,
    "section_80D2": create_faq_answer_80D_2
}
