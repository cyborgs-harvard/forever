from yt_dlp import YoutubeDL

ydl_opts = {
    "skip_download": True,
    "writesubtitles": True,
    "subtitleslangs": ["en", "-live_chat"],
    # Looks like formats available are vtt, ttml, srv3, srv2, srv1, json3
    "subtitlesformat": "json3",
    # You can skip the following option
    "sleep_interval_subtitles": 1,
}
with YoutubeDL(ydl_opts) as ydl:
    ydl.download(["16Ci_2bN_zc"])
