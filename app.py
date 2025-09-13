from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import register_user, verify_otp, cast_vote, has_voted, get_results, get_candidates
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Twilio configuration
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar')
        mobile = request.form.get('mobile')
        
        # Validate input
        if not aadhaar or not mobile:
            return render_template('register.html', error='Aadhaar and mobile are required')
        
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return render_template('register.html', error='Invalid Aadhaar number')
        
        if len(mobile) != 10 or not mobile.isdigit():
            return render_template('register.html', error='Invalid mobile number')
        
        # Register user and send OTP
        otp = register_user(aadhaar, mobile)
        
        if not otp:
            return render_template('register.html', error='Failed to send OTP. Please try again.')
        
        # Store user info in session
        session['aadhaar'] = aadhaar
        session['mobile'] = mobile
        
        return redirect(url_for('otp_verification'))
    
    return render_template('register.html')

@app.route('/otp', methods=['GET', 'POST'])
def otp_verification():
    """OTP verification"""
    if 'aadhaar' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        aadhaar = session['aadhaar']
        
        if verify_otp(aadhaar, otp):
            session['verified'] = True
            return redirect(url_for('vote'))
        else:
            return render_template('otp.html', mobile=session['mobile'][-4:], error='Invalid OTP')
    
    return render_template('otp.html', mobile=session['mobile'][-4:])

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    """Voting page"""
    if 'verified' not in session:
        return redirect(url_for('register'))
    
    aadhaar = session['aadhaar']
    
    # Check if user has already voted
    if has_voted(aadhaar):
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        candidate_id = request.form.get('candidate')
        if cast_vote(aadhaar, candidate_id):
            return redirect(url_for('confirmation'))
        else:
            return render_template('vote.html', candidates=get_candidates(), error='Vote casting failed')
    
    return render_template('vote.html', candidates=get_candidates())

@app.route('/confirmation')
def confirmation():
    """Vote confirmation page"""
    if 'verified' not in session:
        return redirect(url_for('register'))
    
    return render_template('confirmation.html')

@app.route('/results')
def results():
    """Results page"""
    results = get_results()
    candidates = get_candidates()
    
    # Prepare data for display
    candidate_results = []
    for candidate in candidates:
        candidate_results.append({
            'id': candidate['id'],
            'name': candidate['name'],
            'party': candidate['party'],
            'symbol': candidate['symbol'],
            'votes': results.get(candidate['id'], 0)
        })
    
    # Sort by votes
    candidate_results.sort(key=lambda x: x['votes'], reverse=True)
    
    return render_template('results.html', results=candidate_results)

@app.route('/api/candidates')
def api_candidates():
    """API endpoint for candidates"""
    return jsonify(get_candidates())

@app.route('/api/results')
def api_results():
    """API endpoint for results"""
    return jsonify(get_results())

if __name__ == '__main__':
    app.run(debug=True)