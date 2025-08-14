import pytest
from ncdgen.aux_discriminators import AUX_DISCRIMINATORS, discriminator_from_name
from ncdgen.aux_discriminators._interface import AuxDiscriminator


@pytest.mark.parametrize(
    "name, expected_type",
    [
        (name, discriminator_type)
        for name, discriminator_type in AUX_DISCRIMINATORS.items()
    ],
)
def test_discriminator_from_name(name: str, expected_type: type[AuxDiscriminator]):
    assert isinstance(discriminator_from_name(name), expected_type)
