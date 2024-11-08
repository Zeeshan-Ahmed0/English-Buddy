import streamlit as st
from groq import Groq

api_keys = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]
# Function to intercept the back button
def back_intercept():
    js_code = """
    <script>
    let modalShown = false;

    window.onbeforeunload = function() {
        if (!modalShown) {
            modalShown = true; // Prevent multiple modals
            const userConfirmed = confirm("Are you sure you want to leave this page?");
            if (!userConfirmed) {
                return false; // Prevent leaving the page
            }
        }
    };
    </script>
    """
    st.components.v1.html(js_code, height=0)

# Call the back button intercept function
back_intercept()

# An alias for using session state
ss = st.session_state

# Initialize session state variables
session_vars = ["level_selected", "area_selected", "reading_type_selected", "writing_type_selected","speaking_type_selected", "text_generated", "user_answers", "feedback_generated", "feedback_tone", "continues","listening_questions","audio_path", "show_answer","read_text_instead"]
for var in session_vars:
    ss.setdefault(var, None)

# Function to get response from Groq
current_key_index = 0

def get_groq_client():
    global current_key_index
    # Select the current API key
    api_key = api_keys[current_key_index]
    # Create a Groq client with the current API key
    client = Groq(api_key=api_key)
    # Update the index for the next call
    current_key_index = (current_key_index + 1) % len(api_keys)
    return client
# llama-3.1-70b-versatile
def get_response(prompt):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception:
        st.error("Error generating the desired response. Please try again.")
        return None

# Function to get feedback on answers from Groq
def get_feedback(prompt_content):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_content}],
            model="llama-3.1-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception:
        st.error("Error generating feedback. Please try again.")
        return None

if 'levels' not in ss:
    ss.levels = []

def back():
    ss.text_generated = None
    ss.reading_type_selected = None
    ss.writing_type_selected = None
    ss.speaking_type_selected = None
    ss.is_recording = None
    ss.user_answers = None
    ss.continues = None
    ss.feedback_generated = None
    ss.audio_path = None
    ss.show_answer = None
    ss.read_text_instead = None

def main_interface():
    st.markdown("<h1>English Buddy</h1>", unsafe_allow_html=True)
    # Level selection
    if not ss.levels:
        st.markdown("### Select Your Level:")
        level = st.radio("Choose a Level:", ["Beginner", "Intermediate", "Advanced"], index=0)
        if st.button("Select Level"):
            ss.level_selected = level
            ss.levels.append("level_selected")
            st.rerun()
    
    elif ss.text_generated and ss.levels[-1] == ss.text_generated:
        if st.button("⬅️ Back", key="back", help="Go back"):
            ss.levels = ss.levels[:-2]
            back()
            st.rerun()

        elif ss.writing_type_selected:
            st.write(ss.text_generated)
            ss.user_answers = st.text_area("Your Answers to the Questions", height=150, placeholder="Start Writing Here:")
            ss.continues = "true"
            
        else:
            st.write(ss.text_generated)
            ss.user_answers = st.text_area("Your Answers to the Questions", height=150, placeholder="Please attempt the answers like:\n1. A\n2. C\n3. B.....")
            ss.continues = "true"
            
        if ss.continues == "true":
            st.markdown("### Please select the tone you want the feedback in:")
            tone = st.radio("Options:", ["Professional", "Friendly", "Motivational", "Sarcastic", "Optimistic"])
            ss.feedback_tone = tone
            if st.button("Get Result"):
                with st.spinner("Generating feedback..."):
                    feedbacks = {
                        "reading_feedback" : f"The following text and questions were used to evaluate reading comprehension ability:\n{ss.text_generated}\nGiven Answers of the MCQs are:\n{ss.user_answers}\n\nPlease first tell me how many answers are correct. Then, provide feedback on the incorrect answers in a {ss.feedback_tone} tone strictly for a person who has {ss.level_selected} level proficiency in grammar. If the answers are none or irrelevant, please say: 'Please attempt the answers correctly.' If some answers are missing, specify which ones are missing and request that they be answered. Additionally don't add any intro",
                        "story_essay_feedback" : f"Act as an English instructor and evaluate the user's writing skill at the {ss.level_selected} level based on the provided text:\n\nText Provided:\n{ss.text_generated}\n\nuser's Response:\n{ss.user_answers}\n\nProvide feedback on the clarity, structure, grammar, and coherence of the writing, and offer suggestions for improvement in a {ss.feedback_tone} and rate the given response out of 10 strictly according to a person with {ss.level_selected} level proficiency in English writing (Be generous with the ratings). If the user's answer is none or irrelevant, say something like: 'Kindly attempt the answers correctly. Additionally don't add any intro",
                        "qna_writing_feedback" : f"Act as an English instructor and evaluate the user's writing skill strictly at a {ss.level_selected} level based on the following questions:\n\nQuestions Provided:\n{ss.text_generated}\n\nuser's Answers:\n{ss.user_answers}\n\nFocus on the {ss.level_selected} level of writing skill. Provide brief and concise feedback on vocabulary, clarity, and structure, grammar, punctuation and suggest areas for improvement in a {ss.feedback_tone} tone and rate the given answers out of 10 strictly according to a person with {ss.level_selected} level proficiency in English writing.\nIf the answers are none or irrelevant, say something like: 'Kindly attempt the answers correctly.' If some answers are missing, specify which ones are missing and request that they be answered. Additionally don't add any intro",
                        "summary_feedback" : f"Act as an English instructor and analyze the user's summary response at the {ss.level_selected} level, based on the provided text:\n\nText Provided:\n{ss.text_generated}\n\nuser's Summary:\n{ss.user_answers}\n\nEvaluate briefly the usage of vocabulary, clarity, structure, grammar, punctuation, and overall summary writing, and provide brief feedback with suggestions for improvement in a {ss.feedback_tone} tone and rate the given summary out of 10 strictly according to a person with {ss.level_selected} level proficiency in summary writing.\nIf the response is none or irrelevant, say: 'Kindly attempt the summary correctly.' If some parts are missing, specify which ones are missing and request that they be completed. Additionally don't add any intro",
                        "grammar_feedback" : f"Act as an English instructor to evaluate the user's grammar skills based on the following MCQs:\n{ss.text_generated}\n\nUser's Answers:\n{ss.user_answers}\n\nFirst, indicate the number of correct answers. Then, provide {ss.level_selected} feedback on any incorrect answers, explaining the correct grammar concepts in a {ss.feedback_tone} tone.\nIf the answers are none, irrelevant, or incomplete, say: 'Please ensure all answers are attempted thoughtfully.' If some answers are missing, specify which ones are missing and request that they be answered.' Additionally don't add any intro",
                        "test_feedback" : f"Act as an English teacher and evaluate the user's answer paper strictly in a {ss.feedback_tone} for a person with {ss.level_selected} proficiency in English, rating it out of 70 marks.\nThe question paper is:\n{ss.text_generated}\nUser's answer paper:\n{ss.user_answers}\n\nAssign marks to each section and provide concise feedback on each one in a {ss.feedback_tone} tone at the {ss.level_selected} level. Include an overall feedback summary at the end. Avoid introductory statements.\nIf the response is none or irrelevant, give 0 marks and say: 'Kindly attempt all answers using the correct method.' If any answers are missing, specify which ones and request they be addressed."
                    }
                    feedback_prompt = ""
                    if ss.reading_type_selected:
                        feedback_prompt = feedbacks["reading_feedback"]
                    elif ss.writing_type_selected in ["Story", "Essay"]:
                        feedback_prompt = feedbacks["story_essay_feedback"]
                    elif ss.writing_type_selected == "Questions and Answers":
                        feedback_prompt = feedbacks["qna_writing_feedback"]
                    elif ss.writing_type_selected == "Summary":
                        feedback_prompt = feedbacks["summary_feedback"]
                    elif ss.area_selected and ss.area_selected == "Grammar":
                        feedback_prompt = feedbacks["grammar_feedback"]
                    elif ss.area_selected == "Take a Test":
                        feedback_prompt = feedbacks["test_feedback"]
                           
                    ss.feedback_generated = get_feedback(feedback_prompt)
                    with st.spinner("Generating Feedback....."):
                        if ss.feedback_generated:
                            st.markdown("### Feedback:")
                            st.write(ss.feedback_generated)
                        else:
                            st.error("Feedback could not be generated.")
                        if ss.feedback_generated:
                            if st.button("Try Again"):
                                back()
                                ss.levels = ss.levels[:-2]
                                st.rerun()
                            if st.button("Go To Home Page"):
                                back()
                                ss.level_seleted = None
                                ss.area_seleted = None
                                ss.levels = None
                                st.rerun()
                    
    # Area selection
    elif ss.levels[-1] == "level_selected":
        if st.button("⬅️ Back", key="back", help="Go back to the previous selection"):
            ss.level_selected = None
            ss.levels.pop()
            st.rerun()
        st.markdown("### Choose Your Focus Area:")
        area = st.radio(
            "Choose an Area:", 
            options=["Grammar", "Reading Comprehension", "Writing", "Take a Test"], 
            index=0
        )
        if st.button("Confirm Area"):
            ss.area_selected = area
            ss.levels.append(ss.area_selected)
            st.rerun()

    # Reading Comprehension Flow
    elif ss.levels[-1] == "Reading Comprehension":
        if not ss.reading_type_selected:
            if st.button("⬅️ Back", key="back", help="Go back to the previous selection"):
                ss.area_selected = None
                ss.levels.pop()
                st.rerun()
            st.markdown("#### Select Reading Material Type:")
            reading_type = st.radio("Options:", ["Short Story", "Dialogue", "Short Essay", "News Article"])
            if st.button("Continue"):
                ss.reading_type_selected = reading_type
                reading_prompt = f"Generate a {ss.reading_type_selected} suitable for a {ss.level_selected} level English learner. After the passage, include 10 multiple-choice questions that test the reader’s understanding of key concepts, details, and vocabulary from the passage.\nAdditionally, don't mention the correct answers."
                ss.text_generated = get_response(reading_prompt)
                ss.levels.append(ss.text_generated)
                st.rerun()
                
    # Writing Flow
    elif ss.levels[-1] == "Writing":        
        if st.button("⬅️ Back", key="back", help="Go back to the previous selection"):
            ss.area_selected = None
            ss.levels.pop()
            st.rerun()
        st.markdown("#### Select Writing Task:")
        writing_type = st.radio("Options:", ["Story", "Essay", "Questions and Answers", "Summary"])
        if st.button("Proceed"):
            ss.writing_type_selected = writing_type
            
            story_essay_prompt = f"Provide 3 writing options for {ss.writing_type_selected} and give a couple of brief and concise hints strictly for a person who has {ss.level_selected} level proficiency in English writing.\nSpecify 'Attempt any one of the following:'."
            qna_prompt = f"Ask 3 personal questions strictly at a {ss.level_selected} that require some moderate answers.\nAdditionally don't add any onter information just ask the questions."
            summary_prompt = f"Generate an essay at a moderate length strictly for a person who has {ss.level_selected} level of English comprehension ability. Provide a couple of brief hints on writing a summary, don't add any examples or sample summary."
            
            if ss.writing_type_selected in ["Story", "Essay"]:
                ss.text_generated = get_response(story_essay_prompt)    
            elif ss.writing_type_selected == "Questions and Answers":
                ss.text_generated = get_response(qna_prompt)
            elif ss.writing_type_selected == "Summary":
                ss.text_generated = get_response(summary_prompt)
                
            ss.levels.append(ss.text_generated)
            st.rerun()
                                 
    # Grammar Flow
    elif ss.levels[-1] == "Grammar":
        if st.button("⬅️ Back", key="back", help="Go back to the previous selection"):
            ss.area_selected = None
            ss.levels.pop()
            st.rerun()
        # Step 1: Checkbox selection for Grammar Topics (all checked by default)
        st.markdown("### Select Grammar Topics to Practice:")
        grammar_topics = {
            "Tenses": st.checkbox("Tenses"),
            "Parts of Speech": st.checkbox("Parts of Speech"),
            "Sentence Structure": st.checkbox("Sentence Structure"),
            "Subject-Verb Agreement": st.checkbox("Subject-Verb Agreement", value=True),
            "Forms of Verb": st.checkbox("Forms of Verb", value=True),
            "Spellings": st.checkbox("Spellings"),
            "Common Error Detection": st.checkbox("Common Error Detection", value=True),
            "Articles": st.checkbox("Articles"),
            "Modal verbs": st.checkbox("Modal verbs"),
            "Synonyms/Antonyms": st.checkbox("Synonyms/Antonyms", value=True)
        }

        selected_topics = [topic for topic, checked in grammar_topics.items() if checked]

        st.markdown("### Select the Number of MCQs:")
        
        # Step 2: Radio button selection for number of MCQs
        mcq_count = st.radio(
            "Please select the number of MCQs you want:",
            ["5", "10", "15"], horizontal=True
        )
        # Step 2: Provide MCQs based on selected topics
        if st.button("Generate Questions"):
            if selected_topics:
                selected_topics_str = ", ".join(selected_topics)
                questions_prompt = f"Generate {mcq_count} practical, applied multiple-choice questions based on the following topics: {selected_topics_str}. These questions should be strictly for someone who has {ss.level_selected} level of English proficiency.\nShow options on a new line.\nDo not include any introductory statements like 'here are the questions.'"
                ss.text_generated = get_response(questions_prompt)
                ss.levels.append(ss.text_generated)
                st.rerun()
            elif not selected_topics:
                st.write("Please select atleast one Grammar topic to continue.")

    elif ss.levels[-1] == "Take a Test":
        if st.button("⬅️ Back", key="back", help="Go back to the previous selection"):
            ss.area_selected = None
            ss.levels.pop()
            st.rerun()
        
        st.markdown("## Total marks are 70:\n1. Writing: 30 Marks\n2. Reading Comprehension: 30 Marks\n3. Grammar: 20 Marks")
        st.markdown("#### Kindly select the topic of writing:")
        test_writing_type = st.radio("Options:", ["Essay", "Story", "Dialogue", "Email"], horizontal=True)
        st.markdown("#### Kindly select the topic of Reading Comprehension:")
        test_reading_type = st.radio("Options:", ["Story", "Dialogue", "Essay", "News Article"], horizontal=True)
        st.markdown("### Select Grammar Topics:")
        grammar_topics = {
            "Tenses": st.checkbox("Tenses", value=True),
            "Parts of Speech": st.checkbox("Parts of Speech", value=True),
            "Sentence Structure": st.checkbox("Sentence Structure", value=True),
            "Subject-Verb Agreement": st.checkbox("Subject-Verb Agreement", value=True),
            "Forms of Verb": st.checkbox("Forms of Verb", value=True),
            "Spellings": st.checkbox("Spellings", value=True),
            "Common Error Detection": st.checkbox("Common Error Detection", value=True),
            "Articles": st.checkbox("Articles", value=True),
            "Modal verbs": st.checkbox("Modal verbs", value=True),
            "Synonyms/Antonyms": st.checkbox("Synonyms/Antonyms", value=True)}
        
        selected_topics = [topic for topic, checked in grammar_topics.items() if checked]
        if st.button("Start The Test"):
            if selected_topics:
                selected_topics_str = ", ".join(selected_topics)
                test_prompt = (
    f"Create a comprehensive English proficiency test tailored to a {ss.level_selected} level, accurately matching the user's current English skills. The test should total 70 marks and be divided as follows:\n\n"
    f"1. Writing (30 marks): Provide three options for {test_writing_type} writing tasks suited to a {ss.level_selected} proficiency level. Specify 'Attempt any one.'\n\n"
    f"2. Reading Comprehension (30 marks): Present a short {ss.level_selected} level passage on {test_reading_type}, followed by 5 MCQs (15 marks) and 2 comprehension questions (15 marks), designed to assess the user's reading skills at this level.\n\n"
    f"3. Grammar (20 marks): Generate 10 multiple-choice questions focusing on {selected_topics_str}, crafted for someone at a {ss.level_selected} English proficiency level.\n\n"
    f"Ensure the test is presented professionally, without introductory phrases such as 'Here are the options' or 'Grammar section.'")

                ss.text_generated = get_response(test_prompt)
                ss.levels.append(ss.text_generated)
                st.rerun()
            elif not selected_topics:
                st.write("Please select atleast one Grammar topic to continue.")

main_interface()
