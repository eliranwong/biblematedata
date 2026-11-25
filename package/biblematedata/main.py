import os, re, zipfile, gdown, time, random, requests, shutil
from collections import defaultdict
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog
from pathlib import Path

GITHUB_REPO = "eliranwong/biblematedata"
GITHUB_BRANCH = "main"
GITHUB_DATA_PREFIX = "biblemate/data/"


AUDIO_REPOS = {
    "ASV (American accent; verse-by-verse)": ("BBE", "eliranwong/MP3_AmericanStandardVersion_american", "default"),
    "BBE (British accent; verse-by-verse)": ("BBE", "eliranwong/MP3_BibleInBasicEnglish_british", "default"),
    "BHS5 (Hebrew; word-by-word)": ("BHS5", "eliranwong/MP3_BHS5_word-by-word", "default"),
    "BSB (American accent; verse-by-verse)": ("BSB", "eliranwong/MP3_BereanStudyBible_american", "default"),
    "BSB (British accent; verse-by-verse)": ("BSB", "eliranwong/MP3_BereanStudyBible_british", "default"),
    "CUV (Cantonese; verse-by-verse)": ("CUV", "eliranwong/MP3_ChineseUnionVersion_cantonese", "default"),
    "CUVs (Mandarin; verse-by-verse)": ("CUVs", "eliranwong/MP3_ChineseUnionVersion_mandarin", "default"),
    "ERV (British accent; verse-by-verse)": ("ERV", "eliranwong/MP3_EnglishRevisedVersion_british", "default"),
    "ISV (American accent; verse-by-verse)": ("ISV", "eliranwong/MP3_InternationalStandardVersion_american", "default"),
    "ISV (British accent; verse-by-verse)": ("ISV", "eliranwong/MP3_InternationalStandardVersion_british", "default"),
    "KJV (American accent; verse-by-verse)": ("KJV", "eliranwong/MP3_KingJamesVersion_american", "default"),
    "KJV (British accent; verse-by-verse)": ("KJV", "eliranwong/MP3_KingJamesVersion_british", "default"),
    "LEB (American accent; verse-by-verse)": ("LEB", "eliranwong/MP3_LexhamEnglishBible_american", "default"),
    "LEB (British accent; verse-by-verse)": ("LEB", "eliranwong/MP3_LexhamEnglishBible_british", "default"),
    "NET (American accent; verse-by-verse)": ("NET", "eliranwong/MP3_NewEnglishTranslation_american", "default"),
    "NET (British accent; verse-by-verse)": ("NET", "eliranwong/MP3_NewEnglishTranslation_british", "default"),
    "OGNT (Greek; word-by-word)": ("OGNT", "eliranwong/MP3_OpenGNT_word-by-word", "default"),
    "OHGB (Hebrew & Greek; fast; verse-by-verse)": ("OHGB", "eliranwong/MP3_OpenHebrewGreekBible_fast", "default"),
    "OHGB (Hebrew & Greek; slow; verse-by-verse)": ("OHGB", "eliranwong/MP3_OpenHebrewGreekBible_slow", "default"),
    "SBLGNT (Greek; fast; verse-by-verse)": ("SBLGNT", "eliranwong/MP3_SBLGNT_fast", "default"),
    "SBLGNT (Greek; slow; verse-by-verse)": ("SBLGNT", "eliranwong/MP3_SBLGNT_slow", "default"),
    "WEB (British accent; verse-by-verse)": ("WEB", "eliranwong/MP3_WebEnglishBible_british", "default"), 
    "WLC (Hebrew; fast; verse-by-verse)": ("WLC", "eliranwong/MP3_WLC_fast", "default"),
    "WLC (Hebrew; slow; verse-by-verse)": ("WLC", "eliranwong/MP3_WLC_slow", "default"),
}

FILE_IDS = {
    # podcast - new (kept on Google Drive due to large number of files)
    "podcast": ((), "1aNS8rtdQcTZGub6jhZhEarpUK3R4f_x8"),
    # audio (via git clone)
}

_PART_RE = re.compile(r"^(.*\.zip)(?:\.part(\d+))?$")


def list_github_data_archives(repo=GITHUB_REPO, branch=GITHUB_BRANCH, prefix=GITHUB_DATA_PREFIX):
    """Fetch the file tree from GitHub and group .zip / .zip.partNNN blobs by target path."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    headers = {"User-Agent": "biblematedata"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    grouped = defaultdict(list)
    for item in data.get("tree", []):
        if item.get("type") != "blob":
            continue
        blob_path = item.get("path", "")
        if not blob_path.startswith(prefix):
            continue
        rel_blob = blob_path[len(prefix):]
        m = _PART_RE.match(rel_blob)
        if not m:
            continue
        zip_rel = m.group(1)
        part_num = int(m.group(2)) if m.group(2) else 0
        grouped[zip_rel].append((part_num, blob_path))

    for zip_rel in grouped:
        grouped[zip_rel].sort(key=lambda x: x[0])
    return dict(sorted(grouped.items()))


def download_github_file(blob_path, dest_file, mode="wb", repo=GITHUB_REPO, branch=GITHUB_BRANCH, retries=3):
    """Stream-download a single raw file from GitHub with retries."""
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{blob_path}"
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(dest_file, mode) as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
            return
        except Exception as e:
            if attempt == retries:
                raise
            print(f"Attempt {attempt} failed for {blob_path}: {e}. Retrying...")
            time.sleep(3 * attempt)


def download_github_data(data_root=None, force=False):
    """Download and unzip all database archives from GitHub into ~/biblemate/data."""
    if data_root is None:
        data_root = os.path.join(os.path.expanduser("~"), "biblemate", "data")
    Path(data_root).mkdir(parents=True, exist_ok=True)

    print(f"Fetching file list from https://github.com/{GITHUB_REPO} ...")
    archives = list_github_data_archives()
    total = len(archives)
    print(f"Found {total} data files.")

    for idx, (zip_rel, parts) in enumerate(archives.items(), 1):
        target_rel = zip_rel[:-4]  # strip .zip
        final_path = os.path.join(data_root, target_rel)
        target_folder = os.path.dirname(final_path)
        Path(target_folder).mkdir(parents=True, exist_ok=True)

        if os.path.exists(final_path):
            if force:
                os.remove(final_path)
            else:
                print(f"[{idx}/{total}] {final_path} already exists.")
                continue

        tmp_zip = os.path.join(data_root, zip_rel)
        if os.path.isfile(tmp_zip):
            os.remove(tmp_zip)

        try:
            print(f"[{idx}/{total}] Downloading {target_rel} ...")
            for part_idx, (_, blob_path) in enumerate(parts):
                mode = "wb" if part_idx == 0 else "ab"
                download_github_file(blob_path, tmp_zip, mode=mode)
            with zipfile.ZipFile(tmp_zip, "r") as zip_ref:
                zip_ref.extractall(target_folder)
        except Exception as e:
            print(f"Error downloading {target_rel}: {e}")
        finally:
            if os.path.isfile(tmp_zip):
                os.remove(tmp_zip)

def start_download(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    # Handle large file warning tokens
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

def download_google_drive_file(file_id, target_folder=None, force=False):
    # check if target folder exists
    if target_folder is None:
        target_folder = os.path.join(os.path.expanduser("~"), "biblemate", "data", *FILE_IDS[file_id][0])
    if not os.path.isdir(target_folder):
        Path(target_folder).mkdir(parents=True, exist_ok=True)
    # check if final path exists
    final_path = os.path.join(target_folder, file_id)
    #print(f"Checking if {final_path} exists")
    if os.path.exists(final_path):
        if force:
            os.remove(final_path)
        else:
            print(f"{final_path} already exists.")
            return final_path
    # download
    try:
        print(f"Downloading {file_id}")
        output = os.path.join(target_folder, file_id+".zip")
        if os.path.isfile(output):
            os.remove(output)
        if os.path.isfile(output[:-4]):
            os.remove(output[:-4])
        start_download(FILE_IDS[file_id][-1], output)
        with zipfile.ZipFile(output, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
        if os.path.isfile(output):
            os.remove(output)
        # Wait between 5 to 15 seconds before the next download, to workaround rate limit 
        delay = random.uniform(5, 15)
        print("Waiting for", delay, "seconds...")
        time.sleep(random.uniform(5, 15))
    except Exception as e:
        print(f"Error downloading {file_id} in the first try: {str(e)}")
        #traceback.print_exc()
        delay = 15
        print("Waiting for", delay, "seconds...")
        time.sleep(delay)
        try:
            # 2nd attempt with gdown
            print(f"Trying again to download {file_id}")
            gdown.download(id=FILE_IDS[file_id][-1], output=output)
            with zipfile.ZipFile(output, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            if os.path.isfile(output):
                os.remove(output)
        except Exception as e:
            print(f"Error downloading {file_id}: {str(e)}")
            #traceback.print_exc()
            delay = 15
            print("Waiting for", delay, "seconds...")
            time.sleep(delay)
        return ""
    return final_path

def getValidOptions(options=[], descriptions=[], bold_descriptions=False, filter="", default="", title="Available Options", text="Select an item:"):
    if not options:
        return ""
    filter = filter.strip().lower()
    if descriptions:
        descriptionslower = [i.lower() for i in descriptions]
        values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options) if (filter in option.lower() or filter in descriptionslower[index])]
    else:
        values = [(option, option) for option in options if filter in option.lower()]
    if not values:
        if descriptions:
            values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options)]
        else:
            values = [(option, option) for option in options]
    result = radiolist_dialog(
        title=title,
        text=text,
        values=values,
        default=default if default and default in options else values[0][0],
    ).run()
    if result:
        print(result)
        return result
    return ""

def downloadbibleaudio(default=""):
    options = list(AUDIO_REPOS.keys())
    userInput = getValidOptions(options=options, title="Downlaod Bible Audio", default=default, text="NET (American accent), OHGB (slow), BHS5, OGNT are downloaded by default. \nSelect below for a replacement or new download:")
    if not userInput:
        return False
    print(f"You selected '{userInput}'.")
    module, repo, *_ = AUDIO_REPOS[userInput]
    downloadbibleaudioaction(module, repo, force=True)
    return True

def downloadbibleaudioaction(module, repo, force=False):
    if not shutil.which("git"):
        print("git is not installed. Please install git and try again.")
        return
    try:
        audioDir = os.path.join(os.path.expanduser("~"), "biblemate", "data", "audio", "bibles", module, "default")
        # remove old files
        if os.path.isdir(audioDir):
            # os.rmdir does not work with sub directories
            # os.rmdir(audioDir)
            # use shutil.rmtree instead
            if force:
                shutil.rmtree(audioDir)
            else:
                print(f"{audioDir} already exists.")
                return
        Path(audioDir).mkdir(parents=True, exist_ok=True)
        os.system(f"git clone https://github.com/{repo} {audioDir}")
        print("Downloaded!")
        print(f"unpacking `{module}` audio files ...")
        for item in os.listdir(audioDir):
            zipFile = os.path.join(audioDir, item)
            if os.path.isfile(zipFile) and item.endswith(".zip"):
                #os.system(f"unzip {zipFile}")
                # Unzip file
                shutil.unpack_archive(zipFile, audioDir)
                # Delete zip file
                os.remove(zipFile)
        print(f"`{module}` audio installed!")
    except:
        print("Errors!")

def main():
    # download database files from GitHub
    download_github_data()
    # download podcast files from Google Drive
    for i in FILE_IDS:
        download_google_drive_file(i)
    # setup custom folders
    for i in ("lexicons", "commentaries", "audio", "bibles", "books", "clauses"):
        target_folder = os.path.join(os.path.expanduser("~"), "biblemate", "data_custom", i)
        if not os.path.isdir(target_folder):
            Path(target_folder).mkdir(parents=True, exist_ok=True)
    # downloading default audio with git clone
    for i in (
        "NET (American accent; verse-by-verse)",
        "OHGB (Hebrew & Greek; slow; verse-by-verse)",
        "BHS5 (Hebrew; word-by-word)",
        "OGNT (Greek; word-by-word)",
    ):
        module, repo, *_ = AUDIO_REPOS[i]
        downloadbibleaudioaction(module, repo)
    # download more audio
    download_audio = True
    while download_audio:
        download_audio = downloadbibleaudio()

if __name__ == "__main__":
    main()
