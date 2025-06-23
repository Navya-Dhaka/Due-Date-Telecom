from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the CSV file
df = pd.read_csv('data.csv')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    
    # Extract user ID from Dialogflow request
    user_id = req.get('queryResult', {}).get('parameters', {}).get('ID')
    
    # Look up the user in the CSV file
    user_data = df[df['ID'] == user_id]
    
    if not user_data.empty:
        due_date = user_data['DueDate'].values[0]
        amount_due = user_data['AmountDue'].values[0]
        
        response = {
            "fulfillmentText": f"Your due date is {due_date} and the amount due is {amount_due}."
        }
    else:
        response = {
            "fulfillmentText": "User ID not found."
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
