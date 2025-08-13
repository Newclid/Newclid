from ncdgen.aux_discriminators._interface import AuxDiscriminator
from ncdgen.aux_discriminators.he_point_deps import AuxFromHEPointsDeps
from ncdgen.aux_discriminators.newclid_traceback import AuxFromNewclidTraceback

AUX_DISCRIMINATORS = {
    "he_point_deps": AuxFromHEPointsDeps,
    "newclid_traceback": AuxFromNewclidTraceback,
}


def discriminator_from_name(name: str) -> AuxDiscriminator:
    discriminator = AUX_DISCRIMINATORS.get(name)
    if discriminator is None:
        raise ValueError(f"Unknown aux discriminator: {name}")
    return discriminator()
