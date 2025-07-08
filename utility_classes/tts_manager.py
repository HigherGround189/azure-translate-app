import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv


class TTSManager:
    def __init__(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        AZURE_ENDPOINT_REGION = os.getenv("AZURE_ENDPOINT_REGION")

        speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=AZURE_ENDPOINT_REGION)
        speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
        audio_config = speechsdk.audio.AudioOutputConfig(filename="/content/output.mp3")

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    def transcribe(self, transcript):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(transcript).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}] and saved to /content/output.mp3".format(transcript))
        elif speech_synthesis_result.reason == speechsdk.CancellationReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and endpoint values?")