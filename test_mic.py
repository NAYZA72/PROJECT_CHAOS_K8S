"""
JARVIS Microphone Test Script
Run this to check if your microphone is working with speech recognition
"""
import speech_recognition as sr

print("=" * 50)
print("  MICROPHONE TEST")
print("=" * 50)

# List all microphones
print("\nAvailable microphones:")
for i, mic in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  [{i}] {mic}")

# Test default microphone
r = sr.Recognizer()
print("\n" + "-" * 50)
print("Testing default microphone...")
print("Speak something when you see 'Listening...'")
print("-" * 50)

try:
    with sr.Microphone() as source:
        print("\nAdjusting for ambient noise (2 seconds)...")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"Energy threshold set to: {r.energy_threshold}")
        
        print("\nListening... (speak now)")
        audio = r.listen(source, timeout=10, phrase_time_limit=10)
        print("Got audio! Processing...")
        
        try:
            text = r.recognize_google(audio, language='en-in')
            print(f"\n✓ SUCCESS! You said: '{text}'")
        except sr.UnknownValueError:
            print("\n✗ Could not understand audio")
            print("  Try speaking louder or closer to the mic")
        except sr.RequestError as e:
            print(f"\n✗ Google API error: {e}")
            print("  Check your internet connection")
            
except sr.WaitTimeoutError:
    print("\n✗ No speech detected within 10 seconds")
    print("  Make sure your microphone is working")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 50)
input("Press Enter to exit...")
