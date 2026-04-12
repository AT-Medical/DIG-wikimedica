<?php
/**
 * LocalSettings.php — Wikimedica MediaWiki Configuration Example
 *
 * USAGE:
 *   Copy this file to LocalSettings.php and replace all REPLACE_WITH_* placeholders
 *   with actual values from your .env file.
 *
 *   In production, this file is generated from environment variables.
 *   NEVER commit LocalSettings.php with real credentials to version control.
 *
 * SECURITY:
 *   - This file must not be web-accessible.
 *   - Keep $wgSecretKey and $wgDBpassword secret at all times.
 *   - File permissions: chmod 640 LocalSettings.php
 *
 * See: https://www.mediawiki.org/wiki/Manual:LocalSettings.php
 */

# =============================================================================
# Path & URL Configuration
# =============================================================================

## The URL base path to the directory containing the wiki.
$wgScriptPath = "";

## The protocol and server name to use in fully-qualified URLs.
$wgServer = "https://REPLACE_WITH_DOMAIN";  # e.g. https://wikimedica.de

## The URL path to static resources (images, scripts, etc.)
$wgResourceBasePath = $wgScriptPath;

## The URL path for the logo.
$wgLogos = [
    '1x' => "$wgResourceBasePath/resources/assets/wikimedica-logo.png",
    'icon' => "$wgResourceBasePath/resources/assets/wikimedica-icon.png",
];

# =============================================================================
# Site Identity
# =============================================================================

$wgSitename = "Wikimedica";
$wgMetaNamespace = "Wikimedica";

## Default language of the wiki — German.
$wgLanguageCode = "de";

## Site contact email address.
$wgEmergencyContact = "tech@wikimedica.de";
$wgPasswordSender = "noreply@wikimedica.de";

# =============================================================================
# Database Configuration
# =============================================================================

$wgDBtype = "mysql";
$wgDBserver = getenv('MEDIAWIKI_DB_HOST') ?: "mariadb";
$wgDBname = getenv('MEDIAWIKI_DB_NAME') ?: "wikimedica";
$wgDBuser = getenv('MEDIAWIKI_DB_USER') ?: "wikimedica_app";
$wgDBpassword = getenv('MEDIAWIKI_DB_PASSWORD') ?: "REPLACE_WITH_DB_PASSWORD";

## MySQL specific settings.
$wgDBprefix = "";

## MySQL table options to use during installation or updates.
$wgDBTableOptions = "ENGINE=InnoDB, DEFAULT CHARSET=binary";

# =============================================================================
# Security & Secrets
# =============================================================================

## This is a secret key for HMAC-based authentication of login cookies.
## Generate with: openssl rand -hex 32
$wgSecretKey = getenv('MEDIAWIKI_SECRET_KEY') ?: "REPLACE_WITH_64_CHAR_SECRET_KEY";

## An internal secret used to modify MediaWiki's page/revision upgrade key.
$wgUpgradeKey = getenv('MEDIAWIKI_UPGRADE_KEY') ?: "REPLACE_WITH_16_CHAR_UPGRADE_KEY";

# =============================================================================
# Cache Configuration
# =============================================================================

## Shared memory settings.
$wgMainCacheType = CACHE_ACCEL;  # Use APCu/opcache if available
$wgMessageCacheType = CACHE_ACCEL;
$wgParserCacheType = CACHE_DB;   # Or CACHE_MEMCACHED if Memcached is configured

## Specify a different path for cache files.
$wgFileCacheDirectory = "{$wgUploadDirectory}/cache";

# =============================================================================
# Images and File Uploads
# =============================================================================

## To enable image uploads, make sure the 'images' directory is web-accessible.
$wgEnableUploads = true;
$wgUploadDirectory = "/var/www/html/images";
$wgUploadPath = "$wgScriptPath/images";

## Allowed file extensions for uploads.
$wgFileExtensions = array_merge(
    $wgFileExtensions,
    ['svg', 'webp', 'pdf']
);

## Max upload file size (in bytes) — 10 MB default.
$wgMaxUploadSize = 10 * 1024 * 1024;

# =============================================================================
# User Account Policies
# =============================================================================

## Who can create accounts.
## For a moderated contributor model, restrict registration.
$wgGroupPermissions['*']['createaccount'] = false;

## Who can edit pages without logging in.
$wgGroupPermissions['*']['edit'] = false;

## Allow users to read all pages.
$wgGroupPermissions['*']['read'] = true;

## Email confirmation required for editing.
$wgEmailConfirmToEdit = true;

## Require email address for account creation.
$wgEmailAuthentication = true;

# =============================================================================
# Content Namespace Configuration
# =============================================================================

## Enable subpages in the main namespace.
$wgNamespacesWithSubpages[NS_MAIN] = true;

# =============================================================================
# Skin
# =============================================================================

## Default skin: Vector 2022 (modern responsive layout)
$wgDefaultSkin = "vector-2022";

## Installed skins.
wfLoadSkin( 'Vector' );
wfLoadSkin( 'MinervaNeue' );  # Optional: mobile skin

# =============================================================================
# Extensions
# =============================================================================

## Core editing tools
wfLoadExtension( 'WikiEditor' );          # Enhanced edit toolbar
wfLoadExtension( 'VisualEditor' );        # WYSIWYG editor

## Content structure and display
wfLoadExtension( 'CategoryTree' );        # Interactive category trees
wfLoadExtension( 'ParserFunctions' );     # Template logic functions
wfLoadExtension( 'Cite' );               # Footnote/reference system
wfLoadExtension( 'TemplateStyles' );      # Per-template CSS

## Code display
wfLoadExtension( 'SyntaxHighlight_GeSHi' );  # Syntax highlighting

## Navigation and search
wfLoadExtension( 'TitleBlacklist' );      # Prevent unwanted page titles

## User notifications
wfLoadExtension( 'Echo' );               # Notification system

## Anti-spam (important for a public wiki)
wfLoadExtension( 'ConfirmEdit' );
wfLoadExtension( 'ConfirmEdit/ReCaptchaNoCaptcha' );

# ReCaptcha keys (obtain from https://www.google.com/recaptcha/)
$wgReCaptchaSiteKey = getenv('RECAPTCHA_SITE_KEY') ?: "REPLACE_WITH_RECAPTCHA_SITE_KEY";
$wgReCaptchaSecretKey = getenv('RECAPTCHA_SECRET_KEY') ?: "REPLACE_WITH_RECAPTCHA_SECRET_KEY";

# =============================================================================
# VisualEditor Configuration
# =============================================================================

$wgVirtualRestConfig['modules']['parsoid'] = [
    'url' => 'http://localhost:8142',  # Parsoid service URL
    'domain' => 'wikimedica.de',
    'prefix' => 'wikimedica',
];

# =============================================================================
# Search Configuration
# =============================================================================

## Use built-in MySQL full-text search by default.
## Consider ElasticSearch (CirrusSearch) for production scale.
$wgDisableInternalSearch = false;

# =============================================================================
# Performance
# =============================================================================

## Compress stored revision text.
$wgCompressRevisions = true;

## Use gzip for stored revisions.
$wgRevisionStoreType = 'FileStore';

## Enable CDN/Squid support (Cloudflare acts as CDN).
$wgUseSquid = true;
$wgSquidServers = [];  # Cloudflare handles this transparently

# =============================================================================
# Logging
# =============================================================================

## Log errors to file rather than displaying them to users.
$wgShowExceptionDetails = false;  # IMPORTANT: false in production
$wgShowDBErrorBacktrace = false;  # IMPORTANT: false in production

error_reporting( E_ERROR );
ini_set( 'display_errors', '0' );

# =============================================================================
# Additional Notes
# =============================================================================

# For initial installation, run the MediaWiki installer:
#   php /var/www/html/maintenance/install.php \
#     --dbname wikimedica \
#     --dbserver mariadb \
#     --dbuser wikimedica_app \
#     --dbpass "${MEDIAWIKI_DB_PASSWORD}" \
#     --lang de \
#     --pass "${MEDIAWIKI_ADMIN_PASS}" \
#     "Wikimedica" "admin"
#
# After installation, copy this LocalSettings.php into place.
