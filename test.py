import downloader

t = downloader.Downloader(["beer",2,"bottle"])
t.start()
t.join()
