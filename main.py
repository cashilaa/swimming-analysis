from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY', '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')

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
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)

@app.route('/api/analyze-performance', methods=['POST'])
def analyze_performance():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'lap_times', 'stroke_counts', 'breath_counts', 'splits', 'dps']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
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
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)