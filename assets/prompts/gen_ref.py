from gtts import gTTS
tts = gTTS("আমি বাংলায় কথা বলি।", lang="bn")
tts.save("bangla_ref_new.mp3")
print("Done")
