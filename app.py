import streamlit as st
from tavily import TavilyClient
from google import generativeai as genai
from concurrent.futures import ThreadPoolExecutor


# --------- Core Bot Class ---------
class PostBot:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key="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")
        genai.configure(api_key="AIzaSyDYEFcG8xwMKQc9iNSMIyrKcWBdGhk4q4U")
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def web_search(self, query):
        response = self.tavily_client.search(query=query)
        return " ".join([r.get("content", "") for r in response.get("results", [])])

    def ask_ai(self, prompt):
        return self.model.generate_content(contents=prompt).text.strip()

    def summarize(self, content):
        prompt = f"Summarize the web content into 5 important points: web content = {content}"
        return self.ask_ai(prompt)

    def linkedin_agent(self, summary):
        prompt = f"""
You are a professional LinkedIn content creator. Based on the following summary, write a concise, insightful, and authentic post that resonates with industry professionals.
- Make it suitable for LinkedIn readers.
- Use a friendly yet professional tone.
- Highlight value or lessons learned.
- Include relevant hashtags at the end.
- Avoid emojis unless the context really supports it.

Summary:
\"\"\"{summary}\"\"\"
"""
        return self.ask_ai(prompt)

    def fb_agent(self, summary):
        prompt = f"""
Act as a storyteller for Facebook. Using the summary below, write a casual, warm, and engaging post that feels personal.
- Include emotions or reactions where appropriate.
- You can use emojis to enhance tone.
- The post should feel like you're talking to friends or a close community.

Summary:
\"\"\"{summary}\"\"\"
"""
        return self.ask_ai(prompt)

    def twitter_agent(self, summary):
        prompt = f"""
You're writing for X (formerly Twitter). Craft a tweet thread or a single tweet from this summary:
- Use strong hooks in the first line.
- Maximize clarity and impact in minimal words.
- Optionally use emojis and hashtags.
- Use plain English that grabs attention.

Summary:
\"\"\"{summary}\"\"\"
"""
        return self.ask_ai(prompt)

    def run_all_agents(self, query):
        research = self.web_search(query)
        summary = self.summarize(research)

        agents = [self.fb_agent, self.linkedin_agent, self.twitter_agent]
        platforms = ['Facebook', 'LinkedIn', 'Twitter']

        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda fn: fn(summary), agents)

        return dict(zip(platforms, results))


# ---------- Streamlit UI ----------
# ---------- Streamlit UI ----------
st.set_page_config(page_title="📣 Social Post Generator", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1.2em;
    }
    .section-box {
        background-color: white;
        color: black;
        padding: 1.2em;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.07);
        margin-bottom: 30px;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- App Title ----------
st.title("🧠 AI-Powered Social Post Generator")
st.write("Enter a topic below, and this tool will:")
st.markdown("- 🔍 Search the web\n- ✏️ Summarize it\n- 📣 Generate posts for **LinkedIn**, **Facebook**, and **Twitter (X)**")

# ---------- Input ----------
query = st.text_input("🧾 Enter your topic:", placeholder="e.g. Apple iPhone 17 launch")

if st.button("✨ Generate Posts"):
    if not query.strip():
        st.warning("Please enter a topic.")
    else:
        try:
            bot = PostBot()

            # Step 1: Web Search
            with st.spinner("🔍 Searching the web..."):
                web_result = bot.web_search(query)
                st.markdown("### 🔍 Web Results (raw content)")
                st.markdown(f"<div class='section-box'>{web_result}</div>", unsafe_allow_html=True)

            # Step 2: Summarize
            with st.spinner("✏️ Summarizing the content..."):
                summary = bot.summarize(web_result)
                st.markdown("### 📝 Summary (AI-generated)")
                st.markdown(f"<div class='section-box'>{summary}</div>", unsafe_allow_html=True)

            # Step 3: Generate Posts (in parallel)
            with st.spinner("📣 Generating social media posts..."):
                agents = [bot.fb_agent, bot.linkedin_agent, bot.twitter_agent]
                platforms = ['Facebook', 'LinkedIn', 'Twitter']
                with ThreadPoolExecutor() as executor:
                    results = executor.map(lambda fn: fn(summary), agents)
                posts = dict(zip(platforms, results))

                for platform, post in posts.items():
                    st.markdown(f"### {platform} Post")
                    st.markdown(f"<div class='section-box'>{post}</div>", unsafe_allow_html=True)

            st.success("✅ Done! All content generated.")

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
