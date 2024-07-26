## Local Cache Operations

This section covers the commands to interact with the local cache, including scraping course data and reading it from the cache.

### Scraping Course Data to Local Cache

To scrape course data and save it to the local cache file, run the following command:

```shell
# Download session data, parse, and store.
# Sessions that have already been downloaded will not be downloaded again.
python -m crawler.scrape

# Download session data, parse, and store.
# If there are already downloaded sessions, they will be moved to the backup folder first.
python -m crawler.scrape --reset

# Parse and store using only the session data from the backup folder.
python -m crawler.scrape --on-backup
```

### Reading Course Data from Local Cache

After scraping, you can read the course data from the local cache using these functions in your Python code:

```python
get_cached_sentence_pairs()
get_cached_word_pairs()
```

## Duolingo API Endpoints

Here are the API endpoints for accessing Duolingo courses information:

### Courses List

To get a list of courses, use the following endpoint:

<https://www.duolingo.cn/api/1/courses/list>

### Current Course

To get information about the current course for a specific user, use this endpoint:

<https://www.duolingo.cn/2017-06-30/users/1495461906?fields=currentCourse>
