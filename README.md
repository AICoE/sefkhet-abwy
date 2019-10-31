# Sefkhet-Abwy

This repository contains script/actions that could be executed by Sefkhet-Abwy, one of the many names Sesheta is known by.

## `label_normalizer`

## `review-manager`

The review manager will do two basic things: handle the 'do-not-merge' labels, and assign reviewers once a pull request is ready to be reviewed.

A Pull Request is ready to be reviewed if it has

1. no label starting with "do-not-merge"
2. the "local/check" status is "success" (so we know zuul is happy)

## `merge_master_into_pullrequest`

A command line utility used to merge the current master of the base of a pull request into the pull request head. A human could also press the 'update branch' button on the GitHub web user interface.

[![Maintainability](https://api.codeclimate.com/v1/badges/330c4396d0cf56dc9102/maintainability)](https://codeclimate.com/github/AICoE/Sefkhet-Abwy/maintainability)
