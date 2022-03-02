# tap-amazon-advertising

Author: Drew Banin (drew@fishtownanalytics.com)

This is a [Singer](http://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

It:

- Generates a catalog of available data in the Amazon Advertising API
- Extracts the following resources:
    - Portfolios
    - Sponsored Display Campaigns
    - Sponsored Products Campaigns
    - Sponsored Brands Campaigns
    - AdGroups
    - Biddable Keywords
    - Negative Keywords
    - Campaign Negative Keywords
    - Product Ads

    - Sponsored Display Report: Product Ads
    - Sponsored Display Report: Campaigns
    - Sponsored Display Report: Ad Groups
    - Sponsored Display Report: Targeting
    - Sponsored Display Report: Asins

    - Sponsored Products Report: Product Ads
    - Sponsored Products Report: Campaigns
    - Sponsored Products Report: Ad Groups
    - Sponsored Products Report: Keywords
    - Sponsored Products Report: Targeting
    - Sponsored Products Report: Asins

    - Sponsored Brands Report: Keywords
    - Sponsored Brands Report: Campaigns
    - Sponsored Brands Report: Ad Groups
    - Sponsored Brands Report: Search Term

    - Sponsored Brands Video Report: Keywords
    - Sponsored Brands Video Report: Search Term
    - Sponsored Brands Video Report: Campaigns

### Quick Start

1. Install

```bash
git clone git@github.com:fishtown-analytics/tap-amazon-advertising.git
cd tap-amazon-advertising
pip install .
```

2. Get credentials from Amazon

In addition to a client id and secret, you'll also need to obtain a refresh token for an authorized amazon advertising user. This can be accomplished by
running the `get_refresh_token.py` script located in the root of this repository.

3. Create the config file.

There is a template you can use at `config.json.example`, just copy it to `config.json` in the repo root and insert your credentials.

4. Run the application to generate a catalog.

```bash
tap-amazon-advertising -c config.json --discover > catalog.json
```

5. Select the tables you'd like to replicate

Step 4 a file called `catalog.json` that specifies all the available endpoints and fields. You'll need to open the file and select the ones you'd like to replicate. See the [Singer guide on Catalog Format](https://github.com/singer-io/getting-started/blob/c3de2a10e10164689ddd6f24fee7289184682c1f/BEST_PRACTICES.md#catalog-format) for more information on how tables are selected.

6. Run it!

```bash
tap-amazon-advertising -c config.json --catalog catalog.json
```

Copyright &copy; 2019 Fishtown Analytics
