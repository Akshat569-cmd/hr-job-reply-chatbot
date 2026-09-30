from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(".env", override=True)

app = FastAPI(title="HR Chatbot API")

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


# Load .env
load_dotenv()

# Create FastAPI app
app = FastAPI(title="HR Chatbot API")

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Job data
jobs = [
    {
        "title": "Python Developer Intern",
        "skills": ["Python", "Django"]
    },
    {
        "title": "Frontend Developer Intern",
        "skills": ["HTML", "CSS", "JavaScript"]
    }
]


# Request format
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    # Empty message
    if not message:
        return {
            "response": "Please enter a message."
        }

    # Convert jobs data into text for the LLM
    jobs_text = ""

    for job in jobs:
        jobs_text += (
            f"Job Title: {job['title']}\n"
            f"Skills: {', '.join(job['skills'])}\n\n"
        )

    # System prompt
    system_prompt = f"""
You are an HR chatbot.

You can only answer questions related to jobs and recruitment.

Here is the available job data:

{jobs_text}

Rules:
1. If the user greets you, respond politely.
2. If the user asks what jobs are available, list the available job titles.
3. If the user asks about a specific skill, check the provided job data.
4. Do not invent jobs or skills.
5. If the question is unrelated to jobs, say:
"Sorry, I can only help with job-related queries."
"""

    # Call Groq LLM
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    return {
        "response": answer
    }
