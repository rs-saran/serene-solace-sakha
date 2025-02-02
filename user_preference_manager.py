import random

# User profiles dictionary
users = {
    "user_1": {
        "name": "Alice",
        "emotional_state": "Happy and content",
        "helpful_activities": ["Talking to someone", "Doing something creative"],
        "interests": ["Reading", "Crafting"],
        "suggestion_preference": "Relaxation or mindfulness exercises",
        "available_time": "15-30 minutes",
        "energy_peak": "Morning",
        "self_care_frequency": "Daily",
        "engagement_preference": "Sending daily check-ins",
        "motivational_quotes": "Yes, frequently"
    },
    "user_2": {
        "name": "Bob",
        "emotional_state": "Stressed or overwhelmed",
        "helpful_activities": ["Spending time outdoors", "Taking a break"],
        "interests": ["Exercising", "Exploring nature"],
        "suggestion_preference": "Physical activities or exercises",
        "available_time": "30-60 minutes",
        "energy_peak": "Afternoon",
        "self_care_frequency": "A few times a week",
        "engagement_preference": "Offering reminders based on my preferences",
        "motivational_quotes": "Yes, occasionally"
    },
    "user_3": {
        "name": "Charlie",
        "emotional_state": "Sad or low",
        "helpful_activities": ["Watching or reading something comforting", "Talking to someone"],
        "interests": ["Watching movies", "Learning new skills"],
        "suggestion_preference": "Entertainment recommendations",
        "available_time": "Less than 15 minutes",
        "energy_peak": "Evening",
        "self_care_frequency": "Occasionally",
        "engagement_preference": "Responding only when I initiate the chat",
        "motivational_quotes": "No, I don’t find them helpful"
    },
    "user_4": {
        "name": "Diana",
        "emotional_state": "Calm and relaxed",
        "helpful_activities": ["Meditating", "Practicing mindfulness"],
        "interests": ["Crafting", "Exploring nature"],
        "suggestion_preference": "Relaxation or mindfulness exercises",
        "available_time": "More than an hour",
        "energy_peak": "Night",
        "self_care_frequency": "Rarely",
        "engagement_preference": "Occasionally suggesting activities or tips",
        "motivational_quotes": "Yes, occasionally"
    },
    "user_5": {
        "name": "Ethan",
        "emotional_state": "Energetic and motivated",
        "helpful_activities": ["Learning new things", "Exercising"],
        "interests": ["Playing sports", "Learning or trying new things"],
        "suggestion_preference": "Activities to boost your mood",
        "available_time": "30-60 minutes",
        "energy_peak": "Morning",
        "self_care_frequency": "Daily",
        "engagement_preference": "Sending daily check-ins",
        "motivational_quotes": "Yes, frequently"
    }
}

# Function to return a random user profile
def get_random_user():
    return random.choice(list(users_dict.values()))


