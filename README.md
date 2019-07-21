
# Home Assistant Our Groceries Sensor

Gets your our groceries lists.

---

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE.md)

![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

## Installation

* Add the `ourgroceries` folder in your `custom_components` folder


## Options

| Name | Type | Requirement | `default` Description
| ---- | ---- | ------- | -----------
| username | string | **Required** | your our groceries username
| password | string | **Required** | your our groceries password


In your `configuration.yaml` file add:

```yaml
ourgroceries:
    username: !secret our_groceries_username
    password: !secret our_groceries_password
```

---

Enjoy my card? Help me out for a couple of :beers: or a :coffee:!

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/JMISm06AD)


[commits-shield]: https://img.shields.io/github/commit-activity/y/ljmerza/ha-our-groceries.svg?style=for-the-badge
[commits]: https://github.com/ljmerza/ha-our-groceries/commits/master
[license-shield]: https://img.shields.io/github/license/ljmerza/ha-our-groceries.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Leonardo%20Merza%20%40ljmerza-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/ljmerza/ha-our-groceries.svg?style=for-the-badge
[releases]: https://github.com/ljmerza/ha-our-groceries/releases

