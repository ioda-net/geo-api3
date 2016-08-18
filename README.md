# Getting started with geo-api3

Checkout the source code:

    git clone https://github.com/ioda-net/geo-api3.git

The build process relies on a manuelfile. Templates are generated with jinja2-cli.

View the [getting started document in geo-infra](https://github.com/ioda-net/geo-infra/blob/master/docs/getting-started.rst) to start with this project.

To learn more specifically about the api, look at the [api page of the documentation](https://github.com/ioda-net/geo-infra/blob/master/docs/api/index.rst).

You can customize the build in a copy of `config/config.dist.toml`. This copy must be
named `config/config.<branchname>.toml`. This file is written in the
[toml configuration](https://github.com/toml-lang/toml) language. Without this
configuration file, you will not be able to generate the configuration files
from the templates. The keys used in it, will override any values loaded from
`config/config.dist.toml`.


## Credits

- [manuel](https://github.com/ShaneKilkelly/manuel) was created by Shane Kilkelly and is released under the MIT License.
