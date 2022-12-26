# DropBoxFileFinder
Provides a functionality to search documents from DropBox using keywords

**Requirements:**

* Python >= 3.10
  * Make sure necessary python libraries are installed 
  `python3 -m pip install dropbox tika flask`
* ELasticSearch Cluster >= 8.5
* [DropBox api auth token](https://developers.dropbox.com/oauth-guide#:~:text=If%20you'd%20like%20to,of%20your%20app%20settings%20page.) 

**Usage:**

* Invoke command to launch app using command `python file_finder.py`. You should see a scree
```
PS C:\Users\tapas\Desktop\DropBoxFileFinder> python .\dropboxconnector\file_finder.py 
 * Serving Flask app 'file_finder'
 * Debug mode: off
2022-12-26 11:51:04,422 - INFO: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2022-12-26 11:51:04,422 - INFO: Press CTRL+C to quit
```

**API Requests:**
Using postman/curl or any suitable clients make api requests

* Download/sync from dropbox to local directory. Sample example `GET http://127.0.0.1:5000/sync?local_path=D:\LocalRepo&auth_token=your_token`
* Index contents of file in local dir to elasticsearch cluster. `GET http://127.0.0.1:5000/index?local_path=D:\LocalRepo`
* Search for keywords in all files `http://127.0.0.1:5000/search?query="Architecture"`


