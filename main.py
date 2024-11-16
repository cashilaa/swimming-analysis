from flask import Flask, request, jsonify
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("No OpenAI API key found in environment variables")

def generate_analysis(swimmer_data):
    comprehensive_feedback_prompt = f""" 
    As a professional swim coach, analyze the performance of Swimmer {swimmer_data['name']} and provide guidance for four distinct periods: First Form Freestyle, First Period Recovery, Second Form Freestyle, and Second Period Recovery.

    The response should be in this exact JSON structure:
    {{
        "first_form_freestyle": {{
            "start_time": "Time period start",
            "end_time": "Time period end",
            "observations": "General observations about the freestyle form",
            "spirit_guidance": "Mental and motivational feedback for freestyle",
            "technique_guidance": "Technical swimming advice specific to freestyle",
            "speed_guidance": "Pace and speed recommendations",
            "metrics_analysis": "Analysis of stroke count, DPS, and other metrics"
        }},
        "first_period_recovery": {{
            "start_time": "Time period start",
            "end_time": "Time period end",
            "observations": "General observations about recovery",
            "spirit_guidance": "Mental guidance during recovery",
            "technique_guidance": "Recovery technique recommendations",
            "energy_management": "Energy conservation and recovery strategies",
            "breathing_analysis": "Analysis of breathing patterns during recovery"
        }},
        "second_form_freestyle": {{
            "start_time": "Time period start",
            "end_time": "Time period end",
            "observations": "General observations about the freestyle form",
            "spirit_guidance": "Mental and motivational feedback for freestyle",
            "technique_guidance": "Technical swimming advice specific to freestyle",
            "speed_guidance": "Pace and speed recommendations",
            "metrics_analysis": "Analysis of stroke count, DPS, and other metrics"
        }},
        "second_period_recovery": {{
            "start_time": "Time period start",
            "end_time": "Time period end",
            "observations": "General observations about recovery",
            "spirit_guidance": "Mental guidance during recovery",
            "technique_guidance": "Recovery technique recommendations",
            "energy_management": "Energy conservation and recovery strategies",
            "breathing_analysis": "Analysis of breathing patterns during recovery"
        }}
    }}

    Base your analysis on these metrics:
    - Lap times: {swimmer_data['lap_times']}
    - Stroke counts: {swimmer_data['stroke_counts']}
    - Breath counts: {swimmer_data['breath_counts']}
    - Splits: {swimmer_data['splits']}
    - DPS (Distance Per Stroke): {swimmer_data['dps']}

    Consider the following in your analysis:
    1. For Freestyle periods:
       - Focus on stroke efficiency and form
       - Analyze speed variations and consistency
       - Evaluate technique maintenance under fatigue
    
    2. For Recovery periods:
       - Assess effectiveness of recovery techniques
       - Analyze breathing patterns and their impact
       - Evaluate energy conservation strategies
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional swim coach providing structured analysis for freestyle swimming and recovery periods."},
                {"role": "user", "content": comprehensive_feedback_prompt}
            ],
            timeout=30 
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        app.logger.error(f"OpenAI API error: {str(e)}")
        raise Exception("Error generating analysis")
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
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
