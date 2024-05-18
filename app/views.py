import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
    send_whatsapp_message,
    create_interactive_message, 
    FAQ_ANSWERS, 
    create_faqs_message_80C, 
    create_faqs_message_80CCC, 
    create_faqs_message_80CCD, 
    create_faqs_message_80D,
    send_whatsapp_message_text
)

webhook_blueprint = Blueprint("webhook", __name__)

def handle_message():
    body = request.get_json()
    # logging.info(f"request body: {body}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            sender_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            message_type = body["entry"][0]["changes"][0]["value"]["messages"][0]["type"]
            message_text = body["entry"][0]["changes"][0]["value"]["messages"][0].get("text", {}).get("body", "")
            print(message_type)

            if message_type == "text":
                if message_text.strip() == "\\default":
                    interactive_message = create_interactive_message()
                    send_whatsapp_message(interactive_message)
                else:
                    process_whatsapp_message(body)
            elif message_type == "interactive":
                interactive_response = body["entry"][0]["changes"][0]["value"]["messages"][0]["interactive"]
                print(interactive_response)
                list_reply_id = interactive_response.get("list_reply", {}).get("id")
                button_reply_id = interactive_response.get("button_reply", {}).get("id")

                selected_option = list_reply_id or button_reply_id
                print(selected_option)

                if selected_option == "section_80C":
                    print("under 80c")
                    faqs_message = create_faqs_message_80C()
                    send_whatsapp_message(faqs_message)
                elif selected_option == "section_80CCC":
                    faqs_message = create_faqs_message_80CCC()
                    send_whatsapp_message(faqs_message)
                elif selected_option == "section_80CCD":
                    faqs_message = create_faqs_message_80CCD()
                    send_whatsapp_message(faqs_message)
                elif selected_option == "section_80D":
                    faqs_message = create_faqs_message_80D()
                    send_whatsapp_message(faqs_message)
                elif selected_option in FAQ_ANSWERS:
                    print("Under selected options:")
                    answer_message = FAQ_ANSWERS[selected_option]()
                    print(answer_message)
                    send_whatsapp_message_text(answer_message)
                else:
                    print("Under this")
                    send_whatsapp_message_text({"type": "text", "text": {"body": "Sorry, I didn't understand that."}})

            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"status": "error", "message": "Not a WhatsApp API event"}), 404
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400





# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()


