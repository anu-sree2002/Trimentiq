import streamlit as st
import pandas as pd
import plotly.express as px
import json
import time
from groq import Groq

st.set_page_config(page_title="TriMentIQ | Aptitude Test", layout="centered", page_icon="🧠")
client = Groq(api_key=st.secrets["groq_api_key"])

# Session Initialization
sections = ["quantitative", "logical", "verbal"]
section_display_names = {
    "quantitative": "Quantitative Reasoning",
    "logical": "Logical Reasoning",
    "verbal": "Verbal Reasoning"
}
for key, default in {
    "page": "intro",
    "test_started": False,
    "current_section_index": 0,
    "current_question_index": 0,
    "question_timer_start": None,
    "questions": {},
    "responses": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------ Groq Question Generator ------------------
def generate_questions(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a JSON-only assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        st.markdown(f"""
        <div style='color: white; background-color: #e74c3c; padding: 12px; border-radius: 10px; text-align: center;'>
        ❌ Failed to generate questions. Please check your API key and try again.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

def get_questions(section, difficulty, count):
    section_examples = {
        "quantitative": "Profit & Loss, Time & Work, Percentages, Ratios, Speed & Distance, Averages",
        "logical": "Blood Relations, Number Series, Puzzles, Seating Arrangement, Coding-Decoding, Directions",
        "verbal": "Reading Comprehension, Sentence Correction, Fill in the Blanks, Vocabulary, Para Jumbles"
    }
    return generate_questions(f"""
    You are a JSON-only generator for a competitive **aptitude test**.
    Generate {count} multiple-choice questions of **{difficulty}** difficulty level from the **{section.upper()}** section.

    Questions must reflect real exam patterns from government/placement/mock tests such as SSC, Bank PO, CAT, GATE, etc.

    💡 Use topics like: {section_examples[section]}

    Each question must include:
    - "question": Realistic 3-4 line question in plain English
    - "options": A list of 4 concise string options
    - "answer": Exactly one of the 4 options
    - "section": Must be "{section}"

    ❌ No explanations, comments, or formatting
    ✅ Output clean JSON array only: [{{...}}, ...]
    """)

def generate_mixed_questions(section):
    return (
        get_questions(section, "Easy", 5) +
        get_questions(section, "Medium", 5) +
        get_questions(section, "Hard", 5)
    )

def generate_all():
    return {
        "quantitative": generate_mixed_questions("quantitative"),
        "logical": generate_mixed_questions("logical"),
        "verbal": generate_mixed_questions("verbal")
    }

# ------------------ 🎨 Beautiful UI with Custom Intro ------------------

if st.session_state.page == "intro":
    st.markdown("""
        <style>
            .main-container {
                background-color: #f9fafe;
                padding: 30px;
                border-radius: 18px;
                max-width: 700px;
                margin: auto;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .heading {
                text-align: center;
                font-size: 40px;
                font-weight: bold;
                margin-top: 0;
                margin-bottom: 5px;
                color: #1f2937;
            }
            .tagline {
                text-align: center;
                color: #6b7280;
                font-size: 18px;
                margin-bottom: 25px;
            }
            .logo-img {
                display: block;
                margin: 0 auto 10px;
                width: 70px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='heading'>🧠 TriMent<span style='color:#10b981;'>IQ</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='tagline'>Empowering Minds to Solve, Reason, and Succeed — Confidently</div>", unsafe_allow_html=True)

    with st.expander("📘 About Test", expanded=True):
        st.markdown("""
            Dive into a trio of brain-boosting sections designed to test your reasoning edge**:

            - 📊 **Quantitative Reasoning**
            - 🔍 **Logical Reasoning**
            - 📚 **Verbal Reasoning**

            #### 📝 Format Overview:
            - 🎯 **Total Questions:** 45 (15 per section)  
            - ⏱️ **Time Limit:** 1 minute per question  
            - 🚫 **Negative Marking:** None  
            - ✅ **Scoring:** +1 mark per correct answer

            #### 📈 Performance Bands:
            - 🟢 80–100%: Excellent  
            - 🟡 60–79%: Good  
            - 🟠 40–59%: Average  
            - 🔴 Below 40%: Needs Improvement

            👉 *Think fast. Answer smart. Good luck! 👍*
        """)

    with st.form("candidate_form", clear_on_submit=False):
        st.markdown("### 🧾 Candidate Info")
        name = st.text_input("Your Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Mobile Number")
        submitted = st.form_submit_button("🚀 Start Test")

    st.markdown("""
        <style>
        button[kind="primary"] {
            background: linear-gradient(to right, #10b981, #14b8a6) !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            padding: 0.75em 2.5em !important;
            border: none !important;
            border-radius: 12px !important;
            cursor: pointer !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
        }
        button[kind="primary"]:hover {
            background: linear-gradient(to right, #14b8a6, #10b981) !important;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

    if submitted:
        if not name:
            st.error("Please enter your name to start the test.")
        else:
            with st.spinner("⏳ Generating your test..."):
                st.session_state.questions = generate_all()
                st.session_state.page = "section_intro"
                st.session_state.name = name
                st.session_state.responses = {}
                st.session_state.test_started = True
                st.session_state.current_question_index = 0
                st.session_state.current_section_index = 0
                st.session_state.question_timer_start = None
                st.rerun()

elif st.session_state.page == "section_intro":
    raw_section = sections[st.session_state.current_section_index]
    section = section_display_names.get(raw_section, raw_section.capitalize())

    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-top: 20px;">
            <h2 style="text-align:center; color:#1f2937;">📘 Welcome to <span style="color:#10b981;">{section}</span></h2>
    """, unsafe_allow_html=True)

    section_colors = {
        "Quantitative": "#10b981",
        "Logical": "#10b981",
        "Verbal": "#10b981"
    }
    desc_color = section_colors.get(section, "#10b981")

    section_descriptions = {
        "Quantitative Reasoning": """
        ### 📌 Topics Covered:
        - Percentages, Ratios, Profit & Loss  
        - Time & Work, Time & Distance  
        - Averages, Mixtures, Number Systems

        ### 🧪 Section Format:
        - 🧠 15 Questions  
        - ⏱️ 60 seconds per question  
        - 🎯 5 Easy, 5 Medium, 5 Hard
        """,
        "Logical Reasoning": """
        ### 📌 Topics Covered:
        - Puzzles, Number Series, Blood Relations  
        - Coding-Decoding, Seating Arrangements  
        - Direction Sense, Syllogisms

        ### 🧪 Section Format:
        - 🧠 15 Questions  
        - ⏱️ 60 seconds per question  
        - 🎯 5 Easy, 5 Medium, 5 Hard
        """,
        "Verbal Reasoning": """
        ### 📌 Topics Covered:
        - Reading Comprehension, Vocabulary  
        - Grammar, Sentence Correction  
        - Para Jumbles, Fill in the Blanks

        ### 🧪 Section Format:
        - 🧠 15 Questions  
        - ⏱️ 60 seconds per question  
        - 🎯 5 Easy, 5 Medium, 5 Hard
        """
    }
    st.markdown(section_descriptions[section])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #10b981;
            color: white;
            padding: 0.6rem 1.5rem;
            font-size: 17px;
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
        div.stButton > button:hover {
            background-color: #10b981;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Start Section ➡️"):
        st.session_state.page = "questions"
        st.session_state.question_timer_start = None
        st.rerun()

elif st.session_state.page == "questions":
    section_key = sections[st.session_state.current_section_index]
    section = section_display_names.get(section_key, section_key.capitalize())
    questions = st.session_state.questions[section_key]
    q_idx = st.session_state.current_question_index
    question = questions[q_idx]

    section_colors = {
        "quantitative": "#10b981",
        "logical": "#10b981",
        "verbal": "#10b981"
    }
    accent = section_colors.get(section, "#10b981")
    
    st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 12px 20px; border-radius: 12px; margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <h2 style="color: {accent}; margin-bottom: 5px;">{section}</h2>
            </div>
        """, unsafe_allow_html=True)

    # Question text
    st.markdown(f"""
        <div style="font-size: 18px; line-height: 1.6; padding: 15px 20px;
                    background-color: #ffffff; border-left: 5px solid {accent};
                    border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <b>{q_idx + 1}. {question['question']}</b>
        </div>
    """, unsafe_allow_html=True)

    # Timer logic
    if st.session_state.question_timer_start is None:
        st.session_state.question_timer_start = time.time()

    elapsed = int(time.time() - st.session_state.question_timer_start)
    remaining = max(0, 60 - elapsed)

    st.markdown(f"""
        <div style="background-color: #e0f7fa; color: #00796b; font-weight: 600; 
                    border-radius: 10px; padding: 10px 18px; display: inline-block; margin-bottom: 20px;">
            ⏱️ Time Remaining: {remaining} seconds
        </div>
    """, unsafe_allow_html=True)

    # Options
    selected = st.radio("Choose an option:", question["options"], key=f"{section}_{q_idx}", index=None)

    # Button style
    st.markdown(f"""
        <style>
        div.stButton > button {{
            background-color: {accent};
            color: white;
            font-size: 17px;
            font-weight: 500;
            padding: 0.6rem 1.8rem;
            border: none;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        div.stButton > button:hover {{
            background-color: #333;
            color: #fff59d;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Handle Next button
    if remaining > 0 and st.button("Next ➡️"):
        if selected is None:
            selected = "No Response"

        st.session_state.responses[f"{section}_{q_idx}"] = selected

        if q_idx < len(questions) - 1:
            st.session_state.current_question_index += 1
        else:
            st.session_state.current_question_index = 0
            st.session_state.current_section_index += 1
            st.session_state.page = "section_intro" if st.session_state.current_section_index < len(sections) else "feedback"

        st.session_state.question_timer_start = None
        st.rerun()

    # Auto-submit if time runs out
    if remaining == 0:
        st.session_state.responses[f"{section}_{q_idx}"] = selected if selected else "No Response"

        if q_idx < len(questions) - 1:
            st.session_state.current_question_index += 1
        else:
            st.session_state.current_question_index = 0
            st.session_state.current_section_index += 1
            st.session_state.page = "section_intro" if st.session_state.current_section_index < len(sections) else "feedback"

        st.session_state.question_timer_start = None
        st.rerun()

    # Countdown refresh
    if remaining > 0:
        time.sleep(1)
        st.rerun()
      
        
# -------------------------------------
###Section 6: Final Feedback Page ####
# -----------------------------------
if st.session_state.current_section_index == len(sections):
    st.header("📊 Final Result & Feedback")

    correct = 0
    section_scores = {sec: 0 for sec in sections}
    section_totals = {sec: 15 for sec in sections}

    #Evaluate responses
    for sec in sections:
        for i, q in enumerate(st.session_state.questions[sec]):
            user_ans = st.session_state.responses.get(f"{sec}_{i}", "")
            if user_ans == q["answer"]:
                correct += 1
                section_scores[sec] += 1

    total_questions = 15 * len(sections)
    percentage = int((correct / total_questions) * 100)

    if percentage >= 80:
        category = "Excellent"
    elif percentage >= 60:
        category = "Good"
    elif percentage >= 40:
        category = "Average"
    else:
        category = "Needs Improvement"
        
    name = st.session_state.get("name", "Candidate")
    st.success(f"🎯 {name}, Your Total Score: **{percentage}%** — *{category}*")
    
    # Pie Chart
    #pie_df = pd.DataFrame({
     #   "Category": ["Your Score", "Remaining"],
      #  "Score": [percentage, 100 - percentage]
    #})
    #pie_fig = px.pie(pie_df, names="Category", values="Score", title="Overall Score", template="plotly_dark")
    #st.plotly_chart(pie_fig, use_container_width=True)

    # Section-wise Table
    #result_df = pd.DataFrame({
     #   "Section": list(section_scores.keys()),
      #  "Correct": list(section_scores.values()),
       # "Total": [section_totals[k] for k in sections]
    #})
    #result_df["Accuracy %"] = result_df.apply(
     #   lambda row: round((row["Correct"] / row["Total"]) * 100, 2),
      #  axis=1
    #)
    #st.markdown("---")
    #st.subheader("📊 Section-wise Breakdown")
    #st.dataframe(result_df)

    #bar_fig = px.bar(result_df, x="Section", y="Accuracy %", color="Section",
     #                text="Accuracy %", title="Performance by Section", template="plotly_dark")
    #.st.plotly_chart(bar_fig, use_container_width=True)


# 🎯 Final Result & Feedback
    st.markdown("### 📂 View Detailed Results")

    # Create two tabs: Section Breakdown and Feedback
    tab1, tab2 = st.tabs(["📊 Section-wise Breakdown", "🧠 Personalized Feedback"])

    # Shared DataFrame
    result_df = pd.DataFrame({
        "Section": list(section_scores.keys()),
        "Correct": list(section_scores.values()),
        "Total": [section_totals[k] for k in sections]
    })
    result_df["Accuracy %"] = result_df.apply(
        lambda row: round((row["Correct"] / row["Total"]) * 100, 2),
        axis=1
    )

    # Tab 1: Breakdown
    with tab1:
        st.dataframe(result_df, hide_index=True)

    # Tab 2: Feedback
    with tab2:
    
        def generate_ai_feedback_by_marks(result_df):
            section_scores = []
            for _, row in result_df.iterrows():
                section_scores.append({
                    "section": row["Section"],
                    "marks_obtained": int(row["Correct"]),
                    "total_marks": int(row["Total"])
                })
            prompt = f"""
            You are an exam coach. Based on this section-wise performance, write personalized feedback for each section.

            Give 1–2 lines per section. Be specific, encouraging, and practical.    
            Here is the score breakdown:
            {json.dumps(section_scores, indent=2)}

            Write the feedback in markdown like this:

            🔹 *Section*  
            - Point 1  
            - Point 2  

            Only include relevant points based on the user's score in each section. Avoid unnecessary repetition.
            """
            try:
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a feedback coach for competitive aptitude exams."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"❌ Failed to generate AI feedback: {e}")
                return ""

        ai_feedback = generate_ai_feedback_by_marks(result_df)
        st.markdown(ai_feedback)

    st.balloons()
        

    