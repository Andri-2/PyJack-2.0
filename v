Help on Download in module nicegui.functions.download object:

class DDoowwnnllooaadd(builtins.object)
 |  Download functions
 |
 |  These functions allow you to download files, URLs or raw data.
 |
 |  *Added in version 2.14.0*
 |
 |  Methods defined here:
 |
 |  ____ccaallll____(self, src: str | pathlib.Path | bytes, filename: str | None = None, media_type: str = '') -> None
 |      Download
 |
 |      Function to trigger the download of a file, URL or bytes.
 |
 |      :param src: relative target URL, local path of a file or raw data which should be downloaded
 |      :param filename: name of the file to download (default: name of the file on the server)
 |      :param media_type: media type of the file to download (default: "")
 |
 |  ccoonntteenntt(self, content: bytes | str, filename: str | None = None, media_type: str = '') -> None
 |      Download raw bytes or string content
 |
 |      Function to trigger the download of raw data.
 |
 |      *Added in version 2.14.0*
 |
 |      :param content: raw bytes or string
 |      :param filename: name of the file to download (default: name of the file on the server)
 |      :param media_type: media type of the file to download (default: "")
 |
 |  ffiillee(self, path: str | pathlib.Path, filename: str | None = None, media_type: str = '') -> None
 |      Download file from local path
 |
 |      Function to trigger the download of a file.
 |
 |      *Added in version 2.14.0*
 |
 |      :param path: local path of the file
 |      :param filename: name of the file to download (default: name of the file on the server)
 |      :param media_type: media type of the file to download (default: "")
 |
 |  ffrroomm__uurrll(self, url: str, filename: str | None = None, media_type: str = '') -> None
 |      Download from a relative URL
 |
 |      Function to trigger the download from a relative URL.
 |
 |      Note:
 |      This function is intended to be used with relative URLs only.
 |      For absolute URLs, the browser ignores the download instruction and tries to view the file in a new tab
 |      if possible, such as images, PDFs, etc.
 |      Therefore, the download may only work for some file types such as .zip, .db, etc.
 |      Furthermore, the browser ignores filename and media_type parameters,
 |      respecting the origin server's headers instead.
 |      Either replace the absolute URL with a relative one, or use ``ui.navigate.to(url, new_tab=True)`` instead.
 |
 |      *Added in version 2.14.0*
 |
 |      *Updated in version 2.19.0: Added warning for cross-origin downloads*
 |
 |      :param url: URL
 |      :param filename: name of the file to download (default: name of the file on the server)
 |      :param media_type: media type of the file to download (default: "")
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  ____ddiicctt____
 |      dictionary for instance variables
 |
 |  ____wweeaakkrreeff____
 |      list of weak references to the object
