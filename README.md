# Lists: a CLI to-do list manager

![A screenshot of Lists running in the Code Institute terminal](doc/screenshot.png)

*Lists* is an interactive command-line program for creating and editing to-do lists. The lists can be synchronized with Dropbox for persistence.

Live version is available [here](https://tearnote-lists.herokuapp.com).

## Important notes

Type `help` to get info about the basic usage.

By default, your lists are not saved anywhere, and will disappear on page refresh. To keep your lists, run the `connect` command to link with Dropbox. This will enable the `save` and `load` commands, as well as autosave on `exit`.

The Dropbox account link, as well as your settings, are not saved. As such, the `connect` command must be run at every startup. For details, see the [bugs](#bugs) section.

The documentation is split across three files:

  - [README.md](README.md) (this file): Overview of the app. Read this to get an idea of the feature set, technologies used and project conventions.
  - [DESIGN.md](doc/DESIGN.md): UX design notes crafted during early stages of development. The design process is described entirely, from the concept and market research, through information structuring to visual design.
  - [TESTING.md](doc/TESTING.md): Testing procedures. The app has been automatically validated and manually tested with procedures noted down in this file. WARNING - file contains ?MB of animated GIFs.

## Highlights

![Screenshot of Lists showing the list view](doc/highlights/lists.png)

The app starts showing all available lists, with their progress summary.

![Screenshot of Lists showing the task view](doc/highlights/tasks.png)

The task view shows all tasks in the list, colored by their state.

![Screenshot of Lists showing the sidebar](doc/highlights/sidebar.png)

The sidebar shows the list of all commands that are available right now.

![Screenshot of Lists showing help text](doc/highlights/help.png)

Help text is available for every command.

![Screenshot of Lists showing the Dropbox connection wizard](doc/highlights/dropbox.png)

The Dropbox connection wizard guides the user through the steps of setting up cloud sync via OAuth.

![Screenshot of Lists showing the settings view](doc/highlights/settings.png)

User-adjustable settings to customize app behavior.

![Screenshot of Lists showing error handling](doc/highlights/errors.png)

Graceful and helpful handling of incorrect inputs.

## Technologies

  - Python
    - Idiomatic Python 3 source organized with classes and modules,
    - Error handling via exceptions,
    - PEP 8 compliant,
    - Minimal dependencies,
    - Communication with web services via API libraries and OAuth.
