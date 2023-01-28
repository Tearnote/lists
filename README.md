# Lists: a CLI to-do list manager

![A screenshot of Lists running in the Code Institute terminal](doc/screenshot.png)

*Lists* is an interactive command-line program for creating and editing to-do lists. The lists can be synchronized with Dropbox for persistence.

Live version is available [here](https://tearnote-lists.herokuapp.com).

## Important notes

Type `help` to get info about the basic usage.

By default, your lists are not saved anywhere, and will disappear on page refresh. To keep your lists, run the `connect` command to link with Dropbox. This will enable the `save` and `load` commands, as well as autosave on `exit`.

The Dropbox account link, as well as your settings, are not saved. As such, the `connect` command must be run at every startup. For details, see the [bugs](#bugs) section.
