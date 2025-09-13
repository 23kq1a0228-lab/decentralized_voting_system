from pymongo import MongoClient
from datetime import datetime
import random
import string
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('mongodb+srv://23kq1a0228_db_user:1234@cluster0.gmgtxql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
try:
    print("Databases:", client.list_database_names())
except Exception as e:
    print("MongoDB connection failed:", e)
db = client['voting_system']
users_collection = db['users']
votes_collection = db['votes']

# Twilio configuration
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

# Create indexes for better performance
users_collection.create_index("aadhaar", unique=True)
votes_collection.create_index("aadhaar", unique=True)

def generate_otp():
    """Generate a 4-digit OTP"""
    return ''.join(random.choices(string.digits, k=4))

def send_otp_via_sms(mobile, otp):
    """Send OTP via SMS using Twilio"""
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP for voting system is: {otp}. Valid for 5 minutes.",
            from_=twilio_phone_number,
            to=f"+91{mobile}"  # Assuming Indian numbers
        )
        print(f"OTP sent successfully to {mobile}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")
        return False

def register_user(aadhaar, mobile):
    """Register a new user or update existing user"""
    existing_user = users_collection.find_one({'aadhaar': aadhaar})
    
    # Generate OTP
    otp = generate_otp()
    
    if existing_user:
        # Update existing user with new OTP
        users_collection.update_one(
            {'aadhaar': aadhaar},
            {'$set': {'mobile': mobile, 'otp': otp, 'otp_created_at': datetime.utcnow()}}
        )
    else:
        # Create new user
        user = {
            'aadhaar': aadhaar,
            'mobile': mobile,
            'otp': otp,
            'otp_created_at': datetime.utcnow(),
            'registered_at': datetime.utcnow()
        }
        users_collection.insert_one(user)
    
    # Send OTP via SMS
    success = send_otp_via_sms(mobile, otp)
    return otp if success else None

def verify_otp(aadhaar, otp):
    """Verify OTP for a user"""
    user = users_collection.find_one({'aadhaar': aadhaar})
    if user and user.get('otp') == otp:
        # Clear OTP after successful verification
        users_collection.update_one(
            {'aadhaar': aadhaar},
            {'$unset': {'otp': '', 'otp_created_at': ''}}
        )
        return True
    return False

def has_voted(aadhaar):
    """Check if user has already voted"""
    return votes_collection.find_one({'aadhaar': aadhaar}) is not None

def cast_vote(aadhaar, candidate_id):
    """Record a vote"""
    if has_voted(aadhaar):
        return False
    
    vote = {
        'aadhaar': aadhaar,
        'candidateId': candidate_id,
        'timestamp': datetime.utcnow(),
        'blockHash': ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    }
    votes_collection.insert_one(vote)
    return True

def get_results():
    """Get voting results"""
    pipeline = [
        {'$group': {'_id': '$candidateId', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    results = list(votes_collection.aggregate(pipeline))
    
    # Format results
    formatted_results = {}
    for result in results:
        formatted_results[result['_id']] = result['count']
    
    return formatted_results

def get_candidates():
    """Get list of candidates"""
    return [
        {"id": "1", "name": "Rahul Gandhi", "party": "Indian National Congress", "symbol": "Hand"},
        {"id": "2", "name": "Narendra Modi", "party": "Bharatiya Janata Party", "symbol": "Lotus"},
        {"id": "3", "name": "Mamata Banerjee", "party": "All India Trinamool Congress", "symbol": "Flowers"},
        {"id": "4", "name": "Amit Shah", "party": "Bharatiya Janata Party", "symbol": "Helicopter"}
    ]