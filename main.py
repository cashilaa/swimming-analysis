from flask import Flask, request, jsonify
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("No OpenAI API key found in environment variables")

def generate_analysis(swimmer_data):
    comprehensive_feedback_prompt = f""" 
    As a professional swim coach, analyze the performance of Swimmer {swimmer_data['name']} and provide guidance for four distinct periods: First Form Freestyle, First Period Recovery, Second Form Freestyle, and Second Period Recovery.

    Base your analysis on these metrics:
    - Lap times: {swimmer_data['lap_times']}
    - Stroke counts: {swimmer_data['stroke_counts']}
    - Breath counts: {swimmer_data['breath_counts']}
    - Splits: {swimmer_data['splits']}
    - DPS (Distance Per Stroke): {swimmer_data['dps']}

    Provide a structured analysis following this exact format for each period, ensuring valid JSON output:
    {{
        "first_form_freestyle": {{
            "start_time": "0:00",
            "end_time": "5:00",
            "observations": "Brief analysis of freestyle form",
            "spirit_guidance": "Mental feedback",
            "technique_guidance": "Technical advice",
            "speed_guidance": "Pace recommendations",
            "metrics_analysis": "Metrics evaluation"
        }},
        "first_period_recovery": {{
            "start_time": "5:00",
            "end_time": "10:00",
            "observations": "Recovery observations",
            "spirit_guidance": "Mental guidance",
            "technique_guidance": "Recovery recommendations",
            "energy_management": "Energy strategies",
            "breathing_analysis": "Breathing patterns"
        }},
        "second_form_freestyle": {{
            "start_time": "10:00",
            "end_time": "15:00",
            "observations": "Freestyle form analysis",
            "spirit_guidance": "Mental feedback",
            "technique_guidance": "Technical advice",
            "speed_guidance": "Pace recommendations",
            "metrics_analysis": "Metrics evaluation"
        }},
        "second_period_recovery": {{
            "start_time": "15:00",
            "end_time": "20:00",
            "observations": "Recovery observations",
            "spirit_guidance": "Mental guidance",
            "technique_guidance": "Recovery recommendations",
            "energy_management": "Energy strategies",
            "breathing_analysis": "Breathing patterns"
        }}
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional swim coach providing structured analysis for freestyle swimming and recovery periods. Ensure all responses are in valid JSON format."},
                {"role": "user", "content": comprehensive_feedback_prompt}
            ]
        )
        
        analysis_text = response.choices[0].message.content
        analysis_json = json.loads(analysis_text)
        return analysis_json
        
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON parsing error: {str(e)}")
        raise Exception("Error parsing analysis response")
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        raise

def validate_data(data):
    """Validate incoming data"""
    required_fields = ['name', 'lap_times', 'stroke_counts', 'breath_counts', 'splits', 'dps']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data['lap_times'], list) or not all(isinstance(x, (int, float)) for x in data['lap_times']):
        raise ValueError("lap_times must be a list of numbers")
    
    if not isinstance(data['stroke_counts'], list) or not all(isinstance(x, (int, float)) for x in data['stroke_counts']):
        raise ValueError("stroke_counts must be a list of numbers")
    
    if not isinstance(data['breath_counts'], list) or not all(isinstance(x, (int, float)) for x in data['breath_counts']):
        raise ValueError("breath_counts must be a list of numbers")
    
    if not isinstance(data['splits'], list) or not all(isinstance(x, (int, float)) for x in data['splits']):
        raise ValueError("splits must be a list of numbers")
    
    if not isinstance(data['dps'], list) or not all(isinstance(x, (int, float)) for x in data['dps']):
        raise ValueError("dps must be a list of numbers")

@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'status': 'error'
            }), 400
            
        try:
            validate_data(data)
        except ValueError as e:
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 400

        analysis = generate_analysis(data)
        
        response_data = {
            'status': 'success',
            'data': {
                'swimmer_name': data['name'],
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'session_info': {
                    'group_number': data.get('group_number'),
                    'club_name': data.get('club_name'),
                    'event_date': data.get('event_date'),
                    'session_type': 'freestyle_and_recovery'
                }
            }
        }
        
        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'details': 'An error occurred while processing the request'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
