# Sakha 🤖

Sakha is a friendly AI chatbot designed to help users improve their mood by suggesting personalized activities, setting reminders, and following up to track well-being.

[//]: # (🚀 **Try it here**  )

📖 **[Project Blog: Read about the implementation details here](https://rs-saran.github.io/projects/20250122_serene_solace_sakha/)**  

[//]: # (🎥 **Watch the demo**  )

## 🎯 Features
✅ **Personalized Activity Suggestions** – Recommends activities based on user preferences and feedback.  
✅ **Smart Reminders** – Helps users set up reminders for activities.  
✅ **Follow-ups & Feedback** – Checks in after an activity to see if it helped improve the user's mood.  
✅ **Crisis Support** – Provides helpline information if necessary.  
✅ **Seamless Conversations** – Engages naturally with users to support their well-being.  

## 🛠️ Technologies Used
- **LLM (LLaMA 3.3)** – Powers the chatbot’s responses and supervision.
- **LangGraph** – Manages structured conversation flows.
- **PostgreSQL** – Stores user info, reminders, feedback, and conversation checkpoints.
- **Flask** – Serves as a lightweight interface for user interaction.
- **Qdrant** - powers long term memory 
- **APScheduler** – Schedules and triggers reminders.

## 🚀 How to Run the App  
1️⃣ Clone the repository:  
   ```bash
   git clone https://github.com/your-repo/sakha.git
   cd sakha
   ```

2️⃣ Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3️⃣ Set up environment variables:  
- Copy the example `.env` file and fill in the required values:
   ```bash
   cp .env.example .env
   ```

4️⃣ Run the chatbot:  
   ```bash
   python main.py
   ```

5️⃣ Navigate to [http://localhost:8000/](http://localhost:8000/) to register and start chatting.


## ⚠️ Limitations

1. Responses depend on LLMs; edge cases may still exist.
2. Crisis handling is currently limited to providing a hardcoded helpline number.
3. No multilingual support yet—currently works only in English.

## 🔧 Future Improvements

1. **Cross session Memory:** Allow the chatbot to remember past interactions across sessions for more natural and engaging conversations
2. **Improved Reminder System:** Add features like recurring reminders, snooze options based on user availability.
3. **Deploy:** Deploy it to production after testing 

## 💡 Usage
- Start chatting with Sakha and receive activity suggestions.
- Set reminders for activities.
- Get follow-ups to track mood improvements.
- If needed, Sakha will provide crisis support information.

📃 **License**  
This project is licensed under the MIT License.  

📩 **Contact**  
For questions or feedback, contact [Sai Saran Reddy](mailto:rs.saran.reddy@gmail.com).
