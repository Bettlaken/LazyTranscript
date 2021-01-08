<p align="center">
  <a href="" rel="noopener">
 <img width=100px height=100px src="assets/icons/neutral/quote.png" alt="Project logo"></a>
</p>

<h1 align="center">Contributing</h1>

### Introduction

Thank you for liking LazyTranscript so much that you are considering contributing to it. It's only through people like you that LazyTranscript can continue to evolve and make transcriptions as easy as possible!

Through these guidelines, all helpers of this project should benefit from each other's contribution. The guidelines try to solve common questions and problems in advance and try to reduce the workload for everyone.

LazyTranscript is happy about every contribution! You can for example:
* improve or extend the documentation
* write your own plug-in (little explanation follows later in this document)
* make code improvements
* add features
* help others

Feel free to suggest or implement ideas!

### Ground Rules

In order to facilitate the collaborative work on LazyTranscript, the following basic rules should be followed. 

__Follow the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md)!__

* New functionality should preferably be implemented as a plug-in.
* Fill issues not only with error messages, but also with examples.
* The more detailed and extensive the issues are, the easier they are to track.
* Create a new branch for each new feature.
* Features should be as isolated as possible.
* If you are unsure about an idea, feel free to create an issue to discuss your idea and find contributors.
* External programs, which have to be installed without pip, should be avoided urgently. This is to prevent that the installation barrier of LazyTranscript becomes too large.
* Issues should not be used for basic python questions.

### Your First Contribution

If you want to help with LazyTranscript, but are not sure what to do, it is worth taking a look at the issues. If possible, these are tagged so you can quickly determine that they match your expertise.

**Working on your first Pull Request?** You can learn how from this *free* series [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github) 

Once the first issues are established, it is planned to create and support "first-timers-only" issues according to http://www.firsttimersonly.com/

Now you can start creating your first changes. Feel free to ask for help!

### Getting started

1. Create your own fork of the code
2. Do the changes in your fork
3. Create a Pull Request

If you find a small fix and don't want to correct it yourself, create a beginner friendly issue so people new to open source can fix them.

### Code, commit message and labeling conventions
* Class names should use the CapWords convention
* Function and variable names should be lowercase separated by underscores 
* You can find a code documenation in the "docs" folder.

### Code review process

The maintainer(s) try to process and comment pull requests as fast as possible. However, do not forget that LazyTranscript is a hobby project and therefore delays are possible.

### Quick guide for creating your own plug-in

1. Create a folder under the "plugins" directory for your plug-in
0. In this folder create a python-file called "<YOUR_PLUGIN_NAME>_lt_plugin.py"
0. Create a class called "plugin" which inherited the "IPlugin"-Class
0. Override the necessary methods from IPlugin and use the plugin_manager to manipulate or receive the text or specific words
    * If you want to make a toolbar-plug-in then you need override the "get_toolbar_action"-Method and create the QActions there
    * If you want to make a word by word editing plug-in then you need to override the "get_word_action"-Method and return the QPushButtons via the "add_new_word_by_word_action"-Method of the plug-in manager.
0. Override the get_name Method and return your plug-in name

Optional:
* Override the project_loaded-Method to do something when the project is loaded
* For long task you should use a QThread and use the signals in the IPlugin-Class to notify the main thread
* If you are using some open source libraries you should include them in the "licence"-directory in your plug-in directory.

If you have further questions: Have a look at the other plug-ins, read the documentation or feel free to create a issue with your question.

### How to report a bug

__If you find a security vulnerability please send it to: maurice(at)samuel-bolle.de__

If not: Create an Issue and try to describe the bug as detailed as possible.
As the project evolves and certain patterns are found in the bug reports, an ISSUE_TEMPLATE will be generated.

### How to suggest a feature or enhancement

Create an issue and try to describe the feature and its gains as detailed as possible. If you already have an idea for a possible implementation, describe it as well. This way, others can evaluate this idea and refine the implementation.

