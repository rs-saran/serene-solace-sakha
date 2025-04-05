# Sakha 🤖

Sakha is a friendly AI chatbot designed to help users improve their mood by suggesting personalized activities, setting reminders, and following up to track well-being.

[//]: # (🚀 **Try it here**  )

📖 **Read about the implementation details here [WIP]**  

[//]: # (🎥 **Watch the demo**  )

## 🎯 Features
✅ **Personalized Activity Suggestions** – Recommends activities based on user preferences.  
✅ **Smart Reminders** – Helps users set up reminders for activities.  
✅ **Follow-ups & Feedback** – Checks in after an activity to see if it helped improve the user's mood.  
✅ **Crisis Support** – Provides helpline information if necessary.  
✅ **Seamless Conversations** – Engages naturally with users to support their well-being.  

## 🛠️ Technologies Used
- **LLM (LLaMA 3.3-700B via Groq API)** – Powers the chatbot’s responses and supervision.
- **LangGraph** – Manages structured conversation flows.
- **PostgreSQL** – Stores user info, reminders, feedback, and conversation checkpoints.
- **Flask** – Serves as a lightweight interface for user interaction.
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

1. Crisis handling is currently limited to providing a hardcoded helpline number.
2. Activity suggestions are based on simple preferences and do not yet adapt dynamically over time.
3. No multilingual support yet—currently works only in English.
4. Chat flow switching is controlled by the backend rather than by the supervisor or Sakha, limiting flexibility in dynamically adjusting conversations based on user interactions.

## 🔧 Future Improvements

1. **Enhanced Personalization:** Improve activity recommendations by leveraging user history and behavioral patterns.  
2. **Cross session Memory:** Allow the chatbot to remember past interactions across sessions for more natural and engaging conversations
3. **Improved Reminder System:** Add features like recurring reminders, snooze options based on user availability.
4. **Dynamic Chat Flow control:** Enhance chat flow management by allowing dynamic switching based on user interactions rather than relying solely on backend control.

## 💡 Usage
- Start chatting with Sakha and receive activity suggestions.
- Set reminders for activities.
- Get follow-ups to track mood improvements.
- If needed, Sakha will provide crisis support information.

📃 **License**  
This project is licensed under the MIT License.  

📩 **Contact**  
For questions or feedback, contact [Sai Saran Reddy](mailto:rs.saran.reddy@gmail.com).
