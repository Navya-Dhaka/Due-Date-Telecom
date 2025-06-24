from flask import Flask, request, jsonify
import pandas as pd
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load the CSV file
df = pd.read_csv('data.csv')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    logging.debug(f"Received request JSON: {req}")

    tag = req.get('fulfillmentInfo', {}).get('tag')
    params = req.get('sessionInfo', {}).get('parameters', {})
    user_id = params.get('id_number')
    user_name = params.get('name')

    logging.debug(f"Tag: {tag}, ID: {user_id}, Name: {user_name}")

    user_data = df[(df['ID'] == user_id) & (df['Name'].str.lower() == user_name.lower())]

    if user_data.empty:
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": ["We couldn't find a matching record for the provided ID and name. Please re-enter your details."]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "user_found": False,
                    "received_ID_number": user_id,
                    "received_name": user_name
                }
            }
        })

    # User is authenticated
    if tag == 'authenticate_user':
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": ["User authenticated successfully."]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "user_found": True,
                    "received_ID_number": user_id,
                    "received_name": user_name
                }
            }
        })

    elif tag == 'get_due_date':
        due_date = user_data['Due Date'].values[0]
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": [f"Your due date is {due_date}."]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "due_date": str(due_date)
                }
            }
        })

    elif tag == 'get_amount_due':
        amount_due = user_data['Amount'].values[0]
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": [f"The amount you have to pay is {amount_due} dollars."]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "amount_due": float(amount_due)
                }
            }
        })

    elif tag == 'get_negative_reason':
        amount_due = user_data['Amount'].values[0]
        why_negative = user_data['Why Negative'].values[0]
        if amount_due < 0 and pd.notna(why_negative) and str(why_negative).strip():
            message = f"The reason for your negative balance is: {why_negative}."
        else:
            message = "You do not have a negative balance."
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": [message]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "why_negative": why_negative
                }
            }
        })

    elif tag == 'get_plan_type':
        plan_type = user_data['Plan'].values[0]
        return jsonify({
            "fulfillment_response": {
                "messages": [
                    {"text": {"text": [f"Your plan type is {plan_type}."]}}
                ]
            },
            "session_info": {
                "parameters": {
                    "plan_type": plan_type
                }
            }
        })

    # else:
    #     return jsonify({
    #         "fulfillment_response": {
    #             "messages": [
    #                 {"text": {"text": ["Unknown request type."]}}
    #             ]
    #         }
    #     })

if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, request, jsonify
# import pandas as pd
# import logging

# app = Flask(__name__)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# # Load the CSV file
# df = pd.read_csv('data.csv')

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     req = request.get_json(silent=True, force=True)
#     logging.debug(f"Received request JSON: {req}")

#     # Extract parameters from Dialogflow CX request
#     params = req.get('sessionInfo', {}).get('parameters', {})
#     user_id = params.get('id_number')
#     user_name = params.get('name')

#     logging.debug(f"Extracted parameters - ID_number: {user_id}, name: {user_name}")

#     # Look up the user in the CSV file
#     user_data = df[(df['ID'] == user_id) & (df['Name'].str.lower() == user_name.lower())]

#     if not user_data.empty:
#         due_date = user_data['Due Date'].values[0]
#         amount_due = user_data['Amount'].values[0]
#         why_negative = user_data['Why Negative'].values[0]

#         # Build the message conditionally
#         message = f"Your due date is {due_date} and the amount due is {amount_due}."
#         if pd.notna(why_negative) and str(why_negative).strip():
#             message += f" The reason for your negative balance is: {why_negative}."

    
#         response = {
#             "fulfillment_response": {
#                 "messages": [
#                     {
#                         "text": {
#                             "text": [message]
#                         }
#                     }
#                 ]
#             },

#             "session_info": {
#                 "parameters": {
#                     "user_found": True,
#                     "due_date": str(due_date),
#                     "amount_due": float(amount_due),
#                     "why_negative": why_negative,
#                     "received_ID_number": user_id,
#                     "received_name": user_name
#                 }
#             }
#         }
#     else:
#         response = {
#             "fulfillment_response": {
#                 "messages": [
#                     {
#                         "text": {
#                             "text": ["We couldn't find a matching record for the provided ID and name. Please re-enter your details."]
#                         }
#                     }
#                 ]
#             },
#             "session_info": {
#                 "parameters": {
#                     "user_found": False,
#                     "received_ID_number": user_id,
#                     "received_name": user_name
#                 }
#             }
#         }

#     return jsonify(response)

# if __name__ == '__main__':
#     app.run(debug=True)

