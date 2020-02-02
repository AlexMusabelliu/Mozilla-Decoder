import lz4.frame as lz4, json, time
import lz4.block
import win32gui

def decompress(filepath, mozilla=False):
    '''
    Takes the filepath to a .*lz4 file and returns the decompressed version.

    Note:
        the * in .*lz4 here means 'wildcard', so you can give and file with contains lz4 in its file extension (e.g. .jsonlz4, .baklz4, etc.)

    Args: 
        filepath (string): a filepath to a .*lz4 file
        mozilla (boolean) (optional, default True): whether or not to enable mozilla mode, which just skips a mozilla header when reading from the file
    Returns: 
        text: the decompressed .*lz4 file
    '''
    bytestream = open(filepath, "rb")

    if mozilla:
        bytestream.read(8)  # skip past the b"mozLz40\0" header

    valid_bytes = bytestream.read()
    text = lz4.block.decompress(valid_bytes)
    return text

def get_tabs(filepath, verbal=False):
    '''
    Gets and returns all open tabs in the mozilla browser.

    Args: 
        filepath (string): a filepath to a .jsonlz4 file
        verbal (boolean, defaults to False): whether or not to enable the verbal output (prints when curSong changes)
    Returns: 
        alltabs: a list of all tabs currently open
    '''
    alltabs = []
    text = decompress(filepath, True)
    jdata = json.loads(text)
    for w in jdata['windows']:
        for t in w['tabs']:
            i = t['index'] - 1
            tab = (t['entries'][i]['title'], t['entries'][i]['url'])

            if verbal:
                print(tab)

            alltabs.append(tab)
    return alltabs

def _get_name(hwnd, trash):
    global VLC_WINDOW, found2
    s = win32gui.GetWindowText(hwnd)
    if "- VLC" in s:
        VLC_WINDOW = s
        found2 = True

if __name__ == "__main__":
    '''
    Example script below, which outputs to a file (CURSONG.txt) the name of the video playing on the first tab accessing YouTube.
    '''
    curSong = None
    VLC_WINDOW = None

    while True:
        allTabs = get_tabs(r"C:\Users\AlexPC\AppData\Roaming\Mozilla\Firefox\Profiles\b1r8tuon.default\sessionstore-backups\recovery.jsonlz4")
        found = False
        found2 = False
        
        for (name, url) in allTabs:
            if "YouTube" in name:
                found = True
                nexSong = name[:name.index(" - YouTube")]
                
                if nexSong != curSong:
                    with open("CURSONG.txt", 'w') as f:
                        curSong = name[:name.index(" - YouTube")]
                        f.write(curSong)
                        print(f"Wrote to file: \"{curSong}\"")
                    break
        
        if not found:
            win32gui.EnumChildWindows(0, _get_name, None)
            if VLC_WINDOW != curSong and found2:
                # print(VLC_WINDOW, curSong)
                with open("CURSONG.txt", 'w') as g:
                    name = VLC_WINDOW[:VLC_WINDOW.index(" - VLC media player")]
                    g.write(name)
                    print(f"Wrote to file: \"{name}\"")
                    curSong = VLC_WINDOW

        if not found and not found2:
            with open("CURSONG.txt", 'w') as f:
                f.write("Nothing")
                        

        time.sleep(0.5)

