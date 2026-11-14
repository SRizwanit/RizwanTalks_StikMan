# RizwanTalks Intro (Python + React + Remotion + GitHub Actions)

মিনিমালিস্ট স্টিকফিগার ইন্ট্রো। ক্যারেক্টারের নড়াচড়া ক্যাজুয়াল: হালকা শ্বাস-প্রশ্বাস, ছোট ঢেউ-হাত, ধীরে পুশ-ইন।

```
data/script.json  --(python/build_timeline.py [--voice])-->  data/timeline.json (+ public/voice.mp3)
                                                                   |
                                          src/ (React + Remotion) -+-> out/rizwantalks_intro.mp4
```

## লোকালি চালাতে
```bash
npm install
pip install -r python/requirements.txt   # শুধু ভয়েস লাগলে
npm run timeline          # ভয়েস ছাড়া
# npm run timeline:voice  # edge-tts ভয়েস + ক্যাপশন সিঙ্ক
npm run studio            # প্রিভিউ
npm run render            # out/rizwantalks_intro.mp4
```

## GitHub Actions
`.github/workflows/render.yml`: `main`-এ পুশ করলে বা Actions ট্যাব থেকে **Run workflow** (voice অন/অফ) দিলে MP4 তৈরি হয়ে Artifacts-এ আসে।

## কাস্টমাইজ
- টেক্সট/টাইমিং/শট: `data/script.json`
- ক্যারেক্টার ও নড়াচড়া: `src/Character.tsx` (হাত নাড়ার কোণ `0.18` রেডিয়ান; বাড়ালে বেশি নড়বে)
- ক্যাপশন ফন্ট: `src/Caption.tsx` (ইংরেজি Poppins Italic, বাংলার জন্য Noto Sans Bengali)
- বাংলা ভয়েস: `voice.name` = `bn-BD-PradeepNeural`, `say` বাংলায়
- `tools/preview_pillow.py`: Remotion ছাড়া অফলাইন প্রিভিউ রেন্ডারার

## লাইসেন্স নোট
Remotion ব্যক্তিগত/ছোট টিমে ফ্রি; কোম্পানির ব্যবহারে তাদের লাইসেন্স শর্ত দেখুন।
