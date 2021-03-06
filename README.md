# Getting started with geo-api3

## Read-Only project

After serving well its purpose, this project is now considered as deprecated, and this repository is made only read-only
before being deleted on December 31 2020.

If you want to take over the project please contact us : contact (at) ioda-net (dot) ch


## history

Checkout the source code:

    git clone https://github.com/ioda-net/geo-api3.git

View the [getting started](https://docs.geoportal.xyz/getting-started.html) to start with this project. To learn more specifically about the api, look at the [api page of the developer guide](https://docs.geoportal.xyz/dev/api.html). You can also look at [the documentation](https://docs.geoportal.xyz/).

In a nutshell:

- The build process relies on a manuelfile. Templates are generated with jinja2-cli.
- You can customize the build in a copy of `config/config.dist.toml`. This copy must be named `config/config.<branchname>.toml`. This file is written in the [toml configuration](https://github.com/toml-lang/toml) language. Without this configuration file, you will not be able to generate the configuration files from the templates. The keys used in it, will override any values loaded from `config/config.dist.toml`.


# Credits

[manuel](https://github.com/ShaneKilkelly/manuel) is a task runner for Bash and was created by Shane Kilkelly. It is released under the MIT License.

[geo-front3](https://github.com/ioda-net/geo-front3) and [geo-api3](https://github.com/ioda-net/geo-api3) are based on [mf-geoadmin3](https://github.com/geoadmin/mf-geoadmin3) and [mf-chsdi3](https://github.com/geoadmin/mf-chsdi3).
Thoses two softwares were created by [swisstopo](https://www.swisstopo.admin.ch/) the Federal Office of Topography of Switzerland for their geoportal [map.geo.admin.ch](https://map.geo.admin.ch).
They are released under the BSD licence.

[geo-front3](https://github.com/ioda-net/geo-front3) and [geo-api3](https://github.com/ioda-net/geo-api3) were forked and adapted to modernize the geoportals proposed by [sigeom sa](https://www.sigeom.ch/) a Swiss civil engineer, GIS specialist and land surveying company.
The adaptation was performed by [Ioda-Net Sàrl](https://ioda-net.ch/) a Swiss company specialized in Open Source software.

The following companies give financial support, help to keep this software up to date with swisstopo code, and open source:
- [sigeom sa](https://www.sigeom.ch) 2740 Moutier, Switzerland
- [Ioda-Net Sàrl](https://ioda-net.ch/) CH-2947 Charmoille, Switzerland

Want to help too? [contact (at) geoportal (dot) xyz](mailto:contact(at)geoportal.xyz)
