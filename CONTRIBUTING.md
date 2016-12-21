## Development ##
Like all my projects I am making heavy use of [Git Flow](https://github.com/nvie/gitflow) to manage the source code, so you will probably need to install this extenstion if you wish to add any new features or fix any [bugs](https://nxfifteen.me.uk/gitlab/emby/sync/issues).

As always new features should always be developed in a feature branch `git flow feature finish MYFEATURE` and if you need to push this feature to others or have it stored on the `origin` server you can publish it `git flow feature publish MYFEATURE`. The `master` and `develop` branches are both locked to commits so to have your changes merged back you have to create a [merge request](https://nxfifteen.me.uk/gitlab/emby/sync/merge_requests) or [email](mailto:stuart@nxfifteen.me.uk) me a patch file.

There is a very good cheatsheet for Git Flows command available on [GitHub](http://danielkummer.github.io/git-flow-cheatsheet/)
