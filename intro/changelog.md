---
title: Changelog
excerpt: This page lists changes made to the Web API and its documentation.
category: 6673eedb565107002a159063
isReference: true
slug: changelog
---

<style>
.markdown-body {
	--markdown-title-marginTop: 2em;
}
</style>

Listed below are all the changes to the SeaTable API. Each date corresponds to a new version of SeaTable Server Enterprise Edition. If you’re looking for changes beyond the API, see the SeaTable [Changelog](https://seatable.io/docs/changelog) or check out the [SeaTable Blog](https://seatable.io/blog) for detailed release notes.

## Version 4.4 (15.05.2024)

> 📘 New requests
>
> **Base Operations (from 4.4)**
>
> Starting with version 4.4, SeaTable introduced a new component to SeaTable Server: the API Gateway. It introduces several new API endpoints and improvements to existing ones, creating a more streamlined experience for all base operations. You can identify the new endpoints by their URLs, which include `/api-gateway/`. The old API endpoints for `dtable-server` and `dtable-db` are still valid and could be used.

> 🚧 Breaking changes
>
> - data collection table calls (user) were removed. This was done because data collection tables will be disabled in general with version 5.0. In SeaTable Cloud this feature was never available.
> - [List Rows](/reference/listrowsdeprecated): `Link Formula` returns now an array instead of a string. This is to harmonize the output with `Get Row` and `List Rows with SQL`.
> - [Get Row](/reference/getrowdeprecated): `_mtime` and `_ctime` are not returned if these column types are defined in this base. This is to harmonize the output with `List Rows` and `List Rows with SQL`.

> 👍 Other changes
>
> - [List Rows](/reference/listrowsdeprecated): The options `order_by` and `direction` were removed to avoid conflict situations with a selected view.
> - API-Gateway calls now return the current api usage and limits via X-header.

## Version 4.3 (08.02.2024)

You can access the SeaTable API Reference for version 4.3 via this link: [SeaTable API Reference - Version 4.3](https://seatable.readme.io/v4.3/reference/introduction).

> 📘 New requests
>
> **Base Operations**
>
> [Create Row Links in Big Data](/reference/post_dtable-db-api-v1-base-base-uuid-links) <span class="APIMethod APIMethod_fixedWidth APIMethod_post">post</span> `/dtable-db/api/v1/base/{base_uuid}/links/
[Delete Row Links in Big Data](/reference/post_dtable-db-api-v1-base-base-uuid-links) <span class="APIMethod APIMethod_fixedWidth APIMethod_delete">delete</span> `/dtable-db/api/v1/base/{base_uuid}/links/`
>
> **Account Operations - System Admin**
>
> - [Update Team User](/reference/put_api-v2-1-admin-organizations-org-id-users-user-id) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/admin/organizations/{org_id}/users/{user_id}/`
>
> **Account Operations - Team Admin**
>
> - [List Team Logins](/reference/get_api-v2-1-org-org-id-admin-login-logs) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/login-logs/`
> - [List User Logins](/reference/get_api-v2-1-org-org-id-admin-login-logs-user-id) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/login-logs/{user_id}`
> - [Get SAML Config](/reference/get_api-v2-1-org-org-id-admin-saml-config) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api/v2.1/org/{org_id}/admin/saml-config/`
> - [Update SAML Config](/reference/put_api-v2-1-org-org-id-admin-saml-config) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/org/{org_id}/admin/saml-config/`
> - [Verify SAML Domain](/reference/put_api-v2-1-org-org-id-admin-verify-domain) <span class="APIMethod APIMethod_fixedWidth APIMethod_put">put</span> `/api/v2.1/org/{org_id}/admin/verify-domain/`
>
> **Account Operations - User**
>
> - [Search User](/reference/get_api2-search-user) <span class="APIMethod APIMethod_fixedWidth APIMethod_get">get</span> `/api2/search-user/?q={search_query}`

> 👍 Other changes
>
> - New option to export the base with or without assets in `GET /api/v2.1/admin/dtables/{base_uuid}/synchronous-export/export-dtable/`.

## Version 4.2 (22.11.2023)

The SeaTable API Reference for version 4.2 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.2).

> 📘 New requests
>
> - New Category: Python Scheduler
> - Export base: `GET /api/v2.1/admin/dtables/{base_uuid}/synchronous-export/export-dtable/`
> - Search base/apps of a user: `GET /api/v2.1/dtable/items-search/`
> - Activate/Deactivate app: `PUT /api/v2.1/external-apps/{app_token}/status/`

> 🚧 Breaking changes
>
> None

> 👍 Other changes
>
> - Deprecated base export calls for sytem admins were removed from documentation.

## Version 4.1 (23.08.2023)

The SeaTable API Reference for version 4.1 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.1).

> 📘 New requests
>
> - Add user to multiple groups: `POST /api/v2.1/admin/users/{username}/groups/`

> 👍 Other changes
>
> - Add Row and Update Row: unknown single select or multiple-select options will be created
> - Improved data type and structure checks for `/rows/` endpoint
> - `row_id` cannot be changed anymore with Update Row
> - Fixed permission issue with endpoint `/api/v2.1/org/<org_id>/admin/groups/<group_id>/members/`
> - Filter validation for List Rows (with SQL)

> 🚧 Breaking changes
>
> None

## Version 4.0 (27.06.2023)

The SeaTable API Reference for version 4.0 is no longer accessible here. However, you can find it on [Github](https://github.com/seatable/openapi/tree/v4.0).

> 📘 New requests
>
> - Search User by Org-ID: `GET api/v2.1/admin/search-user-by-org-id/`
> - List Plugins Install Count: `GET api/v2.1/admin/plugins-install-count/`
> - List Org-Admin operations logs: `GET api/v2.1/org/{org_id}/admin/admin-logs/`
> - Update Team Logo: `POST api/v2.1/org/{org_id}/admin/org-logo/`
> - Get Team Logo: `GET api/v2.1/org/{org_id}/admin/org-logo/`
> - Delete Team Logo: `DELETE api/v2.1/org/{org_id}/admin/org-logo/`
> - Export Big Data View to Excel: `GET api/v2.1/workspace/{workspace_id}/dtable/{base_name}/convert-big-data-view-to-excel/`
> - Append Excel csv `POST api/v2.1/workspace/{workspace_id}/synchronous-import/append-excel-csv-to-table/`
> - List Universal Apps `GET api/v2.1/universal-apps/`
> - Batch import user to Universal App `POST api/v2.1/universal-apps/{app_token}/app-users/batch/`
> - List Universal App Users `GET api/v2.1/universal-apps/{app_token}/app-users/`
> - List Universal App Invite Links `GET api/v2.1/universal-apps/{app_token}/invite-links/`
> - Move Rows to Big Data `POST /api/v1/dtables/{base_uuid}/archive-view/`
> - Get Folder Content (Custom Folder)
> - Get File Metadata (Custom Folder)
> - Get Upload Link (Custom Folder)
> - Get Download Link (Custom Folder)

> 👍 Other changes
>
> - Added support for bearer authentication

> 🚧 Breaking changes
>
> - Get Base-Token with Invite-Link `GET api/v2.1/dtable/share-link-access-token/` was removed

## Version 3.5 (12.04.2023)

The SeaTable API Reference for version 3.5 is no longer available.

> 🚧 Breaking changes
>
> - Import from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/import-csv/` was replaced with this [new call](/reference/import-base-from-xlsx-or-csv)
> - Append from CSV `POST dtable-server/api/v1/dtables/{base_uuid}/append-csv/` was replaced with this [new call](/reference/import-base-from-xlsx-or-csv)
> - Create Row Comment `POST dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed
> - Update Row Comment `PUT dtable-server/api/v1/dtables/{base_uuid}/comments/` was removed
