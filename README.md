# DropBoxFileFinder
Provides a functionality to search documents from DropBox using keywords

**Requirements:**

> * Python >= 3.10 
> * ELasticSearch Cluster >= 8.5
> * JDK >= 7.0 for tika. 
> * [DropBox api auth token](https://developers.dropbox.com/oauth-guide#:~:text=If%20you'd%20like%20to,of%20your%20app%20settings%20page.) 

**Usage:**
* Create a virtual environment and activate it:  
    * `python3 -m ~/testenv`
    * `source ~/testenv/bin/activate`
* Make sure necessary python libraries are installed 
    * `pip3 install -r requirements.txt`
* Invoke command to launch app using command `python file_finder.py`. 
```
```

**API Requests:**
Using postman/curl or any suitable clients make api requests

* Download/sync from dropbox to local directory. Sample example `GET http://127.0.0.1:5000/sync?local_path=D:\LocalRepo&auth_token=your_token`
* Index contents of file in local dir to elasticsearch cluster. `GET http://127.0.0.1:5000/index?local_path=D:\LocalRepo`
* Search for keywords in all files `http://127.0.0.1:5000/search?query="Architecture"`


