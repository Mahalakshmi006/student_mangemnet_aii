
#from google import genai


#client = genai.Client(
   ## api_key="AIzaSyB-klr5sJ3Jh2_4-hOMs370Xw1a6NNoUo8"
#)
def generate_feedback(name, subject, mark, attendance):

    prompt = f"""
    Student Name: {name}
    Subject: {subject}
    Mark: {mark}
    Attendance: {attendance}

    Give personalized feedback.
    """

    #response = client.models.generate_content(
      ## contents=prompt
    #)

    #return response.text