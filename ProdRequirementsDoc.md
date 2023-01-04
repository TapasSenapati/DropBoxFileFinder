# DropBox File Finder

## Overview

> Building a prototype application that can search documents from a cloud storage service like Dropbox or Google Drive on the content inside the document. 

## Goals

> * To be able to use the application to connect to dropbox storage service.
> * To be able to sync files incrementally and not have to download all files.
> * To be able to search by contents of files and figure out the files having the content.
> * To receive appropriate/friendly error messages to be able to troubleshoot failures.

## Non-Goals 

> * Not meant for production use and no sla requirements
> * 100% reliability
> * Metrics and Monitoring
> * Performance Profiling

## Future improvements
> * Package application so that it can be uploaded to pypi or anaconda for easy download and installation
> * Add metrics and alerting
> * Add a oauth2.0 flow instead of fetching token through environment variables.
> * Add a persistence layer to store intermediate results/processing metadata during file sync and indexing
> * Persistence for logs and auto rotation
> * Improve message consumption logic using multiple queues and threads.Add a dlq.
> * Monitor and restart automatically when any of the system components crash. supervisord can be used.
> * Add flask templates for better front end rendering, routing and usage

## Assumptions 

> End user is technical to go through the [README.MD](https://github.com/TapasSenapati/DropBoxFileFinder/blob/main/README.md) and follow instructions


## User Stories
### User Story 1

    As a user, I want to be able to index files(docs,images,etc.) from dropbox in elasticsearch, so I can do fast content searching for the files inside dropbox

### Acceptance Testing

    Search by key terms using elasticsearch api, and retrieve list of files that contains those keys. Verify accuracy.

### User Story 2

    As a user, I want indexes updated automatically so my search results are as accurate as possible.

### Acceptance Testing

    Add/Remove files in dropbox and search using api. Changes should be reflected.

