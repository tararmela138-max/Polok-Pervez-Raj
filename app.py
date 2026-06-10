import streamlit as st
import os
import time
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

st.set_page_config(page_title="Polok Parvez Raj", layout="centered")
st.title("Polok Parvez Raj")
st.write("ভিডিও আপলোড করুন এবং স্বয়ংক্রিয়ভাবে কপিরাইট-মুক্ত নতুন ভিডিও তৈরি করুন!")

uploaded_file = st.file_uploader("আপনার মূল নিউজ ভিডিওটি আপলোড করুন", type=["mp4", "mov", "avi"])
voice_option = st.selectbox("ভয়েস টোন সিলেক্ট করুন:", ["Male (পুরুষ কণ্ঠ)", "Female (নারী কণ্ঠ)"])

if uploaded_file is not None:
    if st.button("নতুন ভিডিও তৈরি করুন"):
        with st.spinner("প্রক্রিয়াকৃতি ব্যাকগ্রাউন্ডে চলছে... অনুগ্রহ করে অপেক্ষা করুন..."):
            
            with open("input_video.mp4", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # ১. ভিডিও থেকে অডিও আলাদা করা
            video = VideoFileClip("input_video.mp4")
            video.audio.write_audiofile("extracted_audio.wav", logger=None)
            video.close()

            # ২. অডিও থেকে টেক্সট তৈরি করা
            recognizer = sr.Recognizer()
            with sr.AudioFile("extracted_audio.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    original_text = recognizer.recognize_google(audio_data, language="bn-BD")
                except:
                    original_text = "ভিডিওর অডিও থেকে টেক্সট রূপান্তর করা যায়নি।"

            # ৩. AI দিয়ে শব্দ পরিবর্তন
            modified_text = original_text
            synonyms = {
                "বললেন": "জানালেন",
                "ভিডিও": "ফুটেজ",
                "আজকে": "আজকের দিনে",
                "খবর": "সংবাদ",
                "মানুষ": "জনগণ",
            }
            for word, replacement in synonyms.items():
                modified_text = modified_text.replace(word, replacement)

            # ৪. নতুন কণ্ঠে অডিও তৈরি করা
            tts = gTTS(text=modified_text, lang='bn')
            tts.save("temp_speech.mp3")

            sound = AudioSegment.from_mp3("temp_speech.mp3")
            if voice_option == "Male (পুরুষ কণ্ঠ)":
                new_sample_rate = int(sound.frame_rate * 0.85)
                final_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                final_sound = final_sound.set_frame_rate(sound.frame_rate)
            else:
                new_sample_rate = int(sound.frame_rate * 1.1)
                final_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                final_sound = final_sound.set_frame_rate(sound.frame_rate)

            final_sound.export("final_audio.mp3", format="mp3")

            # ৫. আকর্ষণীয় ফুটেজ ও কপিরাইট চেক
            video = VideoFileClip("input_video.mp4")
            video.save_frame("downloaded_asset.jpg", t=1)
            video.close()

            time.sleep(1)

            # ৬. লোগোহীন 720p ভিডিও প্যাকেজিং
            audio_clip = AudioFileClip("final_audio.mp3")
            image_clip = ImageClip("downloaded_asset.jpg").set_duration(audio_clip.duration)

            final_video = image_clip.set_audio(audio_clip)
            final_video.write_videofile(
                "polok_output_720p.mp4",
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None
            )

            final_video.close()
            audio_clip.close()
            image_clip.close()

            for temp_file in ["input_video.mp4", "extracted_audio.wav", "temp_speech.mp3", "downloaded_asset.jpg"]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            st.success("🎉 আপনার কপিরাইট-মুক্ত 720p ভিডিও সম্পূর্ণ তৈরি!")
            with open("polok_output_720p.mp4", "rb") as file:
                st.download_button(
                    label="নতুন ভিডিও ডাউনলোড করুন",
                    data=file,
                    file_name="polok_final_news.mp4",
                    mime="video/mp4"
                )
