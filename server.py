from flask import Flask, request, jsonify
from waitress import serve
# Import functions from your original script
from gc_1 import authenticate, add_event, parse_event

app = Flask(__name__)

@app.route('/add_calendar_event', methods=['POST'])
def handle_siri_request():
    try:
        # Debug logging
        print("Received request:")
        print(request.json)
        
        # Get the transcribed text from Siri
        voice_command = request.json.get('command')
        
        # Extract the actual command string from the nested dictionary
        if isinstance(voice_command, dict):
            voice_command = next(iter(voice_command.values()))  # Get the first value
        
        print(f"Extracted command: {voice_command}")
        
        if not voice_command:
            return jsonify({
                "status": "error", 
                "message": "No command received. Please provide a command in the format 'Event at time'"
            })
        
        # Use your existing parsing function
        summary, start_time, end_time = parse_event(voice_command)
        
        if summary and start_time and end_time:
            add_event(summary, start_time, end_time)
            return jsonify({
                "status": "success", 
                "message": f"Added event: {summary}",
                "details": {
                    "start": start_time,
                    "end": end_time
                }
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Could not parse event details. Please use format 'Event at time'"
            })
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"status": "success", "message": "Server is running!"})

if __name__ == '__main__':
    # Start ngrok
    from pyngrok import ngrok
    
    # Start http tunnel
    http_tunnel = ngrok.connect(8000)
    print(f'Public URL: {http_tunnel.public_url}')
    
    # Run server
    serve(app, host='0.0.0.0', port=8000)