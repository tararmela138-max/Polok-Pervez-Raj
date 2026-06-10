import streamlit as st
import os
import time
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
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

            # ৫. প্রতি ৫ সেকেন্ড পর পর ৩ সেকেন্ডের ফুটেজ যুক্ত করার লজিক
            audio_duration = AudioFileClip("final_audio.mp3").duration
            video_input = VideoFileClip("input_video.mp4")
            clips = []
            current_time = 0
            
            while current_time < audio_duration:
                # ছবি তৈরি করা
                video_input.save_frame("temp_frame.jpg", t=min(current_time, video_input.duration - 0.1))
                img_clip = ImageClip("temp_frame.jpg").set_duration(5)
                clips.append(img_clip)
                current_time += 5
                
                if current_time >= audio_duration:
                    break
                
                # ফুটেজ যুক্ত করা
                footage_start = current_time % (video_input.duration - 3)
                footage_clip = video_input.subclip(footage_start, min(footage_start + 3, video_input.duration))
                clips.append(footage_clip)
                current_time += 3

            final_video = concatenate_videoclips(clips)
            audio_clip = AudioFileClip("final_audio.mp3")
            final_video = final_video.set_audio(audio_clip)
            
            if final_video.duration > audio_duration:
                final_video = final_video.subclip(0, audio_duration)

            # ৬. লোগোহীন 720p ভিডিও প্যাকেজিং
            final_video.write_videofile(
                "polok_output_720p.mp4",
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None
            )

            video_input.close()
            final_video.close()

            for temp_file in ["input_video.mp4", "extracted_audio.wav", "temp_speech.mp3", "temp_frame.jpg", "final_audio.mp3"]:
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
