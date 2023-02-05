# osu! Difficulty Icons Collection
osu! difficulty icons rendered using the difficulty color gradient

# Normal Use
To use this, use the link below and edit it using the instructions

Change:

* [gamemode] to: std, taiko, ctb or mania
  
* [sr] to: star rating rounded to closest decimal (3.21 -> 3.2 or 5.37 -> 5.4)

```
https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/main/rendered/[gamemode]/stars_[sr].png
```

Alternatively for 2x size (32x32)

```
https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/main/rendered/[gamemode]/stars_[sr]@2x.png
```

# Advanced Use
If you want to create difficulty listings less painfully, you can use the BBCode generator (_py/bbcode_gen.py)

#### Things Needed:
* an osu! account - you already know the url if you are here
* python 3.10 or above (latest recommended) - https://www.python.org/downloads/

Firstly, you will need to create a new OAuth2 application at https://osu.ppy.sh/home/account/edit#new-oauth-application

After that, change the values under [API] category inside bbconfig.ini

```ini
# Copy Client ID (Always Visible)
ClientID = client_id_here

# Show Client Secret -> Copy Revealed Client Secret
ClientSecret = client_secret_here
```

You can tweak the other available values inside the configuration file during this time

Now should be able to use the BBCode generator
