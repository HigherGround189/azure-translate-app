import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

class TTSManager:
    def __init__(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        AZURE_ENDPOINT_REGION = os.getenv("AZURE_ENDPOINT_REGION")

        self.speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=AZURE_ENDPOINT_REGION)
        self.speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'
        
    def synthesize_speech(self, text):
        try:
            audio_output = speechsdk.audio.PullAudioOutputStream()
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=speechsdk.audio.AudioOutputConfig(stream=audio_output))
            
            result = speech_synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized for text [{}]".format(text))
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    if cancellation_details.error_details:
                        print("Error details: {}".format(cancellation_details.error_details))
                return None
        except Exception as e:
            print(f"An error occurred during speech synthesis: {e}")
            return None

