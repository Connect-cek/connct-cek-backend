import os
from openai import OpenAI  # Ensure you have the correct OpenAI library installed
from fastapi import Request,APIRouter
import uuid
from pathlib import Path

# Get API key with error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)
###
#   let conversationHistory = [
#            {"role": "system", "content": "You are a helpful assistant."}
#        ];
# update conversationHistory to include the user message and assistant response    
# conversationHistory.push({
#                 "role": "user",
#                 "content": transcriptionResult.transcription
#             });
# 

# #   Send the transcription to the server for chat completion
#  const chatResponse = await fetch('/chat', {
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/json',
#                     },
#                     body: JSON.stringify({
#                         message: transcriptionResult.transcription,
#                         conversation_history: conversationHistory
#                     })
#                 });

#                 const chatResult = await chatResponse.json();
                
#      Add assistant's response to conversation history
#                 conversationHistory.push({
#                     "role": "assistant",
#                     "content": chatResult.response
#                 });

###



@app.post("/chat")
async def chat_completion(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        conversation_history = data.get("conversation_history", [])
        
        # Get chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        
        response_text = response.choices[0].message.content
        
        # Generate speech from the response
        speech_file_name = f"speech_{uuid.uuid4()}.mp3"
        speech_file_path = Path(__file__).parent.parent.parent / "uploads" / "audio" / speech_file_name
        
        # Ensure the audio directory exists
        speech_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate speech
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text
        )
        
        # Save the audio file
        audio_response.stream_to_file(str(speech_file_path))
        
        return {
            "status": "success", 
            "response": response_text,
            "audio_url": f"/uploads/audio/{speech_file_name}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}