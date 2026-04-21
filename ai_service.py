import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)

    def generate_content(self, prompt, model_name=None):
        if self.provider == "gemini":
            try:
                # Modern model name
                current_model = model_name or 'gemini-1.5-flash'
                model = genai.GenerativeModel(current_model)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error with Gemini ({current_model}): {str(e)}"
        elif self.provider == "groq":
            completion = self.groq_client.chat.completions.create(
                model=model_name or "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return completion.choices[0].message.content
        return "No AI provider configured."

    def generate_course_curriculum(self, topic):
        prompt = f"""
        Create a detailed course curriculum for the topic: '{topic}'.
        The response should be a JSON array of objects, where each object has:
        - 'title': Lesson title
        - 'description': Brief summary of the lesson
        - 'order': Sequential integer
        Return ONLY the JSON.
        """
        response = self.generate_content(prompt)
        try:
            # Basic cleanup of AI response if needed
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return [{"title": "Course Introduction", "description": f"Basics of {topic}", "order": 1}]

    def generate_lesson_content(self, course_title, lesson_title):
        prompt = f"Write a comprehensive and engaging lesson content for '{lesson_title}' as part of the '{course_title}' course. Use markdown formatting."
        return self.generate_content(prompt)

    def generate_quiz(self, content):
        prompt = f"""
        Generate 3 multiple-choice questions based on the following content:
        {content}
        
        The response should be a JSON array of objects:
        - 'question': The question text
        - 'options': A list of 4 strings
        - 'answer': The correct option (must be one of the strings in 'options')
        Return ONLY the JSON.
        """
        response = self.generate_content(prompt)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return []
