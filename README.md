# Proof of Concept - Islandora 7.x using Composer

One of the major shifts in Drupal has been toward using 
[Composer-based workflows](https://www.drupal.org/docs/develop/using-composer/using-composer-to-manage-drupal-site-dependencies). 
 
At DrupalCon New Orleans, Drupal.org announced the availability of supported Composer/Packagist style versions of the
 Drupal ecosystem at [https://packages.drupal.org/7](https://packages.drupal.org/7/packages.json) 
 and [https://packages.drupal.org/8](https://packages.drupal.org/8/packages.json).
 
### Version numbering

Composer is understandably wedded to comparable semantic versioning (x.y.z), while Drupal (and Islandora) practice has had release tags 
in the 7.x-1.x family.  After rather quite a bit of debate, the Drupal community has decided that tag 7.x-1.3 should map to Composer version
"1.3.0" in the "/7" endpoint.  It seems reasonable that Islandora would follow suit.

The [internal-to-Drupal.org project](https://www.drupal.org/project/project_composer) (you may hear it called "the façade")  that maps D.o packages to those
packages.drupal.org endpoints is not terribly easy to apply to other projects.  It does some very cool things 
for drupal.org packages, including mapping module.info dependencies into Composer dependencies.

Drupal modules get Composer type "drupal-module" and Libraries "drupal-library".  
The common [drupal-project template](https://github.com/drupal-composer/drupal-project)
puts those in reasonable locations (like sites/all/modules/contrib for D7 installs).

For creating a Packagist-compatible repo, The Composer team provides a fairly 
simple static repo [generator called Satis](https://github.com/composer/satis).

### Fake composer.jsons

The Islandora 7.x modules have not included composer.json files in their releases.  It is possible to make a verbose
 satis.json file that mocks up what would have been in composer.jsons, had they been included.
 
### Build a builder

In a fit of yak-shaving, I built a generator-generator.  It's Python 3 (yeah, yeah, PHP project, coulda-woulda).

build.py turns modules.yml into satis.json. The Satis (PHP-CLI) package turns satis.json into a static repository based
on GitHub tags.

### Install and use

First, you need a GitHub user and token, otherwise you hit the GitHub API request throttle. That token can be your 
GitHub password (if you don't do 2FA), but better to use a [personal access token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/)
with read-only privileges.

$ composer install (brings in satis into vendor/)

(Python virtualenv if so inclined)

$ pip3 install -r requirements.txt

$ GH_USER=gh_user GH_TOKEN=token python3 build.py modules.yml > satis.json

$ ./vendor/bin/satis build

- or -

$ ./vendor/bin/satis build satis.json docs  (This builds into `docs/` instead of `output/` making it easy to use GitHub pages to serve.

You can then symlink the output/ directory into your webroot, or upload it somewhere. I have it attached here as `docs/`, so it can be found through https://shorock.github.io/islandora_satis (GitHub Pages) 
