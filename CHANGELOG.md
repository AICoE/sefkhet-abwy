# Changelog for Sesheta's actions Project

## [0.3.0] - 2019-Oct-02 - goern

### Added

Added a first skeleton of a review manager.

## [0.2.0] - 2019-Oct-01 - goern

### Changed

Using octomachinery to communicate with GitHub, this turned the application into an async one.

## [0.1.0] - 2019-Sept-30 - goern

### Added

An `merge-master-into-pullrequest` script.

## Release 0.14.1 (2020-10-28T09:05:41)
### Features
* routine update for sefkhet-abwy
* :arrow_up: bounced the version
* :arrow_up: bounced the version
* :sparkles: added status intent handling stub
* :sparkles: added the hacktoberfest-accepted label
* :sparkles: added exception handling for main async loop
* :sparkles: added two advisor release milestones
* :sparkles: added  labels
* :telescope: Removed hardcoded values
* Delete stale.yml
* :arrow_up: using a different ServiceAccount Key now...
* :neckbeard: issue_url is needed for labels creation
* using get with dict for getting the object (#49)
* :recycle: allow sefkhet-abwy to approve sesheta's pr
* :alien: include aicoe-ci configuration file
* :cop: update gchat ids for the users
* Add Tomas Coufal as tumido
* :sparkles: this (should) filter out approvals by sesheta
* do not notify channel on auto approval by Sesheta
* removed adding the 'approved' label, as it is sufficient to add an approving review
* added a realname mapping for sefkhet-abwy[bot]
* :sparkles: dont forget to label it 'approve'
* added a new milestone, auto-approve 'Automatic dependency re-locking'
* added check if PR was opened by sesheta
* :sparkles: two new standard labels, inspired by openshift/kubernetes community
* :sparkles: now with auto-approve of 'automatic updates'
* added descriptions to all DEFAULT_LABELS
* Lets pass the parsed text
* We can log the incoming json
* stipping username from public messages
* Added function to create releases
* commit by error
* :sparkles: debugging left over
* Tag's start with v
* Tag's start with v
* Lets pass the parsed text
* We can log the incoming json
* stipping username from public messages
* Added function to create releases
* fiddled a little on the label normalization
* Fix coala issue
* Added extra message to be ignored
* added metrics to be reported
* added aihttp client session
* :arrow_up: Bump pyyaml from 3.13 to 5.1
* updated the raw github client to get a aiohttp session as a parameter
* relocked dependencies
* releases are repository specific, not PR specific
* do not notify on automatic dependency management PR
* supress the hangout notification on 'Automatic dependency re-locking'
* added logging_env_var_start to init_logging()
* :sparkles: ...
* :sparkles: initial non-functional chat bot
* :green_heart: handle KeyError in hangouts_userid()
* :sparkles: ...
* :sparkles: started migrating methods needed for release handling
* :lock: bounced versions
* :sparkles: notify channel on opened/reopened issue
* 🚕 using the PR number as part of the cache key
* :sparkles: added send_notification() so that he just send one notification within 10secs
* feature to add size labels to pull requests
* feature to add approved labels after approved review
* added ...
* :sparkled: added create_or_update_milestone() and create a v0.6.0 mailestone
* :green_heart: added pytest job and trigger a build
* Update review_manager.py
* :sparkles: requested reviewers are not @mentioned in chat
* Create stale.yml
* .
* reduced the log level from error to warning, so that sentry doesnt pick these up
* finished working on rebase label, infra for reviewer assigning is done
* :green_heart: removed pytest job as we require p37 which is not supported by thoth zuul
* :sparkles: finished handling of needs-rebase label :rocket:
* :green_heart: added has_label() method, to figure out if a given PR has a given label
* :sparkles: added needs-rebase label handling
* :sparkles: working on codeowners based reviewer list
* Update .zuul.yaml
* :sparkles: continued working on the rewiewers list generation method
* :sparkles: started working on the rewieers list generation method
* :sparkles: implemented to reviewer assign logic, part 2
* added rope
* :sparkles: implemented to reviewer assign logic
* :sparkles: moar readme
* :sparkles: WIP label handling works now, thx @webknjaz
* :sparkles: :boom:
* started working on merging master to PR
* using new instance of github api, rather than RUNTIME_CONTEXT
* :sparkles: added a script to normalize the common labels in all our repos
* :sparkles: added WIP handling on PRs
* :sparkles: added a very first skeleton of a review manager, this is more like 'lets get used to octomachinery'
* :truck: worked on logging and command line options
* :sparkles: using octomachinery to communicate with GitHub, this turned us into a async application!
### Bug Fixes
* :bug: fixed the uninitialized text on DM
* fix the issue url
* :sparkles: bug and kind/bug are treaded identifally
* fixed the GITHUB_REALNAME_MAP, added sai
* :sparkles: added/renamed the mile_stonecreator, it will create all the milestones over all the repositories...
* :bug: fixed coala issues
* :bug: fixed coala issues
* :bug: fixed coala issues
* :bug: fixed coala issues
* fixed thoth's config file
* fixed Bissenbay's hangout userid
* fixed E501
* relocked due to octomachinery 0.1.2 release
* :green_heart: fixed D103: Missing docstring in public function
* :green_heart: fixed D202: No blank lines allowed after function docstring
* :green_heart: fixed the repository name
* fixed the mapping, added realname() from github username
* fixed logging, and the slug
* fixed D202: No blank lines allowed after function docstring (found 1)
* :green_heart: some coala fixed
* :green_heart: some coala fixed
* :sparkles: bug issue get more labels
### Improvements
* :arrow_up: added a few more milestones
* :arrow_up: :brain: cleaned up some __version__ chaos
* :sparkles: added a few more standard labels
* :cop: make pre-commit happy
* :sparkles: updated to use Python3.8
* :sparkles: let's do an propper approve review, rather than just adding the label
* removed the handling of WIP label/title
* :sparkles: minor tweaks
* use the whole branch name for tag
* Respect Null response of github api attrib
* some minor parsing of incoming messages
* use the whole branch name for tag
* :sparkles: this version of 'label_normaliyer' uses GitHub's V4 API to get repos and their labels
* Respect Null response of github api attrib
* some minor parsing of incoming messages
* Added github and gchat ids for Karan Chauhan
* removed a little bit toooo much init_logging
* added standard github templates and pre-commit-hook-config
* removed black and pre-commit from [dev]
* some dependency updates, some reformatting
* :sparkles: put a little structure in
* added another positive emoji 😸
* :sparkles: some minor changes, esp on_issue_opened() and hangouts_room_for()
* Effectively use merge_at
* :sparkles: now w/ v0.6.0 and v0.6.0-dev labels for all thoth-station repositories AND due_on
* :sparkles: now w/ v0.6.0 and v0.6.0-dev labels for all thoth-station repositories
* :sparkles: be a little bit more explicite about the kind of the comment we received
* :green_heart: damned typos
* better wording 🗣
* notify AIOps and Thoth chat rooms
* :green_hearts: keep Coala happy, and Zuul
* :green_hearts: I make DevOps chatty
* :green_heart: refactored needs_rebase() and added some more tests
* added a few descriptions to some labels
* removed the stuff we dont need
### Non-functional
* :sparkles: handling the pull request reviewer request notifications
* :sparkles: new action: merge master into pull request
### Automatic Updates
* :pushpin: Automatic update of dependency octomachinery from 0.3.2 to 0.3.3
* :pushpin: Automatic update of dependency aiohttp from 3.7.1 to 3.7.2
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.1.1
* :pushpin: Automatic update of dependency aiographql-client from 1.0.1 to 1.0.2
* :pushpin: Automatic update of dependency google-api-python-client from 1.10.1 to 1.12.5
* :pushpin: Automatic update of dependency octomachinery from 0.2.2 to 0.3.2
* :pushpin: Automatic update of dependency aiohttp from 3.6.2 to 3.7.1
* :pushpin: Automatic update of dependency thoth-common from 0.16.1 to 0.20.2
* :pushpin: Automatic update of dependency pylint from 2.5.3 to 2.6.0
* :pushpin: Automatic update of dependency google-api-python-client from 1.10.0 to 1.10.1
* :pushpin: Automatic update of dependency thoth-common from 0.16.0 to 0.16.1
* :pushpin: Automatic update of dependency octomachinery from 0.2.1 to 0.2.2
* :pushpin: Automatic update of dependency pytest from 6.0.0rc1 to 6.0.1
* :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0
* :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.0rc1
* :pushpin: Automatic update of dependency google-api-python-client from 1.9.3 to 1.10.0
* :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2

## Release 0.16.0 (2020-11-19T12:06:49)
### Features
* manual port @harshad16 comment
* Create OWNERS
* :bug: normalize to lower case string before getting the intent
* :arrow_up: bounced version
* :arrow_up: update pre-commit plugins
* :sparkles: add python38-migration milestone
* Release of version 0.14.1 (#85)
* routine update for sefkhet-abwy
* :arrow_up: bounced the version
* :arrow_up: bounced the version
* :sparkles: added status intent handling stub
* :sparkles: added the hacktoberfest-accepted label
* :sparkles: added exception handling for main async loop
* :sparkles: added two advisor release milestones
* :sparkles: added  labels
* :telescope: Removed hardcoded values
* Delete stale.yml
* :arrow_up: using a different ServiceAccount Key now...
* :neckbeard: issue_url is needed for labels creation
* using get with dict for getting the object (#49)
* :recycle: allow sefkhet-abwy to approve sesheta's pr
* :alien: include aicoe-ci configuration file
* :cop: update gchat ids for the users
* Add Tomas Coufal as tumido
* :sparkles: this (should) filter out approvals by sesheta
* do not notify channel on auto approval by Sesheta
* removed adding the 'approved' label, as it is sufficient to add an approving review
* added a realname mapping for sefkhet-abwy[bot]
* :sparkles: dont forget to label it 'approve'
* added a new milestone, auto-approve 'Automatic dependency re-locking'
* added check if PR was opened by sesheta
* :sparkles: two new standard labels, inspired by openshift/kubernetes community
* :sparkles: now with auto-approve of 'automatic updates'
* added descriptions to all DEFAULT_LABELS
* Lets pass the parsed text
* We can log the incoming json
* stipping username from public messages
* Added function to create releases
* commit by error
* :sparkles: debugging left over
* Tag's start with v
* Tag's start with v
* Lets pass the parsed text
* We can log the incoming json
* stipping username from public messages
* Added function to create releases
* fiddled a little on the label normalization
* Fix coala issue
* Added extra message to be ignored
* added metrics to be reported
* added aihttp client session
* :arrow_up: Bump pyyaml from 3.13 to 5.1
* updated the raw github client to get a aiohttp session as a parameter
* relocked dependencies
* releases are repository specific, not PR specific
* do not notify on automatic dependency management PR
* supress the hangout notification on 'Automatic dependency re-locking'
* added logging_env_var_start to init_logging()
* :sparkles: ...
* :sparkles: initial non-functional chat bot
* :green_heart: handle KeyError in hangouts_userid()
* :sparkles: ...
* :sparkles: started migrating methods needed for release handling
* :lock: bounced versions
* :sparkles: notify channel on opened/reopened issue
* 🚕 using the PR number as part of the cache key
* :sparkles: added send_notification() so that he just send one notification within 10secs
* feature to add size labels to pull requests
* feature to add approved labels after approved review
* added ...
* :sparkled: added create_or_update_milestone() and create a v0.6.0 mailestone
* :green_heart: added pytest job and trigger a build
* Update review_manager.py
* :sparkles: requested reviewers are not @mentioned in chat
* Create stale.yml
* .
* reduced the log level from error to warning, so that sentry doesnt pick these up
* finished working on rebase label, infra for reviewer assigning is done
* :green_heart: removed pytest job as we require p37 which is not supported by thoth zuul
* :sparkles: finished handling of needs-rebase label :rocket:
* :green_heart: added has_label() method, to figure out if a given PR has a given label
* :sparkles: added needs-rebase label handling
* :sparkles: working on codeowners based reviewer list
* Update .zuul.yaml
* :sparkles: continued working on the rewiewers list generation method
* :sparkles: started working on the rewieers list generation method
* :sparkles: implemented to reviewer assign logic, part 2
* added rope
* :sparkles: implemented to reviewer assign logic
* :sparkles: moar readme
* :sparkles: WIP label handling works now, thx @webknjaz
* :sparkles: :boom:
* started working on merging master to PR
* using new instance of github api, rather than RUNTIME_CONTEXT
* :sparkles: added a script to normalize the common labels in all our repos
* :sparkles: added WIP handling on PRs
* :sparkles: added a very first skeleton of a review manager, this is more like 'lets get used to octomachinery'
* :truck: worked on logging and command line options
* :sparkles: using octomachinery to communicate with GitHub, this turned us into a async application!
### Bug Fixes
* :bug: fixed the uninitialized text on DM
* fix the issue url
* :sparkles: bug and kind/bug are treaded identifally
* fixed the GITHUB_REALNAME_MAP, added sai
* :sparkles: added/renamed the mile_stonecreator, it will create all the milestones over all the repositories...
* :bug: fixed coala issues
* :bug: fixed coala issues
* :bug: fixed coala issues
* :bug: fixed coala issues
* fixed thoth's config file
* fixed Bissenbay's hangout userid
* fixed E501
* relocked due to octomachinery 0.1.2 release
* :green_heart: fixed D103: Missing docstring in public function
* :green_heart: fixed D202: No blank lines allowed after function docstring
* :green_heart: fixed the repository name
* fixed the mapping, added realname() from github username
* fixed logging, and the slug
* fixed D202: No blank lines allowed after function docstring (found 1)
* :green_heart: some coala fixed
* :green_heart: some coala fixed
* :sparkles: bug issue get more labels
### Improvements
* Introduce grti and gti commands
* :arrow_up: added a few more milestones
* :arrow_up: :brain: cleaned up some __version__ chaos
* :sparkles: added a few more standard labels
* :cop: make pre-commit happy
* :sparkles: updated to use Python3.8
* :sparkles: let's do an propper approve review, rather than just adding the label
* removed the handling of WIP label/title
* :sparkles: minor tweaks
* use the whole branch name for tag
* Respect Null response of github api attrib
* some minor parsing of incoming messages
* use the whole branch name for tag
* :sparkles: this version of 'label_normaliyer' uses GitHub's V4 API to get repos and their labels
* Respect Null response of github api attrib
* some minor parsing of incoming messages
* Added github and gchat ids for Karan Chauhan
* removed a little bit toooo much init_logging
* added standard github templates and pre-commit-hook-config
* removed black and pre-commit from [dev]
* some dependency updates, some reformatting
* :sparkles: put a little structure in
* added another positive emoji 😸
* :sparkles: some minor changes, esp on_issue_opened() and hangouts_room_for()
* Effectively use merge_at
* :sparkles: now w/ v0.6.0 and v0.6.0-dev labels for all thoth-station repositories AND due_on
* :sparkles: now w/ v0.6.0 and v0.6.0-dev labels for all thoth-station repositories
* :sparkles: be a little bit more explicite about the kind of the comment we received
* :green_heart: damned typos
* better wording 🗣
* notify AIOps and Thoth chat rooms
* :green_hearts: keep Coala happy, and Zuul
* :green_hearts: I make DevOps chatty
* :green_heart: refactored needs_rebase() and added some more tests
* added a few descriptions to some labels
* removed the stuff we dont need
### Non-functional
* :sparkles: handling the pull request reviewer request notifications
* :sparkles: new action: merge master into pull request
### Automatic Updates
* :pushpin: Automatic update of dependency octomachinery from 0.3.3 to 0.3.4 (#84)
* :pushpin: Automatic update of dependency octomachinery from 0.3.2 to 0.3.3
* :pushpin: Automatic update of dependency aiohttp from 3.7.1 to 3.7.2
* :pushpin: Automatic update of dependency pytest from 6.0.1 to 6.1.1
* :pushpin: Automatic update of dependency aiographql-client from 1.0.1 to 1.0.2
* :pushpin: Automatic update of dependency google-api-python-client from 1.10.1 to 1.12.5
* :pushpin: Automatic update of dependency octomachinery from 0.2.2 to 0.3.2
* :pushpin: Automatic update of dependency aiohttp from 3.6.2 to 3.7.1
* :pushpin: Automatic update of dependency thoth-common from 0.16.1 to 0.20.2
* :pushpin: Automatic update of dependency pylint from 2.5.3 to 2.6.0
* :pushpin: Automatic update of dependency google-api-python-client from 1.10.0 to 1.10.1
* :pushpin: Automatic update of dependency thoth-common from 0.16.0 to 0.16.1
* :pushpin: Automatic update of dependency octomachinery from 0.2.1 to 0.2.2
* :pushpin: Automatic update of dependency pytest from 6.0.0rc1 to 6.0.1
* :pushpin: Automatic update of dependency thoth-common from 0.14.2 to 0.16.0
* :pushpin: Automatic update of dependency pytest from 5.4.3 to 6.0.0rc1
* :pushpin: Automatic update of dependency google-api-python-client from 1.9.3 to 1.10.0
* :pushpin: Automatic update of dependency thoth-common from 0.14.1 to 0.14.2
