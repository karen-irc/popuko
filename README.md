# popuko

[![Build Status (master)](https://travis-ci.org/karen-irc/popuko.svg?branch=master)](https://travis-ci.org/karen-irc/popuko)

## What is this?

- This is an operation bot to do these things automatically for your project on GitHub.
    - merge a pull request automatically.
    - assign a pull request to a reviewer.
    - patrol a pull request which are newly unmergeable by others.
- Almost reimplementation of [homu][homu].


## Motivation

[homu][homu] is the super great operation bot for development on GitHub
and it supports a lot of valuable features: merge pull request into the latest upstream, try to testing on TravisCI,
and more. But its development is not in active now. And also Mozilla's servo team maintains
[their forked version of homu][servo-homu]. But it is developed for their specific usecase.
Not for other projects.

And, to use without host homu by yourself, you can use [homu.io][homu.io].
But it's shared by other third repositories. It would not suite to use it for your internal repository.

Some features (e.g. assigning reviewers to the pull request) are provided by [highfilve][highfive], not by homu.
Thus you also have to setup it to use their features which are used in code review frequently.

And furthermore, homu's reviewer configuration need to configure the central configuration file.
But we'd like to place the configuration for each repositries as decentralization.
This decentraization is important if you manage many repositories and
each of them has contibutors and reviewers individually.

By these things, this project intent to re-implement homu and highfive with minimum features
which can support a review process, and the primary targets are an internal repository on GitHub for work
or a public repository which want to host some merge bots by themselves.
And also this aims to simpify deploying this bot. We challenge to make it easier than the original's one.

These are why we have developed this project.


## Features

These features are inspired by [homu][homu] and [highfive][highfive].

- __Change the labels, the assignees of the pull request by comments__
    - By a reviewer's comment, this bot changes the labels, the assignees of the pull request.
- __Patrol pull requests which cannot merge into it after the upstream has been updated__
    - This bot patrols automatically by hooking GitHub's push events.
    - Change the label for the unmergeable pull request and comment about it.
- __Try the pull request with the latest `master` branch, and merge into it automatically__
    - We call this feature as "Auto-Merging".
- __Specify a reviewer by a file committed to the repository__
    - This feature is not implemented by homu.
    - You can manage a reviewer by normal pull request process for open governance.

### Command

You can use these command as the comment for pull request.

#### `r? @<reviewer>`

- Assign the reviewer to the pull request with labeling `S-awaiting-review`.
- You can also call `@<reviewer> r?`.
- All user can call this command.

#### `@<botname> r+` or `@<botname> r=<reviewer>`

- Mark this pull request as `S-awaiting-merge` by labeling.
- If you enable Auto-Merging, this bot queues the pull request into the approved queue.
- Require _reviewer_ privilege to call this command.

#### `@<botname> r-`

- Cancel the approved by `@<botname> r+`.
    - If Auto-Merging is enabled, this removes the pull request from the approved queue.
- This set back the label to `S-awaiting-review`
- Require _reviewer_ privilege to call this command.


### Auto-Merging

This bot provides a powerful feature we called as _Auto-Merging_.
Auto-Merging behaves like this:

1. Accept the pull request by the review's approved comment (e.g. `@<bot> r+`)
2. This bot queues its pull request into the approved queue.
3. If there is no active item, try to merge it into the latest upstream and run CI on the special branch used for auto testing.
4. If the result of step 3 is success, this bot merge its pull request into the upstream actually.
   Otherwise, this bot marks it as failed.
5. This bot redo step 3 until the approved queue will be empty.


### Reviewer

- A _reviewer_ is managed by `OWNERS.json` places to the root of your repository.
- You can provide _reviewer_ privilege for all users that can comment to the repository.
    - This is useful for an internal repository.


## Setup Instructions

### Build & Launch the Application

1. Build from the source.
    - Run these steps:
        1. `make bootstrap`.
        2. `make build` or `make build_linux_x64`.
    - Run `make help` to see more details.
    - You also can do `go get`.
2. Create the config directory.
    - By default, this app uses `$XDG_CONFIG_HOME/popuko/` as the config dir.
      (If you don't set `$XDG_CONFIG_HOME` environment variable, this use `~/.config/popuko/`.)
    - You can configure the config directory by `--config-base-dir`
3. Set `config.toml` to the config directory.
    - Let's copy from [`./example.config.toml`](./example.config.toml)
4. Start the exec binary.
    - This app dumps all logs into stdout & stderr.
    - If you'd like to use TLS, then provide `--tls`, `--cert`, and `--key` options.

#### Set up for your repository in GitHub.

1. Set the account (or the team which it belonging to) which this app uses as a collaborator
   for your repository (requires __write__ priviledge).
2. Add `OWNERS.json` file to the root of your repository.
    - Please see [`OwnersFile`](./setting/ownersfile.go) about the detail.
    - The example is [here](./OWNERS.json).
3. Set `http://<your_server_with_port>/github` for the webhook to your repository with these events:
    - `Issue comment`
    - `Push`
    - `Status` (required to use Auto-Merging feature).
4. Create these labels to make the status visible.
    - `S-awaiting-review`
        - for a pull request assigned to some reviewer.
    - `S-awaiting-merge`
        - for a pull request queued to this bot.
    - `S-needs-rebase`
        - for an unmergeable pull request.
    - `S-fails-tests-with-upstream`
        - for a pull request which fails tests after try to merge into upstream (used by Auto-Merging feature).
6. Enable to start the build on creating the branch named `auto` for your CI service (e.g. TravisCI).
    - You can configure this branch's name by `OWNERS.json`.
7. Done!


## FAQ

### Why there is no released version?

- __This project always lives in canary__.
- We only support the latest revision.
- All of `master` branch is equal to our released version.
- The base revision and build date are embedded to the exec binary. You can see them by checking stdout on start it.


### Out of scope of this project

- Full-replace homu.
- This project does not have any plan to re-implement all features of homu.
- No plans to create any alternatives of [homu.io][homu.io].


### The current limitations

- The upstream branch should be named as `master`.
- This cannot detect the unmergeable pull request which aims to be merged into non-`master`.


### Can I reuse this package as a library?

- Yes... But I don't recomment to do it.
- Sorry. We don't think to maintain this package as a library.
    - We don't care the breaking change for library APIs.
- This repository is developed for the application, not to reuse from others.


### Do you have any plan to support GitLab or GitHub Enterprise?

- GitLab: see [#152](https://github.com/karen-irc/popuko/issues/152).
- GitHub Enterprise: [#173](https://github.com/karen-irc/popuko/issues/173).


### Why didn't you fork homu?

It was notion.


## License

[The MIT License](./LICENSE.txt)


## How to Contribute

- [TODO: Write CONTRUBUTING.md](https://github.com/karen-irc/popuko/issues/97)


## TODO

- Intelligent cooperation with TravisCI.
- [See more...](https://github.com/karen-irc/popuko/issues)



[homu]: https://github.com/barosl/homu
[servo-homu]: https://github.com/servo/homu
[highfive]: https://github.com/servo/highfive
[homu.io]: http://homu.io/
