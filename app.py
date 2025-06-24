from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the CSV file
df = pd.read_csv('data.csv')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    # Extract parameters from Dialogflow CX request
    params = req.get('sessionInfo', {}).get('parameters', {})
    user_id = params.get('ID_number')
    user_name = params.get('name')

    # Look up the user in the CSV file
    user_data = df[(df['ID'] == user_id) & (df['Name'].str.lower() == user_name.lower())]

    if not user_data.empty:
        due_date = user_data['Due Date'].values[0]
        amount_due = user_data['Amount'].values[0]
        why_negative = user_data['Why Negative'].values[0]

        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [
                                f"Your due date is {due_date}, the amount due is {amount_due}, and the reason for negative balance is: {why_negative}."
                            ]
                        }
                    }
                ]
            },
            "session_info": {
                "parameters": {
                    "user_found": True,
                    "due_date": str(due_date),
                    "amount_due": float(amount_due),
                    "why_negative": why_negative
                }
            }
        }
    else:
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["We couldn't find a matching record for the provided ID and name."]
                        }
                    }
                ]
            },
            "session_info": {
                "parameters": {
                    "user_found": False
                }
            }
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
