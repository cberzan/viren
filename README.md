## Viren: bulk-rename files using your editor

To install, run `pip install viren`.

To rename files in the current directory, run `viren`. This will open your
editor with a list of files. Edit the file names (but don't add, remove, or
reorder lines). Save the file and quit. Then viren will rename the files as you
requested.

If you need fancier bulk-renaming features, try
[krename](http://www.krename.net/).

Note: Despite the name, viren works with any editor. It calls the `editor`
command internally, which you can configure using `update-alternatives --config
editor`.

To run the tests, clone this repo and run `nosetests`.
