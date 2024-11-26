import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import tempfile
import os
from groq import Groq
import random
import time
from gtts import gTTS

st.markdown(
    """
    <style>
    /* General background styles */
    html, body, [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(to bottom right, 
           rgba(135, 206, 255, 0.5),  /* Light Sky Blue */
    rgba(255, 200, 255, 0.5),  /* Soft Peach */
    rgba(192, 192, 255, 0.5),  /* Bright Silver */
    rgba(169, 169, 255, 0.5),  /* Gray */
    rgba(200, 248, 255, 0.5),  /* Alice Blue */
    rgba(173, 216, 255, 0.5)   /* Light Blue */);
        background-size: cover;
        background-attachment: fixed;
    }
    .stButton button {
        background-color: #333333;
        color: white;
        border: 2px solid black;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }

    .stButton button:hover {
        background-color: #333;}
    </style>
    """,
    unsafe_allow_html=True)

client = Groq(api_key=("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"))
ss = st.session_state

session_vars = ["stage", "area", "level","topic", "lang", "ex_tone","prompt", "mcqs", "quiz","audio_bytes", "take_test", "read_text", "audio_file_path", "fb_tone", "response", "answer", "feedback"]
for var in session_vars:
    ss.setdefault(var, None)
    
def transcribe(speech):
    try:
        with st.spinner("Transcribing audio this would only take a few seconds...."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(speech)
                temp_audio_file_path = temp_audio_file.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_audio_file_path) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand the audio. Kindly speak clearly."
    except sr.RequestError as e:
        return f"Error with the transcription service: {e}"
        
def get_response(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content
    except:
        st.warning("Oops! It seems like you're offline. Kindly check your internet connection and try again.")

def text_to_speech(text):
    """Convert text to audio using gTTS and return the path to the audio file."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
            tts = gTTS(text)  
            with st.spinner("Generating the audio, Kindly wait..."):
                tts.save(audio_file.name)  
                audio_file_path = audio_file.name
            return audio_file_path
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None

def show_descriptions(topic):
    topic_descriptions = {
                "Surprise Quiz": "Challenge yourself with a variety of MCQs to enhance your skills and knowledge!",
                "Wordcraft": "Want to learn new words? Wordcraft is here to assist you in expanding your vocabulary!",
                "Word Shuffle": "Rearrange the words and form sentences that make perfect sense!",
                "Word Duel": "Test and build your vocabulary by picking the right synonyms and antonyms.",
                "Imposter Hunt": "Spot the odd one out! Find the word that doesn't belong in the same category.",
                "Rapid Fire": "Think fast! Complete the quiz within a one-minute time span.",
                "Boggle": "You have three minutes to create as many words as possible using the given letters!",
                "Statement Check": "Can you tell the truth from lies? Challenge your instincts and reasoning skills!",
                "Patch the Gaps": "Fill in the blanks with the correct words and complete the sentences!"}
    st.markdown(f"### {topic}")
    st.write(topic_descriptions[topic])

def main_interface():
    st.markdown('<h1 class="heading" style="background: linear-gradient(to right, #ff0044, #ff7300, #fffb00, #00ff52, #0061ff); -webkit-background-clip: text; color: transparent;">English-Buddy</h1>', unsafe_allow_html=True)
    st.markdown('<h6 class="heading-desription">"Your pal on the journey towards mastering English!"</h1>', unsafe_allow_html=True)
    
    if not ss.topic:
        stage = st.radio("Let’s make English fun! Choose your area to begin:", ["Practice Zone", "Grammar Guru", "Quiz Arena"], horizontal=True)

        descriptions = {
            "Practice Zone": "Unlock your full potential in the Practice Zone, where you can practice grammar, reading, writing, speaking, and testing for a well-rounded mastery of English!",
            "Grammar Guru": "Let the Grammar Guru guide you through grammar topics and turn complex concepts into simple knowledge, tailored to your learning style!",
            "Quiz Arena": "Gear up for action! The Quiz Arena is here, with exciting quizzes and exercises that will test your limits and turn you into an English pro!"}
        st.markdown(f"###### {descriptions[stage]}")
        ss.stage = stage
        
        if ss.stage == "Practice Zone":
            area = st.radio("Select your area of focus:", ["Reading Comprehension", "Grammar", "Writing", "Listening and Speaking", "Take a Test"])
            
            if area == "Reading Comprehension":
                st.markdown("Put your understanding to the test, choose a reading type to evaluate your comprehension.")
                topic = st.selectbox("Options:", ["Essay", "Story", "News Article", "History", "Dialogue", "Poem"])
                
            elif area == "Grammar":
                st.markdown("Select the grammar areas you wish to focus on and strengthen your overall command of the language.")
                st.markdown("### Select Grammar Topics to Practice:")
                grammar_topics = {
                    "Tenses": st.checkbox("Tenses", value=True),
                    "Parts of Speech": st.checkbox("Parts of Speech", value=True),
                    "Sentence Structure": st.checkbox("Sentence Structure", value=True),
                    "Subject-Verb Agreement": st.checkbox("Subject-Verb Agreement"),
                    "Active and Passive Voice": st.checkbox("Active and Passive Voice"),
                    "Direct and Indirect Speech": st.checkbox("Direct and Indirect Speech"),
                    "Common Error Detection": st.checkbox("Common Error Detection"),
                    "Articles": st.checkbox("Articles"),
                    "Modal verbs": st.checkbox("Modal verbs"),
                    "Punctuation": st.checkbox("Punctuation")}
                selected_topics = [topic for topic, checked in grammar_topics.items() if checked]
                topic = ", ".join(selected_topics)
               
            elif area == "Writing":
                st.markdown("Show off your writing skills to your buddy and get insightful feedback that can take your writing to the next level.")
                topic = st.selectbox("Options:", ["Essay", "Story", "Speech", "Translation", "Dialogue", "Summary", "Questions and Answers"])
                
            elif area == "Listening and Speaking":
                st.markdown("Enhance your language skills with targeted exercises designed to boost your listening and speaking abilities.")
                topic = st.selectbox("Options:", ["Speech Analysis", "Listening Comprehension", "Questions and Answer", "Debate", "Interview"])
                
            elif area == "Take a Test":
                st.markdown("Ready to push your limits? Challenge yourself with a well-rounded test that evaluates your English proficiency and provides insightful feedback for continuous improvement.")
                topic = "test"
                
        elif ss.stage == "Grammar Guru":
            topic = st.selectbox("Which grammar topic do you want to master:", ["Tenses", "Parts of Speech", "Sentence Structure", "Subject-Verb Agreement", "Articles", "Modal Verbs", "Punctuation", "Essay Composition", "Active and Pssive Voice", "Direct and Indirect Speech", "Adverbial Phrases"])
            
        elif ss.stage == "Quiz Arena":
            topic = st.selectbox("Enter the Quiz Arena! Select your category and let the fun begin:", 
                     ["Surprise Quiz", "Wordcraft", "Word Shuffle", "Word Duel", "Imposter Hunt", "Rapid Fire", "Boggle", "Statement Check", "Patch the Gaps"])
            show_descriptions(topic)
            
        level = st.radio("Select your proficiency level in the selected category:", ["Beginner", "Intermediate", "Advanced"], horizontal=True)
        if st. button ("Proceed"):
            if not topic:
                st.warning("Kindly select atleast one Grammar topic to continue.")
                return
            if ss.stage == "Practice Zone":
                ss.area = area
            ss.topic = topic
            ss.level = level
            st.rerun()
                
    elif ss.topic:
        if st.button("Go Back"):
            ss.clear()
            st.rerun()
            
        if ss.stage == "Quiz Arena":
            if st.button("Next Quiz"):
                arena = ["Surprise Quiz", "Wordcraft", "Word Shuffle", "Word Duel", "Imposter Hunt", "Rapid Fire", "Boggle", "Statement Check", "Patch the Gaps"]
                ss.topic = random.choice(arena)
                ss.feedback = None
                ss.fb_tone = None
                ss.response = None
                ss.answer = None
                st.rerun()
        
        if ss.stage == "Practice Zone":
            area_prompts = {
                "Reading Comprehension": "Generate a '{topic}' suitable for a '{level}' level English learner. After the passage, include 5 multiple-choice questions that test the reader’s understanding of key concepts, details, and vocabulary from the passage.\nAdditionally, don't mention the correct answers.",
                
                "Take a Test": "Create a comprehensive English proficiency test tailored to a '{level}' level, accurately matching the user's current English skills. The test should total 80 marks and be divided as follows:\n\n"
                                "1. Writing (30 marks): Provide three options for essay writing tasks suited to a '{level}' proficiency level. Specify 'Attempt any one.'\n\n"
                                "2. Reading Comprehension (30 marks): Present a '{level}' level passage, followed by 5 MCQs (15 marks) and 2 comprehension questions (15 marks), designed to assess the user's reading skills at this level.\n\n"
                                "3. Grammar (20 marks): Generate 10 Grammar multiple-choice questions, crafted for someone at a '{level}' English proficiency level.\n\n"
                                "Ensure the test is presented professionally, without introductory phrases such as 'Here are the options' or 'Grammar section.'",
                
                "Grammar": "Generate 10 concise error detection type multiple-choice questions based on the following topics: {topic}. These questions should be strictly for someone who has '{level}' level of English proficiency. Avoid any intro and don't mention the correct answer.",
                
                "Writing": {
                    "Story": "Provide 3 writing options for '{topic}' and give a couple of brief and concise hints strictly for a person who has '{level}' level proficiency in English writing.\nSpecify 'Attempt any one of the following:'",
                    "Essay": "Provide 3 writing options for '{topic}' and give a couple of brief and concise hints strictly for a person who has '{level}' level proficiency in English writing.\nSpecify 'Attempt any one of the following:'",
                    "Speech": "Provide 3 writing options for '{topic}' and give a couple of brief and concise hints strictly for a person who has '{level}' level proficiency in English writing.\nSpecify 'Attempt any one of the following:'",
                    "Dialogue": "Provide 3 writing options for '{topic}' and give a couple of brief and concise hints strictly for a person who has '{level}' level proficiency in English writing.\nSpecify 'Attempt any one of the following:'",
                    "Translation": "Generate 5 sentences strictly in 'ROMAN URDU' for me to translate into English at a {level} level. Avoid any intros.",
                    "Summary": "Generate an essay at a moderate length strictly for a person who has '{level}' level of English comprehension ability of whch I have to write a summary. Provide a couple of brief hints on writing a summary.",
                    "Questions and Answers": "Ask 3 personal questions strictly at a '{level}' that require some moderate answers.\nAdditionally don't add any other information just ask the questions."},
                
                "Listening and Speaking": {
                    "Speech Analysis": "Provide a brief informative passage strictly at the '{level}' level for the user to read and record the text. Make sure the passage aligns with the '{level}' level, without including any introductory text—just the passage itself.",
                    "Listening Comprehension": "Provide a concise passage suitable for a '{level}' level, designed for listening comprehension practice. Begin directly with the passage, without any introductory or outro text.",
                    "Questions and Answer": "Provide 3 questions strictly at the '{level}' level for the user to answer in audio. Do not include any intro. Ensure the questions are designed to improve the user's speaking ability and are appropriately challenging for the '{level}' proficiency level.",
                    "Debate": "Provide a brief, controversial passage suited for a '{level}' level, intended for the user to share their opinion. The passage should be tailored to enhance listening and speaking skills, with complexity appropriate for '{level}'. No introduction is needed.",
                    "Interview": "Ask 3 general questions usually asked on interviews for a '{level}' level, intended for the user to share their opinion. The passage should be tailored to enhance listening and speaking skills, with complexity appropriate for '{level}'. No introduction is needed."}}

            if ss.area in area_prompts:
                if isinstance(area_prompts[ss.area], dict):
                    ss.prompt = area_prompts[ss.area].get(ss.topic, "").format(topic=ss.topic, level=ss.level)
                else:
                    ss.prompt = area_prompts[ss.area].format(topic=ss.topic, level=ss.level)
            
        elif ss.stage == "Grammar Guru":
            ex_tone = st.radio("How would you like to learn the selected topic:", ["Simple", "Interesting", "Detailed", "Sarcastic"], horizontal=True)
            lang = st.radio("In which language would you prefer the explanation:" , ["English", "Roman Urdu/Hiindi", "Urdu"], horizontal=True)
            if st.button("Let's Learn!"):
                ss.mcqs = None
                ss.take_test=None
                ss.ex_tone = ex_tone
                ss.lang = lang
                ss.prompt = f"Provide a concise explanation on '{ss.topic}', in a '{ss.ex_tone}' tone, suitable for a '{ss.level}' level learner, strictly in '{ss.lang}'. Avoid introductory phrases."
                ss.response = get_response(ss.prompt)
            
        elif ss.stage == "Quiz Arena":
            game_prompts = {
            "Surprise Quiz": "Generate a random quiz with 7 interesting and concise multiple-choice questions based on English error detection and grammar randomly at a '{level}' level. Each question should have 4 options, with one correct answer. Do not include any introductory statements and do not specify the right answer. Avoid any intro.",
            "Wordcraft": "Generate a set of 7 multiple-choice questions, each asking for the meaning of a challenging word but first using it in a sentence. Ensure the words are suitable for a '{level}' English learner and vary in difficulty and don't specify the right answer. Avoid any intro.",
            "Word Shuffle": "Generate 5 sentences with their words scrambled. The sentence should be for a user with '{level}' level proficiency in English do not specify the right answer. Avoid any intro.",
            "Word Duel": "Generate 7 multiple-choice questions focused on synonyms or antonyms. For each question, use a word in a sentence suitable for the {level} level. Then ask the user to identify its synonym or antonym (randomly select one). Avoid any intro.",
            "Imposter Hunt": "Create 7 multiple-choice questions with four words as options (A, B, C, D). Three words should belong to the same grammar or vocabulary category, while one is the imposter. Match the difficulty to the {level} level.",
            "Rapid Fire": "Generate 7 very concise multiple-choice questions based on differnet aspects of English randomly for a {level} learner. Specify the users has only 1 minute after that the answer will be submitted automatically. Avoid any intro.",
            "Boggle": "Generate a random long word (more than 8 letters) with a variety of different words, suitable for a {level} learner.Explain the rules something like: 1. create smaller valid words using the letters from this word. 2. Each word must be at least 3 letters long. 3. The users can use a single letter twice or thrice in a word. 4. The user has only 3 minutes. Additionally give 2 or 3 words as example and don't add any intro.",
            "Statement Check": "Generate 7 true or false statements related to English error detection, vocabulary and grammar randomly as multiple-choice questions. Each statement should have 2 options: 'True' or 'False.' After the user selects an answer, provide an explanation for why the statement is correct or incorrect. Avoid any intro.",
            "Patch the Gaps": "Create 7 very concise Fill in the blanks MCQs based on error detection, vocabulary, and grammar randomly as multiple-choice questions suitable for a {level} learner. The sentence should have a blank where a word is missing, and the choices should be different forms of the word or related words, without including the word in the options provided in the brackets. Avoid specifying the correct answer and any intro.",}
            ss.prompt = game_prompts[ss.topic].format(level=ss.level)
            
        if ss.prompt:
            if ss.stage == "Quiz Arena":
                show_descriptions(ss.topic)
            if not ss.response and ss.stage != "Grammar Guru":
                 ss.response = get_response(ss.prompt)
            if ss.topic in ["Debate","Listening Comprehension", "Questions and Answer", "Interview"]:
                if not ss.audio_file_path:
                    ss.audio_file_path = text_to_speech(ss.response)
                if ss.audio_file_path:
                    with open(ss.audio_file_path, "rb") as audio_file:
                        st.audio(audio_file, format="audio/mp3")
                if ss.topic != "Listening Comprehension" and not ss.read_text:
                    if st.button("Read Text"):
                        ss.read_text = True
                if ss.read_text:
                    st.write(ss.response)
            else:
                st.write(ss.response)
                
            if ss.stage == "Grammar Guru":
                if not ss.take_test:
                    if st.button("Take a Quiz"):
                        ss.take_test = True
                if ss.take_test:
                    questions_prompt = f"Generate 5 very short MCQs with short options related to '{ss.topic}' the explanation used to explain the topic is '{ss.response}' suitable for a person who has '{ss.level}' proficiency in English Grammar.Don't specify the correct answers and avoid any intros."
                    ss.quiz = get_response(questions_prompt)
                    st.write(ss.quiz)
            elif ss.topic == "Listening Comprehension":
                ss.mcqs = get_response(f"Genrate 5 MCQs strictly for a person with {ss.level} level proficiency in listening comprehension based on the following text (transcribed):\n'{ss.response}'. Make sure not to mention the correct answers.")
                st.write(ss.mcqs)
            if ss.topic in ["Speech Analysis", "Debate", "Questions and Answer", "Interview"]:
                if not ss.audio_bytes:
                    st.info("Don’t let the mic get bored! Speak continuously to keep the recording alive.")
                ss.audio_bytes = audio_recorder()
                if ss.audio_bytes:
                    st.info("Your Recording:")
                    st.audio(ss.audio_bytes, format="audio/wav")
                    st.markdown("Press the mic icon to record again")
            
            elif ss.area == "Take a Test":
                answer = st.text_area("Your Answers to the Questions", height=200, placeholder="Attempt the test like:\nSection 'A' Essay\nWrite your essay here.....\n\nSection 'B' Reading Comprehension\n1. C\n2. D....\n\nAnswer 1 ....\nAnswer 2....\n\nSection 'C' Grammar\n1. C\n2. D....")
            elif ss.area == "Writing" or ss.topic in ["Boggle", "Word Shuffle"]:
                answer = st.text_area("Your Answers to the Questions", height=170)
            
            elif ss.stage == "Grammar Guru":
                if ss.take_test:
                    answer = st.text_area("Your Answers to the Questions", height=120, placeholder="Kindly attempt the answers like:\n1. A\n2. C\n3. B.....")
                    fb_tone = st.radio("So which tone would you prefer to get the feedback in:", ["Professional", "Friendly", "Sarcastic", "Encouraging"], horizontal=True)
            else:
                answer = st.text_area("Your Answers to the Questions", height=120, placeholder="Kindly attempt the answers like:\n1. A\n2. C\n3. B.....")
            if ss.stage != "Grammar Guru" and ss.topic not in ["Rapid Fire", "Boggle"]:
                fb_tone = st.radio("So which tone would you prefer to get the feedback in:", ["Professional", "Friendly", "Sarcastic", "Encouraging"], horizontal=True)
            
            if ss.topic in ["Rapid Fire", "Boggle"] and not ss.fb_tone:
                fb_tone = "Encouraging and simple"
                if ss.topic == "Rapid Fire":
                    st.write("You have 60 seconds to answer!")
                else:
                    st.write("You have 3 minutes to answer!")
                if st.button("Submit Answers"):
                    ss.fb_tone = fb_tone
                    st.rerun()
                placeholder = st.empty() 
                start_time = time.time()
                if ss.topic == "Rapid Fire":
                    time_limit = 60
                else:
                    time_limit = 180
                    
                while time.time() - start_time < time_limit:
                    remaining_time = time_limit - int(time.time() - start_time)
                    placeholder.write(f"Time remaining: {remaining_time} seconds")
                    time.sleep(1)  
                placeholder.empty()
                st.warning("Time's up! Generating feedback...")
                ss.fb_tone = fb_tone
                st.rerun()
                
            elif ss.stage == "Grammar Guru":
                if ss.take_test:
                    if st.button("Submit Answers"):
                            ss.fb_tone = fb_tone
            else:
                if st.button("Submit Answers"):
                    ss.fb_tone = fb_tone
                    st.rerun()
                    
        if ss.fb_tone:
            if ss.topic in ["Speech Analysis", "Debate", "Questions and Answer", "Interview"]:
                answer = transcribe(ss.audio_bytes)
                if answer.startswith("Error") or answer.startswith("Could not"):
                    st.error(answer)
                else:
                    st.success(f"What You Said: {answer}")
            if answer is None or answer == "":
                st.info("Kindly write the answers...")
                return
            else:
                ss.answer = answer
            
            if ss.stage == "Grammar Guru":
                fb_prompt = f"Evaluate and provide concise feedback in simple words on the following answers to the questions related to '{ss.topic}.'\nThe explanation used to explain the topic is:\n'{ss.response}.'\nThe mcqs are: '{ss.quiz}.'\nThe answers given by me are: '{ss.answer}.'\nSpecify how many ansers are correct strictly accurately, if the answers are none or irrelevant say something like: 'Kindly give the answers correctly', and if there are some answers missing then specify which ones and request that they be done."
            elif ss.area == "Reading Comprehension":
                fb_prompt = f"The following text and questions were used to evaluate reading comprehension ability:\n'{ss.response}'\nGiven Answers of the MCQs are:\n{ss.answer}\n\nKindly first tell me how many answers are correct. Then, provide feedback on the incorrect answers in a {ss.fb_tone} tone strictly for a person who has {ss.level} level proficiency in grammar and then provide overall brief feedback. If the answers are none or irrelevant thensay: 'Kindly attempt the answers correctly.' If some answers are missing, specify which ones are missing and request that they be answered. Additionally don't add any intro"
            elif ss.area == "Grammar": 
                fb_prompt = f"Act as an English instructor to evaluate the user's grammar skills based on the following MCQs:\n'{ss.response}'\n\nUser's Answers:\n{ss.answer}\n\nFirst, indicate the number of correct answers. Then, provide {ss.level} feedback on any incorrect answers, explaining the correct grammar concepts strictly in a {ss.fb_tone} tone.\nIf the answers are none, irrelevant, or incomplete, say: 'Kindly ensure all answers are attempted thoughtfully.' If some answers are missing, specify which ones are missing and request that they be answered.' Additionally don't add any intro"
            elif ss.area == "Take a Test":
                fb_prompt = f"Act as an English teacher and evaluate the user's answer paper strictly in a {ss.fb_tone} for a person with {ss.level} proficiency in English, rating it out of 80 marks.\nThe question paper is:\n'{ss.response}'\nUser's answer paper:\n{ss.answer}\n\nAssign marks to each section and provide concise feedback on each one in a {ss.fb_tone} tone at the {ss.level} level (Give full marks if the answers are correct). Include an overall feedback summary at the end. Avoid introductory statements.\nIf the response is none or irrelevant, give 0 marks and say: 'Kindly attempt all answers using the correct method.' If any answers are missing, specify which ones and request they be addressed."    
            else:
                feedback_prompts = {
"Story" : f"Provide feedback on story writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The options are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Essay" : f"Provide feedback on essay writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The options are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant. missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Speech" : f"Provide feedback on speech writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The options are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Translation" : f"Provide feedback on tanslation skill, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The sentences are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Questions and Answers" : f"Provide feedback on English writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The qustions are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Dialogue" : f"Provide feedback on English writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The options are: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Summary" : f"Provide feedback on summary writing, clarity, structure, grammar, and coherence and suggest improvements strictly in a {ss.fb_tone} tone and rate out of 10 according to someone who has {ss.level} level proficiency in English Writing.The Summary is: '{ss.response}'\n My Response:\n'{ss.answer}'\n If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Speech Analysis" : f"Provide a concise feedback on intonation, fluency, clarity, and pronunciation strictly in a {ss.fb_tone} tone and according to a person with {ss.level} level proficiency in Speaking and rate the given response out of 10.\nThe text used to assess speaking ability was:\n'{ss.response}'\nUser's recorded speech (transcribed):\n{ss.answer}\n. If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Questions and Answer" : f"Provide a concise feedback on intonation, fluency, calrity, and pronunciation strictly in a {ss.fb_tone} tone and according to a person with {ss.level} level proficiency in Speaking and rate the given response out of 10.\nQuestions:\n'{ss.response}'\nUser's answers in recorded speech (transcribed):\n{ss.answer}\n. If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Debate" : f"Provide a concise feedback on dabate skill, intonation, fluency, and pronunciation strictly in a {ss.fb_tone} tone and according to a person with {ss.level} level proficiency in Speaking and rate the given response out of 10.\nThe debate topic was:\n'{ss.response}'\nUser's resonse (transcribed):\n{ss.answer}\n. If irrelevant. missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Interview" : f"Provide a concise feedback on interview skill, intonation, fluency, and pronunciation strictly in a {ss.fb_tone} tone and according to a person with {ss.level} level proficiency in Speaking and rate the given response out of 10.\nThe interview questions:\n'{ss.response}'\nUser's response (transcribed):\n{ss.answer}\n. If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Listening Comprehension" : f"This text (transcribed) was used to test my listening comprehension:\n '{ss.response}'\n The MCQs were:\n'{ss.mcqs}'\nMy answers:\n '{ss.answer}']n I want you to tell me how many are correct and then provide a brief feedback on the incorrect ones strictly in a {ss.fb_tone} and for a persom with {ss.level} level proficiency in listenong comprehension. If irrelevant, missing or none, say: 'Kindly attempt the answers correctly.' Avoid adding intros.",
"Surprise Quiz": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Wordcraft": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Word Shuffle": f"These sentences are in a jumbled order: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Word Duel": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Imposter Hunt": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Rapid Fire": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Boggle": f"Rules: \n'{ss.response}'\nWords I made:\n'{ss.answer}'\nSpecify how many words are correct and valid according to the rules and provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Statement Check": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify the number of the words that are correct, provide feedback only on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
"Patch the Gaps": f"Questions: \n'{ss.response}'\nMy answers:\n'{ss.answer}'\nSpecify how many answers are correct, provide feedback on the incorrect answers and suggest areas for improvement strictly in a '{ss.fb_tone}' and at a {ss.level} level. If the answers are none or irrelevant, say: 'Kindly attempt the answers correctly.' Avoid introductory statements.",
}
                fb_prompt = feedback_prompts[ss.topic]
        
            if ss.answer:
                with st.spinner("Generating Feedback....."):
                    feedback = get_response(fb_prompt)
                    ss.feedback = feedback
                    st.write(feedback)
                    ss.fb_tone = None
                    
                if st.button("Try Again"):
                    ss.feedback = None
                    ss.answer = None
                    ss.fb_tone = None
                    ss.quiz = None
                    ss.mcqs = None
                    ss.response = None
                    st.rerun()

main_interface()
