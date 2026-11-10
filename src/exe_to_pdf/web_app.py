from __future__ import annotations

import streamlit as st

from exe_to_pdf.converters import ConversionError, convert, edit_image, output_name


CONVERSIONS = {
    "JPG_TO_PNG": "JPG → PNG",
    "JPG_TO_WEBP": "JPG → WEBP",
    "JPG_TO_PDF": "JPG → PDF",
    "PNG_TO_JPG": "PNG → JPG",
    "PNG_TO_WEBP": "PNG → WEBP",
    "PNG_TO_PDF": "PNG → PDF",
    "WEBP_TO_JPG": "WEBP → JPG",
    "WEBP_TO_PNG": "WEBP → PNG",
    "WEBP_TO_PDF": "WEBP → PDF",
    "PDF_TO_JPG": "PDF → JPG",
    "PDF_TO_PNG": "PDF → PNG",
    "PDF_TO_DOCX": "PDF → DOCX",
    "PDF_TO_XLSX": "PDF → Excel",
    "TXT_TO_PDF": "TXT → PDF",
    "CSV_TO_PDF": "CSV → PDF",
    "EXE_TO_PDF": "EXE Vaysoft → PDF",
    "REMOVE_BG": "Hapus background foto",
    "REPLACE_BG_COLOR": "Ganti background warna",
    "REPLACE_BG_IMAGE": "Ganti background foto",
}


def _icon(name: str, label: str = "", class_name: str = "icon") -> str:
    aria = f' aria-label="{label}"' if label else ' aria-hidden="true"'
    return f'<svg class="{class_name}" viewBox="0 0 48 48" role="img"{aria}><use href="#i-{name}"></use></svg>'


def _icon_sprite() -> str:
    return """
    <svg class="icon-sprite" aria-hidden="true">
      <defs>
        <symbol id="i-convert" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 19a13 13 0 0 1 22-5l3 3M36 13v7h-7M36 29a13 13 0 0 1-22 5l-3-3M12 35v-7h7" stroke="currentColor" stroke-width="6" opacity=".8" transform="translate(2.5 2.5)"/>
          <path d="M12 19a13 13 0 0 1 22-5l3 3"/><path d="M36 13v7h-7"/>
          <path d="M36 29a13 13 0 0 1-22 5l-3-3"/><path d="M12 35v-7h7"/>
        </symbol>
        <symbol id="i-upload" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 34h28a7 7 0 0 0-3-13 12 12 0 0 0-23-1 7 7 0 0 0-2 14z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M10 34h28a7 7 0 0 0-3-13 12 12 0 0 0-23-1 7 7 0 0 0-2 14z" fill="#EAF2FF"/>
          <path d="M24 28V15m0 0-5 5m5-5 5 5"/><g class="face-eyes"><circle cx="19" cy="31" r="1" fill="#1B1B1F" stroke="none"/><circle cx="29" cy="31" r="1" fill="#1B1B1F" stroke="none"/></g>
          <path d="M21 34q3 2 6 0" />
        </symbol>
        <symbol id="i-file" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8h17l8 8v24H12z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M12 8h17l8 8v24H12z" fill="#EAF2FF"/><path d="M29 8v8h8"/>
          <g class="face-eyes"><circle cx="20" cy="26" r="1.6" fill="#1B1B1F" stroke="none"/><circle cx="29" cy="26" r="1.6" fill="#1B1B1F" stroke="none"/></g><path d="M22 30q2.5 2.5 5 0"/>
        </symbol>
        <symbol id="i-download" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M24 9v20m0 0-7-7m7 7 7-7M12 35h24" stroke="currentColor" stroke-width="6" transform="translate(2.5 2.5)"/>
          <path d="M24 9v20m0 0-7-7m7 7 7-7M12 35h24"/><g class="face-eyes"><circle cx="19" cy="39" r="1.3" fill="#1B1B1F" stroke="none"/><circle cx="29" cy="39" r="1.3" fill="#1B1B1F" stroke="none"/></g>
        </symbol>
        <symbol id="i-success" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="m10 25 8 9 20-20" stroke="currentColor" stroke-width="7" transform="translate(2.5 2.5)"/><path d="m10 25 8 9 20-20"/>
          <path d="m18 35q6 4 12 0" />
        </symbol>
        <symbol id="i-settings" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 9h8l1 5 4 2 4-2 5 6-4 4v5l4 4-5 6-4-2-4 2-1 5h-8l-1-5-4-2-4 2-5-6 4-4v-5l-4-4 5-6 4 2 4-2z" fill="#FFD4E4" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M20 9h8l1 5 4 2 4-2 5 6-4 4v5l4 4-5 6-4-2-4 2-1 5h-8l-1-5-4-2-4 2-5-6 4-4v-5l-4-4 5-6 4 2 4-2z"/><circle cx="24" cy="26" r="5"/>
        </symbol>
        <symbol id="i-menu" viewBox="0 0 48 48" fill="#1B1B1F"><circle cx="24" cy="12" r="3"/><circle cx="24" cy="24" r="4"/><circle cx="24" cy="36" r="3"/></symbol>
        <symbol id="i-history" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="24" cy="25" r="14" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/><circle cx="24" cy="25" r="14" fill="#FFF2DE"/><path d="M24 17v8l5 3"/><path d="M11 16v-6h6"/>
        </symbol>
        <symbol id="i-delete" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 15h20l-2 25H16z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M14 15h20l-2 25H16z" fill="#FFD4E4"/><path d="M12 13h24M19 13V9h10v4"/>
          <circle cx="27" cy="22" r="1.8" fill="#1B1B1F" stroke="none"/>
        </symbol>
        <symbol id="i-failed" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="m15 15 18 18m0-18L15 33" stroke="currentColor" stroke-width="6" transform="translate(2.5 2.5)"/>
          <path d="m15 15 18 18m0-18L15 33"/><path d="M20 37q4-3 8 0"/>
        </symbol>
        <symbol id="i-streak" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M24 40c-10 0-14-7-10-14 2-3 5-5 5-12 8 4 13 10 13 17 0 5-3 9-8 9z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M24 40c-10 0-14-7-10-14 2-3 5-5 5-12 8 4 13 10 13 17 0 5-3 9-8 9z" fill="#FFD4A8"/>
          <circle cx="27" cy="27" r="1.5" fill="#1B1B1F" stroke="none"/>
        </symbol>
        <symbol id="i-level" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 18 7 3 5-9 5 9 7-3-2 20H14z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="m12 18 7 3 5-9 5 9 7-3-2 20H14z" fill="#FFF0A8"/><path d="M14 38h20"/>
          <g class="face-eyes"><circle cx="20" cy="28" r="1.4" fill="#1B1B1F" stroke="none"/><circle cx="28" cy="28" r="1.4" fill="#1B1B1F" stroke="none"/></g><path d="M21 32q3 2 6 0"/>
        </symbol>
        <symbol id="i-theme" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="24" r="8" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/><circle cx="18" cy="24" r="8" fill="#FFF0A8"/>
          <path d="M18 13v-3m0 25v-3m-8-8H7m25 0h-3M12 18l-2-2m20 16-2-2"/>
          <path d="M34 14a10 10 0 1 0 0 20 8 8 0 0 1 0-20z" fill="#C8D5F6"/><path d="M15 25q3 3 6 0"/>
        </symbol>
        <symbol id="i-tool" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 14h18l7 7v17H10z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
          <path d="M10 14h18l7 7v17H10z" fill="#D9C8FF"/><path d="M28 14v7h7"/><path d="M15 29h15"/>
        </symbol>
      </defs>
    </svg>
    """


def _style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        :root { --ink: #14213d; --muted: #52627d; --line: #cbd6e6; --blue: #1f63d1; }
        .icon-sprite { position: absolute; width: 0; height: 0; overflow: hidden; }
        .icon { width: 1.5rem; height: 1.5rem; display: inline-block; vertical-align: middle; flex: 0 0 auto; }
        .icon-button .icon, .brand-mark .icon { width: 1.35rem; height: 1.35rem; }
        .icon:hover { animation: icon-wiggle .3s ease-in-out; }
        .icon-button { display: inline-grid; place-items: center; border: 0; background: transparent; padding: .2rem; }
        @keyframes icon-wiggle { 0%, 100% { transform: rotate(0); } 50% { transform: rotate(-6deg); } }
        @keyframes icon-pop { 0% { transform: scale(.9); } 70% { transform: scale(1.1); } 100% { transform: scale(1); } }
        @keyframes face-blink { 0%, 92%, 100% { transform: scaleY(1); } 95% { transform: scaleY(.1); } }
        .face-eyes { transform-box: fill-box; transform-origin: center; animation: face-blink 6s ease-in-out infinite; }
        button:active .icon, a:active .icon { animation: icon-pop .2s ease-out; }
        @media (prefers-reduced-motion: reduce) { .icon, .face-eyes { animation: none !important; } }
        .stApp { background: #f5f8fe;
                 color: var(--ink); font-family: 'DM Sans', sans-serif; }
        .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {
            color: var(--ink) !important;
        }
        header, [data-testid="stHeader"] { background: transparent; visibility: visible; }
        [data-testid="stDecoration"], [data-testid="stStatusWidget"],
        [data-testid="stAppDeployButton"], [data-testid="stBaseButton-header"],
        [data-testid="stMainMenuButton"], #MainMenu, footer {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            visibility: visible !important;
            opacity: 1 !important;
        }
        button[aria-label="Collapse sidebar"], button[aria-label="Expand sidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 100001 !important;
            color: #174f9f !important;
        }
        button[aria-label="Collapse sidebar"] {
            position: fixed !important;
            top: .65rem !important;
            left: .65rem !important;
            background: #e0edff !important;
            border: 1px solid #a9c5ed !important;
            border-radius: 4px !important;
        }
        button[aria-label="Expand sidebar"] {
            position: fixed !important;
            top: .65rem !important;
            left: .65rem !important;
            background: #1f63d1 !important;
            border: 1px solid #124fae !important;
            border-radius: 4px !important;
            color: #fff !important;
        }
        [data-testid="stSidebar"] { background: transparent; border-right: 0; }
        [data-testid="stSidebar"] > div:first-child { padding: 1rem .7rem; }
        [data-testid="stSidebar"] > div:first-child { background: #fff; border: 1px solid #cbd6e6;
                 border-radius: 4px; padding: 1.25rem .9rem; box-shadow: 0 12px 35px #50658f18; }
        [data-testid="stSidebar"] > div:first-child > div { background: transparent; padding: 0; }
        [data-testid="stSidebar"] * { color: var(--ink) !important; }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
        [data-testid="stSidebar"] hr { border-color: var(--line); margin: 1.4rem 0; }
        [data-testid="stSidebar"] label { color: var(--muted) !important; font-size: .78rem; }
        [data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
        [data-testid="stSidebar"] [role="radio"] { position: relative; padding: .7rem .75rem .7rem 2.15rem; border-radius: 4px; color: #263754 !important; }
        [data-testid="stSidebar"] [role="radio"]:hover { background: #f6f8fc; }
        [data-testid="stSidebar"] [role="radio"]:before { content: ''; position: absolute; left: .75rem; top: 50%;
                 width: .72rem; height: .72rem; transform: translateY(-50%); border: 2px solid #8b9bb3;
                 border-radius: 2px; background: #fff; box-sizing: border-box; }
        [data-testid="stSidebar"] [role="radio"]:has(input:checked) { background: #e4efff; color: #124fae !important; font-weight: 700; }
        [data-testid="stSidebar"] [role="radio"]:has(input:checked):before { border-color: #1f63d1; background: #1f63d1;
                 box-shadow: inset 0 0 0 2px #e4efff; }
        [data-testid="stSidebar"] [role="radio"] > div:first-child { display: none; }
        .block-container { max-width: 1180px; padding: 1rem 1.5rem 3rem; }
        .brand { display: flex; align-items: center; gap: .65rem; margin-bottom: .35rem; }
        .brand-mark { display: grid; place-items: center; width: 30px; height: 30px;
                      background: #1f63d1; color: white; border-radius: 4px; font-weight: 700; }
        .brand-name { color: var(--ink); font-size: 1.05rem; font-weight: 700; }
        .brand-subtitle { color: var(--muted); font-size: .73rem; line-height: 1.45; margin: .55rem 0 1.35rem; }
        .privacy-card { margin-top: 1.2rem; padding: .8rem; background: #edf4ff; border: 1px solid #c4d9f7;
                        border-radius: 4px; color: #29456d; font-size: .7rem; line-height: 1.45; }
        .hero { position: relative; overflow: hidden; background: #fff; color: var(--ink);
                padding: 1.15rem 1.35rem; border-radius: 4px; margin: .1rem 0 .85rem;
                border: 1px solid var(--line); box-shadow: 0 8px 26px #1e315b0b; }
        .hero h1 { position: relative; z-index: 1; margin: 0; font-size: 1.3rem; letter-spacing: -.035em; }
        .hero p { position: relative; z-index: 1; margin: .35rem 0 0; color: var(--muted) !important; font-size: .88rem; }
        .welcome-line { display: flex; align-items: center; gap: .45rem; margin-bottom: .8rem; color: #174f9f;
                        font-size: .76rem; font-weight: 700; }
        .welcome-line .icon { width: 1.15rem; height: 1.15rem; }
        .hero-tip { display: inline-flex; align-items: center; gap: .45rem; margin-top: .9rem; padding: .45rem .65rem;
                    background: #edf5ff; border: 1px solid #c8dcf7; border-radius: 4px; color: #315783;
                    font-size: .72rem; }
        .hero-tip .icon { width: 1rem; height: 1rem; }
        .eyebrow { color: #1769e0; text-transform: uppercase; letter-spacing: .12em; font-size: .68rem;
                   font-weight: 700; margin-bottom: .65rem; }
        .section-title { margin: .35rem 0 .25rem; font-size: 1.15rem; letter-spacing: -.025em; font-weight: 600; }
        .section-copy { color: var(--muted) !important; font-size: .88rem; margin-bottom: 1rem; }
        .panel { background: white; border: 1px solid var(--line); border-radius: 4px; padding: 1.15rem 1.2rem;
                 box-shadow: 0 10px 28px #1720330b; height: 100%; }
        [data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border-color: var(--line);
                 border-radius: 4px; box-shadow: 0 6px 24px #17203308; }
        [data-testid="stVerticalBlockBorderWrapper"] > div { background: #fff; border-radius: 4px; }
        .panel h3 { margin: 0 0 .25rem; font-size: 1.05rem; }
        .format-list { display: flex; flex-wrap: wrap; gap: .45rem; margin: 1rem 0 1.1rem; }
        .format-chip { background: #e0edff; color: #174f9f; border: 1px solid #a9c5ed; border-radius: 4px;
                       padding: .4rem .62rem; font-size: .78rem; font-weight: 600; }
        .note { background: #fff3cf; color: #634900; border: 1px solid #e8c96c; border-radius: 4px;
                padding: .75rem .85rem; font-size: .78rem; line-height: 1.45; }
        .promo { min-height: 150px; color: white; border-radius: 4px; padding: 1.15rem;
                 background: #4169e1; box-shadow: 0 12px 24px #4169e12b; }
        .promo h3 { color: white; margin: .65rem 0 .3rem; font-size: 1.08rem; }
        .promo p { color: #eafcff !important; font-size: .76rem; margin: 0 0 .8rem; }
        .promo-tag { display: inline-block; background: #fff; color: #153fa4; padding: .25rem .45rem;
                     border-radius: 4px; font-size: .6rem; font-weight: 700; }
        .history-title { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0 .55rem; }
        .history-title h3 { margin: 0; font-size: 1rem; }
        .history-title span { color: var(--muted); font-size: .75rem; }
        .history-row { display: flex; align-items: center; gap: .65rem; background: #fff; border: 1px solid var(--line);
                       border-radius: 4px; padding: .65rem .75rem; margin: .4rem 0; }
        .file-badge { display: grid; place-items: center; width: 27px; height: 27px; border-radius: 4px;
                      background: #edf4ff; color: #1769e0; font-weight: 700; font-size: .7rem; }
        .file-name { flex: 1; font-size: .78rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .file-status { color: #3b9b68; font-size: .68rem; }
        .recommend { background: #fff; border: 1px solid var(--line); border-radius: 4px; padding: .75rem; }
        .recommend strong { font-size: .8rem; }
        .recommend p { color: var(--muted) !important; font-size: .68rem; margin: .25rem 0 0; }
        .return-card { display: grid; grid-template-columns: auto 1fr; gap: .7rem; align-items: center;
                       margin: 1rem 0 0; padding: .85rem 1rem; background: #fff7df; border: 1px solid #eed487;
                       border-radius: 4px; }
        .return-card .icon-box { display: grid; place-items: center; width: 32px; height: 32px;
                                 background: #ffe4a3; color: #8a5b00; border-radius: 4px; }
        .return-card .icon { width: 1.25rem; height: 1.25rem; }
        .return-card strong { display: block; color: #624600; font-size: .78rem; }
        .return-card span { display: block; margin-top: .15rem; color: #806a36; font-size: .7rem; }
        .upload-hint { display: flex; align-items: center; gap: .6rem; color: #718096; font-size: .8rem;
                       margin-top: .55rem; }
        .upload-icon { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 4px;
                       background: #dceaff; color: #1f63d1; font-size: 1rem; }
        .result-heading { display: flex; align-items: center; justify-content: space-between; margin: 1.7rem 0 .8rem; }
        .result-heading h2 { margin: 0; font-size: 1.25rem; letter-spacing: -.02em; }
        .stSelectbox label, .stFileUploader label { color: #556277; font-size: .78rem; font-weight: 600; }
        .stSelectbox > div > div { border-color: #aebed3; border-radius: 4px; background: #fff; }
        [data-baseweb="select"] * { color: var(--ink) !important; }
        [data-testid="stFileUploader"] { border: 1.5px dashed #7899c7; border-radius: 4px; background: #eef5ff; padding: .3rem; }
        [data-testid="stFileUploaderDropzone"] { background: transparent; border: 0; }
        [data-testid="stFileUploader"] button {
            border-radius: 4px; border-color: #8eadd9; color: #124fae !important;
            background: #fff !important;
        }
        [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] { color: #718096 !important; }
        [data-testid="stFileUploaderFile"] { background: #e5eefb; border-radius: 4px; }
        .stAlert { border-radius: 4px; }
        div.stDownloadButton > button { border-radius: 4px; background: #1f63d1; color: white; border: 0; }
        div.stDownloadButton > button:hover { background: #245bc8; color: white; }
        @media (max-width: 800px) {
            .stApp { background: #f7f9fc; }
            [data-testid="stSidebar"] > div:first-child { border-radius: 0 0 4px 4px; }
            .block-container { padding: 1.5rem 1rem 3rem; }
            .hero { padding: 1.6rem; }
            .hero h1 { font-size: 1.7rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Convertly", page_icon="C", layout="wide")
    _style()
    st.markdown(_icon_sprite(), unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(
            f'<div class="brand"><div class="brand-mark">{_icon("convert")}</div><div class="brand-name">Convertly</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="brand-subtitle">Konversi file sederhana,<br>cepat, dan aman.</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("Menu", ["Home", "Semua konversi", "Tentang"], label_visibility="collapsed")
        st.markdown(
            '<div class="privacy-card"><strong>Privasi terjaga</strong><br>'
            'File diproses di komputer ini dan tidak dikirim ke server.</div>',
            unsafe_allow_html=True,
        )

    if page == "Tentang":
        st.markdown('<div class="eyebrow">Tentang aplikasi</div>', unsafe_allow_html=True)
        st.title("Konversi lokal yang aman")
        st.write("Konverter lokal untuk gambar, PDF, dokumen, dan spreadsheet.")
        st.info("EXE buatan Vaysoft PDF to EXE dapat dikembalikan ke PDF asli tanpa menjalankan programnya.")
        return

    st.markdown(
        f'<div class="hero"><div class="welcome-line">{_icon("streak")} Ruang konversimu sudah siap</div>'
        '<div class="eyebrow">Fast convert</div>'
        '<h1>Konversi file jadi lebih mudah</h1>'
        "<p>Ubah gambar, PDF, teks, dan dokumen ke format yang kamu perlukan.</p>"
        f'<div class="hero-tip">{_icon("success")} Satu file masuk, satu hasil rapi keluar.</div></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.45, .8], gap="medium")
    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">Mulai konversi</div>'
                '<div class="section-copy">Pilih pasangan format yang jelas, lalu tambahkan file yang sesuai.</div>',
                unsafe_allow_html=True,
            )
            target = st.selectbox("Jenis konversi", list(CONVERSIONS), format_func=lambda key: CONVERSIONS[key])
            if target == "REPLACE_BG_COLOR":
                background_color = st.color_picker("Warna background baru", "#E8F1FF")
            elif target == "REPLACE_BG_IMAGE":
                st.caption("Upload foto utama terlebih dahulu, lalu foto yang akan menjadi background.")
                background_color = None
            else:
                background_color = None
            uploaded = st.file_uploader(
                "Klik atau tarik file ke sini",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "csv", "exe"],
            )
            st.markdown(
                f'<div class="upload-hint"><span class="upload-icon">{_icon("upload")}</span>'
                '<span>Maksimal 200 MB per file · Pemrosesan berlangsung di perangkatmu</span></div>',
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(
            f'<div class="promo"><span class="promo-tag">NEW FEATURE</span><h3>{_icon("tool")} AI Converter</h3>'
            '<p>Ubah file kamu lebih cepat dengan workflow konversi yang praktis.</p>'
            '<span class="promo-tag">Try now</span></div>'
            '<div class="history-title"><h3>Format didukung</h3><span>8 format</span></div>'
            '<div class="panel"><div class="format-list"><span class="format-chip">PNG</span><span class="format-chip">JPG</span>'
            '<span class="format-chip">JPEG</span><span class="format-chip">WEBP</span>'
            '<span class="format-chip">PDF</span><span class="format-chip">TXT</span><span class="format-chip">CSV</span>'
            '<span class="format-chip">EXE</span></div>'
            '<p class="section-copy">Pilih format asal dan tujuan secara langsung agar tidak salah.</p>'
            '<div class="note"><strong>Catatan:</strong> Converter ini mendukung EXE buatan '
            'Vaysoft PDF to EXE dan mengambil PDF aslinya tanpa menjalankan program.</div></div>',
            unsafe_allow_html=True,
        )

    if not uploaded:
        st.markdown(
            '<div class="history-title"><h3>Recommended tools</h3><span>View all</span></div>',
            unsafe_allow_html=True,
        )
        tool_a, tool_b = st.columns(2)
        with tool_a:
            st.markdown(
                f'<div class="recommend">{_icon("file")} <strong>JPG to PDF</strong>'
                '<p>Convert any JPG files to PDF format</p></div>',
                unsafe_allow_html=True,
            )
        with tool_b:
            st.markdown(
                f'<div class="recommend">{_icon("file")} <strong>PDF to DOCX</strong>'
                '<p>Extract PDF text into an editable document</p></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="return-card"><div class="icon-box">{_icon("level")}</div>'
            '<div><strong>Besok mampir lagi, ya.</strong>'
            '<span>Convertly akan tetap jadi tempat kecil yang rapi untuk file-filemu.</span></div></div>',
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        '<div class="history-title"><h3>Hasil konversi</h3>'
        '<span>File siap diunduh</span></div>',
        unsafe_allow_html=True,
    )
    for item_index, item in enumerate(uploaded):
        try:
            if target in {"REMOVE_BG", "REPLACE_BG_COLOR", "REPLACE_BG_IMAGE"}:
                if target == "REPLACE_BG_IMAGE":
                    if len(uploaded) != 2:
                        raise ConversionError("Upload tepat 2 gambar: foto utama dan background baru.")
                    result, extension, mime = edit_image(
                        uploaded[0].getvalue(),
                        target,
                        uploaded[1].getvalue(),
                    )
                    if item_index != 0:
                        continue
                else:
                    result, extension, mime = edit_image(
                        item.getvalue(),
                        target,
                        background_color=background_color or "#E8F1FF",
                    )
            else:
                result, extension, mime = convert(item.getvalue(), item.name, target)
        except ConversionError as error:
            st.error(f"{item.name}: {error}")
            continue
        st.success(f"{item.name} berhasil dikonversi")
        st.download_button(
            f"Download {output_name(item.name, extension)}",
            data=result,
            file_name=output_name(item.name, extension),
            mime=mime,
            key=f"{item.name}-{target}",
        )


if __name__ == "__main__":
    main()
