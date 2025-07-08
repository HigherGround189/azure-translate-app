import azure.cognitiveservices.speech as speechsdk
import os

class TTSManager:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
        # Set the voice name, refer to https://aka.ms/speech/voices/neural for available voices
        self.speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'
        
    def synthesize_speech(self, text):
        try:
            # Use an in-memory audio stream
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

