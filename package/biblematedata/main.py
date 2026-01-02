import os, zipfile, gdown, traceback, time, random, requests, shutil
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog
from pathlib import Path


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
    # vectors - new
    "bible.db": (("vectors",), "1x5WbytQHkiJHzDiAjaf_I6XTIkRyMIBF"),
    "collection.db": (("vectors",), "18tUxwdcaGPaQ7e7m-RIIEEBFNwyBFWva"),
    "dictionary.db": (("vectors",), "1JYjxA6Zf2TkJ4eHEJ9xSaG5XpGcz46yq"),
    "encyclopedia.db": (("vectors",), "1yQmwXIjvZEbrUtoMAm7OQoAYVbnRZVP7"),
    "exlb.db": (("vectors",), "1zY9sKi53ct4fyH5KwOe31uAsSDJ_6t8z"),
    # commentaries - new
    "cAIC.commentary": (("commentaries",), "1tkNrdpw5fmRJ0-3_uvJiRz-f8hMQJIPh"),
    "cAICSC.commentary": (("commentaries",), "1sjPHwZf4gVp5O35yYr7qbjJDC0KzSsvh"),
    "cAICTC.commentary": (("commentaries",), "1pKAzBeuFHXV7Jw6OTKQ9kqDlIUxt-Sf1"),
    # commentaries - UBA
    "cBarnes.commentary": (("commentaries",), "13uxButnFH2NRUV-YuyRZYCeh1GzWqO5J"),
    "cBenson.commentary": (("commentaries",), "1MSRUHGDilogk7_iZHVH5GWkPyf8edgjr"),
    "cBI.commentary": (("commentaries",), "1DUATP_0M7SwBqsjf20YvUDblg3_sOt2F"),
    "cBrooks.commentary": (("commentaries",), "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm"),
    "cCalvin.commentary": (("commentaries",), "1FUZGK9n54aXvqMAi3-2OZDtRSz9iZh-j"),
    "cCBSC.commentary": (("commentaries",), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
    "cCECNT.commentary": (("commentaries",), "1MpBx7z6xyJYISpW_7Dq-Uwv0rP8_Mi-r"),
    "cCGrk.commentary": (("commentaries",), "1Jf51O0R911Il0V_SlacLQDNPaRjumsbD"),
    "cCHP.commentary": (("commentaries",), "1dygf2mz6KN_ryDziNJEu47-OhH8jK_ff"),
    "cClarke.commentary": (("commentaries",), "1ZVpLAnlSmBaT10e5O7pljfziLUpyU4Dq"),
    "cCPBST.commentary": (("commentaries",), "14zueTf0ioI-AKRo_8GK8PDRKael_kB1U"),
    "cEBC.commentary": (("commentaries",), "1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r"),
    "cECER.commentary": (("commentaries",), "1sCJc5xuxqDDlmgSn2SFWTRbXnHSKXeh_"),
    "cEGNT.commentary": (("commentaries",), "1ZvbWnuy2wwllt-s56FUfB2bS2_rZoiPx"),
    "cGCT.commentary": (("commentaries",), "1vK53UO2rggdcfcDjH6mWXAdYti4UbzUt"),
    "cGill.commentary": (("commentaries",), "1O5jnHLsmoobkCypy9zJC-Sw_Ob-3pQ2t"),
    "cHenry.commentary": (("commentaries",), "1m-8cM8uZPN-fLVcC-a9mhL3VXoYJ5Ku9"),
    "cHH.commentary": (("commentaries",), "1RwKN1igd1RbN7phiJDiLPhqLXdgOR0Ms"),
    "cICCNT.commentary": (("commentaries",), "1QxrzeeZYc0-GNwqwdDe91H4j1hGSOG6t"),
    "cJFB.commentary": (("commentaries",), "1NT02QxoLeY3Cj0uA_5142P5s64RkRlpO"),
    "cKD.commentary": (("commentaries",), "1rFFDrdDMjImEwXkHkbh7-vX3g4kKUuGV"),
    "cLange.commentary": (("commentaries",), "1_PrTT71aQN5LJhbwabx-kjrA0vg-nvYY"),
    "cMacL.commentary": (("commentaries",), "1p32F9MmQ2wigtUMdCU-biSrRZWrFLWJR"),
    "cPHC.commentary": (("commentaries",), "1xTkY_YFyasN7Ks9me3uED1HpQnuYI8BW"),
    "cPulpit.commentary": (("commentaries",), "1briSh0oDhUX7QnW1g9oM3c4VWiThkWBG"),
    "cRob.commentary": (("commentaries",), "17VfPe4wsnEzSbxL5Madcyi_ubu3iYVkx"),
    "cSpur.commentary": (("commentaries",), "1OVsqgHVAc_9wJBCcz6PjsNK5v9GfeNwp"),
    "cVincent.commentary": (("commentaries",), "1ZZNnCo5cSfUzjdEaEvZ8TcbYa4OKUsox"),
    "cWesley.commentary": (("commentaries",), "1rerXER1ZDn4e1uuavgFDaPDYus1V-tS5"),
    "cWhedon.commentary": (("commentaries",), "1FPJUJOKodFKG8wsNAvcLLc75QbM5WO-9"),
    # lexicons - new
    "lexicons": ((), "1xlvJ6GURwYCxPnYwo2xuyREutWTeWMcH"),
    # bibles - new
    "ODB.bible": (("original",), "1DD8IsGnH2YAcyHeIp4_CKiezw0vvoMUF"),
    "OIB.bible": (("original",), "1RipYgwIflQprP1h02_7L0chpcINNFxef"),
    "OLB.bible": (("original",), "13wCL_cHTX-ZO6xcbtx6YhiZZuJq_iZht"),
    "OPB.bible": (("original",), "1WzrQlFzOE1PK7Lg2QxcUo-zpFiQlJujO"),
    "ORB.bible": (("original",), "17TnhpbkO7y261NcJ8GThEBpMpF_MeTjG"),
    "OHGB.bible": (("bibles",), "1Wwn_HaVW_ViOdG7MA_3aAxZQajw7O4tK"),
    "OHGBi.bible": (("bibles",), "1z5xSfTQ8FESr01xx-WKppRisLUECiXbV"),
    # bibles - UBA
    "ASV.bible": (("bibles",), "1oDuV54_zOl_L0GQqmYiLvgjk2pQu4iSr"),
    "BSB.bible": (("bibles",), "1fQX8cT12LE9Q3dBUJyezTYg4a0AbdKbN"),
    "CUV.bible": (("bibles",), "1SuXGZIx_ivz9ztPvnylO_ComYOYrJyzk"),
    "CUVs.bible": (("bibles",), "1cu0FFIb_Zc3lQ71P1EJB3P8E5vDLnOt6"),
    "ISV.bible": (("bibles",), "1_nmaakABx8wVsQHdBL9rVh2wtRK8uyyW"),
    "KJV.bible": (("bibles",), "1ycOkEJ2JI_4iwjllb4mE02wkDvrsPlNq"),
    "LEB.bible": (("bibles",), "1p-_phmh3y54i4FSLhzEd33_v0kzSjAZn"),
    "LXX1.bible": (("bibles",), "1t9sgkQxYkZElg1M8f3QHYIF8oRAIN_hd"),
    "LXX1i.bible": (("bibles",), "1vtGfv2otmb2N86M2QdRB6KdFjlNyAGOc"),
    "LXX2.bible": (("bibles",), "1oZk5nYKcR1s2XtRLfU-H9IxCkCQ2px6U"),
    "LXX2i.bible": (("bibles",), "1jgq30khM0Oqxa3phE07Wg4R2p15t1N12"),
    "NET.bible": (("bibles",), "1pJ_9Wk4CmDdFO08wioOxs4krKjNeh4Ur"),
    "SBLGNT.bible": (("bibles",), "1N1ryqvSytW3RFlOUy7rex0JdO2X5IzuK"),
    "SBLGNTl.bible": (("bibles",), "1IgbX1ZBB05FgNglQM8t6GZBNSJVCu2fS"),
    "ULT.bible": (("bibles",), "1C_YiWs7GsduCuBOO4vSR7c13RRFtIZGg"),
    "UST.bible": (("bibles",), "1-s7NUKpPauer3w1hpu6W9YqVBjiLuXmc"),
    "WEB.bible": (("bibles",), "1L9qAeamdZwGzVdf7jC4_ks05hyQa2R7l"),
    # core - new
    "collections3.sqlite": ((), "1zvNWt0ffo979Mkgp4XZLurbedY8GC4qU"),
    # core - UBA
    "images.sqlite": ((), "18rjzm_2sRcTN22oJPNZrxPZ3eIh_cphq"),
    "indexes2.sqlite": ((), "1EwYNGBE8kCwQ2GsJnwXlg-kM8PURiNG6"),
    "cross-reference.sqlite": ((), "1uitkNgqOH0TrKXwbULF4ibLl13WnZ-U2"),
    "morphology.sqlite": ((), "11QfpwEd5fjdDglPiqzygLNN99AVz2mw5"),
    # data - new
    "biblePeople.data": (("data",), "1o7mfGoRAgPXKAjZfpj2dsY2Xp4vX8NdU"),
    "book_analysis_sc.data": (("data",), "19PIQCP99HI1TEaJiaoMnmKbMu_vUP_OP"),
    "book_analysis_tc.data": (("data",), "19XtVixBGFnCj0akutTivq13eT_Gkn6gU"),
    "book_analysis.data": (("data",), "1_Z4qjwgxUC4O-Pz7rX72ZtM3qLOD5ZL-"),
    "chapter_summary_sc.data": (("data",), "10Au81R8qxB1kPGUS6sv2L5imDCgQDoEa"),
    "chapter_summary_tc.data": (("data",), "1jpJLNB2UZ7U0VSFnlqCh_idL-j5jLUYX"),
    "chapter_summary.data": (("data",), "1W5a04a4d4hfQEMgHX1x0hUOY4Q2Cu-hp"),
    # data - UBA
    "exlb3.data": (("data",), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP"),
    "dictionary.data": (("data",), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
    "encyclopedia.data": (("data",), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
    # books - UBA
    "books": ((), "10BmoBH-XOY4QOiYQ0gyzUn4YxsHYnPte"),
    # podcast - new
    "podcast": ((), "1aNS8rtdQcTZGub6jhZhEarpUK3R4f_x8"),
    # audio (via git clone)
}

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
    # download files
    for i in FILE_IDS:
        download_google_drive_file(i)
    # setup custom folders
    for i in ("lexicons", "commentaries", "audio", "bibles"):
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
