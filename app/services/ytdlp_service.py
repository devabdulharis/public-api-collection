from __future__ import annotations

from typing import Any
import yt_dlp


def _pick_best_progressive(formats: list[dict[str, Any]]) -> dict[str, Any] | None:
    # progressive = ada video + audio dalam 1 file
    progressive = [
        f for f in formats
        if f.get("vcodec") not in (None, "none")
        and f.get("acodec") not in (None, "none")
        and f.get("url")
    ]
    if not progressive:
        return None

    def score(f: dict[str, Any]) -> tuple:
        # urutkan kira-kira dari kualitas: height, tbr, filesize
        return (
            int(f.get("height") or 0),
            float(f.get("tbr") or 0.0),
            int(f.get("filesize") or 0),
        )

    return sorted(progressive, key=score, reverse=True)[0]


def _pick_best_video_only(formats: list[dict[str, Any]]) -> dict[str, Any] | None:
    video_only = [
        f for f in formats
        if f.get("vcodec") not in (None, "none")
        and (f.get("acodec") in (None, "none"))
        and f.get("url")
    ]
    if not video_only:
        return None

    def score(f: dict[str, Any]) -> tuple:
        return (
            int(f.get("height") or 0),
            float(f.get("tbr") or 0.0),
            int(f.get("filesize") or 0),
        )

    return sorted(video_only, key=score, reverse=True)[0]


def _pick_best_audio_only(formats: list[dict[str, Any]]) -> dict[str, Any] | None:
    audio_only = [
        f for f in formats
        if f.get("acodec") not in (None, "none")
        and (f.get("vcodec") in (None, "none"))
        and f.get("url")
    ]
    if not audio_only:
        return None

    def score(f: dict[str, Any]) -> tuple:
        return (
            float(f.get("abr") or 0.0),
            float(f.get("tbr") or 0.0),
            int(f.get("filesize") or 0),
        )

    return sorted(audio_only, key=score, reverse=True)[0]


def extract_media_info(url: str) -> dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        info = ydl.sanitize_info(info)

    # kalau playlist/hasil pencarian, ambil entry pertama
    if isinstance(info, dict) and info.get("_type") in ("playlist", "multi_video"):
        entries = info.get("entries") or []
        first = next((e for e in entries if e), None)
        if first:
            info = first

    return info


def build_direct_links(info: dict[str, Any]) -> dict[str, Any]:
    formats = info.get("formats") or []

    best_progressive = _pick_best_progressive(formats)
    best_video = _pick_best_video_only(formats)
    best_audio = _pick_best_audio_only(formats)

    return {
        "title": info.get("title"),
        "extractor": info.get("extractor"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "webpage_url": info.get("webpage_url"),
        "direct": {
            "progressive": best_progressive and {
                "url": best_progressive.get("url"),
                "ext": best_progressive.get("ext"),
                "height": best_progressive.get("height"),
                "format_id": best_progressive.get("format_id"),
            },
            "video_only": best_video and {
                "url": best_video.get("url"),
                "ext": best_video.get("ext"),
                "height": best_video.get("height"),
                "format_id": best_video.get("format_id"),
            },
            "audio_only": best_audio and {
                "url": best_audio.get("url"),
                "ext": best_audio.get("ext"),
                "abr": best_audio.get("abr"),
                "format_id": best_audio.get("format_id"),
            },
        },
        "note": "Direct URL biasanya punya masa berlaku (expired). Kalau 403/expired, panggil ulang endpoint ini.",
    }