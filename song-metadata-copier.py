import os
import io
import shutil
import zipfile
import streamlit as st
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3

st.set_page_config(page_title="Track Metadata Transfer", layout="centered")

st.title("🎶 Song Metadata Transfer Tool")

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_tags(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".mp3":
        return EasyID3(path), "mp3"
    elif ext == ".flac":
        return FLAC(path), "flac"
    return None, None


def apply_metadata(source_tags, target_path, album_override=None, delete_track_number=True):
    target_tags, _ = load_tags(target_path)
    if not target_tags:
            return

    # Fields intentionally copied as-is
    fields = [
        "title",
        "artist",
        "album",
        "genre",
        "composer",
        "albumartist",
        "date",
        "tracknumber",
    ]

    for f in fields:
        if f in source_tags:
            if f == "tracknumber" and delete_track_number:
                continue
            target_tags[f] = source_tags[f]

    if album_override:
        target_tags["album"] = album_override

    target_tags.save()


def auto_zip_and_download(files, label):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            zipf.write(f, os.path.basename(f))
    buffer.seek(0)

    st.download_button(
        label="Download",
        data=buffer,
        file_name=f"{label.replace(' ','_').lower()}.zip",
        mime="application/zip",
        use_container_width=True
    )


# --------------------------------------------------
# Mode Selector
# --------------------------------------------------

mode = st.radio(
    "Choose transfer mode",
    ["Single Song Transfer", "Multiple Songs Transfer"],
    horizontal=True
)

st.divider()

# ==================================================
# SINGLE SONG MODE
# ==================================================

if mode == "Single Song Transfer":

    st.subheader("Single Song Transfer")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            original_file = st.file_uploader(
                "Original song",
                type=["mp3", "flac"],
                key="single_original"
            )

        with col2:
            target_file = st.file_uploader(
                "Song to receive metadata",
                type=["mp3", "flac"],
                key="single_target"
            )

        st.markdown("#### Settings")

        album_override = st.text_input(
            "New album name (optional)",
            placeholder="Leave blank to keep existing album"
        )

        delete_track_number = st.checkbox(
            "Remove track number",
            value=True
        )

        delete_original = st.checkbox(
            "Delete original song after processing",
            value=False
        )

        if original_file and target_file:
            temp_dir = "temp_single"
            os.makedirs(temp_dir, exist_ok=True)

            original_path = os.path.join(temp_dir, original_file.name)
            target_path = os.path.join(temp_dir, target_file.name)

            with open(original_path, "wb") as f:
                f.write(original_file.read())

            with open(target_path, "wb") as f:
                f.write(target_file.read())

            source_tags, _ = load_tags(original_path)
            apply_metadata(source_tags, target_path, album_override, delete_track_number)

            if delete_original:
                os.remove(original_path)

            st.success("Metadata transferred")

            with open(target_path, "rb") as f:
                file_bytes = f.read()

            ext = os.path.splitext(target_path)[1].lower()
            mime = "audio/mpeg" if ext == ".mp3" else "audio/flac"

            st.download_button(
                label="Download",
                data=file_bytes,
                file_name=os.path.basename(target_path),
                mime=mime,
                use_container_width=True
            )

            shutil.rmtree(temp_dir)


# ==================================================
# MULTIPLE SONG MODE
# ==================================================

if mode == "Multiple Songs Transfer":

    st.subheader("Multiple Songs Transfer")

    with st.container(border=True):
        originals = st.file_uploader(
            "Original songs (reference metadata)",
            type=["mp3", "flac"],
            accept_multiple_files=True,
            key="batch_originals"
        )

        targets = st.file_uploader(
            "Songs to update",
            type=["mp3", "flac"],
            accept_multiple_files=True,
            key="batch_targets"
        )

        st.markdown("#### Settings")

        album_override_batch = st.text_input(
            "New album name for all songs (optional)",
            placeholder="Leave blank to keep existing album names"
        )

        delete_track_number_batch = st.checkbox(
            "Remove track numbers",
            value=True
        )

        delete_originals = st.checkbox(
            "Delete original songs after processing",
            value=False
        )

        if originals and targets:
            temp_dir = "temp_batch"
            os.makedirs(temp_dir, exist_ok=True)

            processed_files = []

            st.markdown("#### Match Results")

            for orig in originals:
                orig_path = os.path.join(temp_dir, orig.name)
                with open(orig_path, "wb") as f:
                    f.write(orig.read())

                source_tags, _ = load_tags(orig_path)
                if not source_tags:
                    continue

                base_name = os.path.splitext(orig.name)[0].lower()

                matches = [
                    t for t in targets
                    if base_name in os.path.splitext(t.name)[0].lower()
                ]

                if matches:
                    st.write(f"✔ **{orig.name}** matched {len(matches)} file(s)")
                else:
                    st.write(f"⚠ No match for **{orig.name}**")

                for t in matches:
                    t_path = os.path.join(temp_dir, t.name)
                    with open(t_path, "wb") as f:
                        f.write(t.read())

                    apply_metadata(
                        source_tags,
                        t_path,
                        album_override_batch,
                        delete_track_number_batch
                    )

                    processed_files.append(t_path)

                if delete_originals:
                    os.remove(orig_path)

            if processed_files:
                st.success("Batch processing complete")
                auto_zip_and_download(processed_files, "batch_results")

            shutil.rmtree(temp_dir)