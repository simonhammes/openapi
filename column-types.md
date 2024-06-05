# Column Types - /dtable-server vs /api-gateway

Note: Everything in this document was tested against v5.0 on stage.seatable.io

## Changes from v4.4 to v5.0
- `getRow` and `listRows` return column IDs **by default** -> `convert_keys` needs to be set to `true` to keep the existing behavior
    - The default value of `convert_keys` should be specified in the API specification
- `getRow` and `listRows` always return `date` columns in ISO format with TZ information (good, but a breaking change to keep in mind!)

## Column Types - `listRowsDeprecated` vs. `listRows`

| Column Type                                        | /dtable-server behavior (`listRowsDeprecated`)   | /api-gateway behavior (`listRows`)                        | Comment                                                                     |
| -------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------- | --------------------------------------------------------------------------- |
| `date` (all formats, accurate to minute = `false`) | ISO, e.g. `2030-06-20`                           | ISO with time + TZ, e.g. `2030-06-20T00:00:00+02:00`      |                                                                             |
| `date` (all formats, accurate to minute = `true` ) | ISO with time, e.g. `2030-06-20 23:55`           | ISO with time + TZ, e.g. `2030-06-20T23:55:00+02:00`      |                                                                             |
| `single-select`                                    | String, e.g. `"option-1"`                        | Integer: `1`                                              |                                                                             |
| `multiple-select`                                  | `array<string>`, e.g. `["option-1", "option-2"]` | Empty array, `[]`                                         |                                                                             |
| `formula` (`dateAdd({date}, 1, 'year')`)           | ISO, e.g. `2031-06-20`                           | ISO with time + TZ, e.g. `2031-06-20T00:00:00+02:00`      | Might already be explained by the different `date` formats                  |
| `formula` (`and(true(), false())`)                 | String, e.g. `"false"`                           | Boolean, e.g. `false`                                     |                                                                             |
| `link-formula` (`countlinks`)                      | String, e.g. `"6"`                               | Integer, e.g. `6`                                         |                                                                             |
| `link-formula` (`findmax/findmin`)                 | String, e.g. `"1.4"`                             | `array<string, int>`, e.g. `[1.4]`                        |                                                                             |
| `link-formula` (`lookup`)                          | String, e.g. `"1.1, 1.2, 1.4"` (CSV)             | `array<string, int>`, e.g. `[1.1, 1.2, 1.4]`              | Mentioned in the API changelog: https://api.seatable.io/reference/changelog |
| `link-formula` (`rollup`, `average/max/...`)       | String, e.g. `"1.25"`                            | Integer/Number, e.g. `1.25`                               |                                                                             |
| `link`                                             | Array of strings (row IDs)                       | Array of objects (Keys: **display_value** and **row_id**) |                                                                             |

### Other Changes
- **listRows** returns `null` for unset column values, while **listRowsDeprecated** omits them
- **listRows** always returns metadata fields such as `_archived`, `_creator`, `_last_modifier`, `_locked`, `_locked_by`
    - This should not be a problem since _extra fields_ are most likely going to be ignored by existing API clients when deserializing a response body

### Commands

```bash
git diff --no-index __snapshots__/test_base_operations/test_listRows\[listRows* --color-words
git diff --no-index __snapshots__/test_base_operations/test_listRows_links\[listRows* --color-words
```
