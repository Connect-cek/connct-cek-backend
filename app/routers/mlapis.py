import os
from openai import OpenAI  # Ensure you have the correct OpenAI library installed
from fastapi import Request, APIRouter
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import requests

# Get API key with error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

router = APIRouter()

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


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Create a temporary file to store the uploaded audio
        with open(f"temp_{file.filename}", "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Open and transcribe the audio file
        with open(f"temp_{file.filename}", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up the temporary file
        os.remove(f"temp_{file.filename}")
        
        return {"status": "success", "transcription": transcription.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/runpod_get/{text}")
async def runpod_get(text: str):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer rpa_0M3LBM21PJE4T60JP9Q6253OMVYY4V8GH5D88KSI169nw6'
    }

    data = {
        'input': {"prompt": text}
    }

    response = requests.post('https://api.runpod.ai/v2/c7nwlf5x14trj0/runsync', headers=headers, json=data)
    print(response.json())
    return response.json()


@router.post("/runpod_post")
async def runpod_post(request: Request):
    try:
        # Parse the JSON body from the request
        data = await request.json()
        prompt = data.get("prompt")
        
        if not prompt:
            return {"status": "error", "message": "Prompt is required"}
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer rpa_0M3LBM21PJE4T60JP9Q6253OMVYY4V8GH5D88KSI169nw6'
        }

        payload = {
            'input': {"prompt": prompt}
        }

        # Make the POST request to the RunPod API
        response = requests.post('https://api.runpod.ai/v2/86jxoe64tyzxb6/runsync', headers=headers, json=payload)
        response_data = response.json()
        
        return response_data
    except Exception as e:
        return {"status": "error", "message": str(e)}