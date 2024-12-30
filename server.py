from flask import Flask, request, jsonify
from waitress import serve
from gc_1 import authenticate, add_event, parse_event
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/test_calendar', methods=['GET'])
def test_calendar():
    try:
        service = authenticate()
        calendar_list = service.calendarList().list().execute()
        num_calendars = len(calendar_list.get('items', []))
        return jsonify({
            "status": "success",
            "message": "Successfully authenticated with Google Calendar",
            "details": f"Found {num_calendars} calendars"
        })
    except Exception as e:
        logger.error("Calendar test error: %s", str(e), exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/add_calendar_event', methods=['POST'])
def handle_siri_request():
    logger.debug("Received request headers: %s", request.headers)
    logger.debug("Received request data: %s", request.get_data())
    
    try:
        # Verify content type
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 400

        # Get and log the raw request data
        data = request.get_json()
        logger.info("Parsed JSON data: %s", data)
        
        # Extract the command
        voice_command = data.get('command', {})
        logger.debug("Extracted command object: %s", voice_command)
        
        # Handle both string and dict command formats
        if isinstance(voice_command, dict):
            voice_command = next(iter(voice_command.values()), '')
        
        logger.info("Final voice command: %s", voice_command)
        
        # Validate command
        if not voice_command:
            return jsonify({
                "status": "error", 
                "message": "No command received"
            }), 400
        
        # Parse event details
        try:
            summary, start_time, end_time = parse_event(voice_command)
        except Exception as parse_error:
            logger.error("Error parsing event: %s", str(parse_error))
            return jsonify({
                "status": "error",
                "message": f"Failed to parse event details: {str(parse_error)}"
            }), 400
        
        # Validate parsed data
        if not all([summary, start_time, end_time]):
            return jsonify({
                "status": "error", 
                "message": "Could not parse event details - missing required information"
            }), 400
        
        # Add event to calendar
        try:
            add_event(summary, start_time, end_time)
            logger.info("Successfully added event: %s", summary)
            return jsonify({
                "status": "success", 
                "message": f"Added event: {summary}",
                "details": {
                    "summary": summary,
                    "start": start_time,
                    "end": end_time
                }
            })
        except Exception as calendar_error:
            logger.error("Error adding event to calendar: %s", str(calendar_error))
            return jsonify({
                "status": "error",
                "message": f"Failed to add event to calendar: {str(calendar_error)}"
            }), 500
            
    except Exception as e:
        logger.error("Unexpected error: %s", str(e), exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # For development
    # app.run(debug=True)
    
    # For production
    serve(app, host='0.0.0.0', port=8080)